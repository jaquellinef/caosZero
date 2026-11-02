"""Testes de integração do fluxo completo do CaosZero.

Diferente dos testes unitários, aqui as camadas são exercitadas juntas sobre um
sistema de arquivos real e temporário: planejamento, execução, journal,
relatórios e undo.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _bootstrap  # noqa: F401
from caoszero.cli import main
from caoszero.config import Config
from caoszero.demo import criar_sandbox
from caoszero.executor import execute_plan, undo_run
from caoszero.journal import Journal
from caoszero.models import Status
from caoszero.planner import PlanOptions, build_plan
from caoszero.reporter import write_report
from helpers import make_file


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.state = self.base / "estado"
        self.sandbox = self.base / "sandbox"
        self.env = mock.patch.dict(
            os.environ,
            {"CAOSZERO_HOME": str(self.state)},
            clear=False,
        )
        self.env.start()
        self.logger = __import__("logging").getLogger("caoszero.integration")
        self.logger.addHandler(__import__("logging").NullHandler())

    def tearDown(self):
        self.env.stop()
        self.temporary.cleanup()

    # ------------------------------------------------------------------
    # Auxiliares
    # ------------------------------------------------------------------
    def run_cli(self, arguments):
        output = io.StringIO()
        errors = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = main(arguments)
        return code, output.getvalue(), errors.getvalue()

    def plan(self, options=None, config=None):
        return build_plan(
            self.sandbox,
            config=config or Config(),
            options=options or PlanOptions(),
            state_dir=self.state,
        )

    # ------------------------------------------------------------------
    # Fluxo completo
    # ------------------------------------------------------------------
    def test_fluxo_completo_demo_organiza_relata_e_desfaz(self):
        criar_sandbox(self.sandbox)
        plan = self.plan()
        self.assertGreater(len(plan.operations), 0)

        journal = Journal(self.state)
        result = execute_plan(plan, journal, self.logger, dry_run=False)
        self.assertEqual(result.failed, 0)
        self.assertEqual(result.moved, len(plan.operations))
        self.assertTrue((self.sandbox / "Imagens" / "foto_ferias (1).jpg").exists())

        report = write_report(result.run, self.state / "reports" / "integracao.md")
        content = report.read_text(encoding="utf-8")
        self.assertIn("# Relatório CaosZero", content)
        self.assertIn("Execução real", content)

        undo = undo_run(result.run, journal, self.logger)
        self.assertEqual(undo.undo_failed, 0)
        self.assertEqual(undo.undone, result.moved)
        self.assertTrue((self.sandbox / "foto_ferias.jpg").exists())

    def test_simulacao_nao_cria_journal_nem_altera_arquivos(self):
        criar_sandbox(self.sandbox)
        before = sorted(path.name for path in self.sandbox.iterdir())
        plan = self.plan()

        result = execute_plan(plan, Journal(self.state), self.logger, dry_run=True)

        self.assertTrue(result.run.dry_run)
        self.assertEqual(sorted(path.name for path in self.sandbox.iterdir()), before)
        self.assertEqual(Journal(self.state).list_runs(), [])

    # ------------------------------------------------------------------
    # Filtros e recursão
    # ------------------------------------------------------------------
    def test_recursivo_com_arquivamento_de_antigos(self):
        make_file(self.sandbox, "antigo.pdf", days_old=400)
        make_file(self.sandbox, "recente.pdf")
        make_file(self.sandbox, "sub/profundo.png")

        plan = self.plan(
            PlanOptions(recursive=True, archive_old_days=365),
        )
        destinations = {operation.source.name: operation.destination for operation in plan.operations}

        self.assertIn("Arquivo", destinations["antigo.pdf"].parts)
        self.assertEqual(
            destinations["recente.pdf"].parent.resolve(),
            (self.sandbox / "Documentos").resolve(),
        )
        self.assertEqual(
            destinations["profundo.png"].parent.resolve(),
            (self.sandbox / "Imagens").resolve(),
        )

    def test_filtro_por_idade_e_tamanho(self):
        make_file(self.sandbox, "velho_grande.bin", content=b"x" * 4096, days_old=60)
        make_file(self.sandbox, "novo_grande.bin", content=b"x" * 4096)
        make_file(self.sandbox, "velho_pequeno.bin", content=b"x", days_old=60)

        plan = self.plan(PlanOptions(older_than=30, min_size=1024))
        names = [operation.source.name for operation in plan.operations]

        self.assertEqual(names, ["velho_grande.bin"])

    # ------------------------------------------------------------------
    # Renomeação e colisões
    # ------------------------------------------------------------------
    def test_renomeacao_em_massa_com_colisao(self):
        make_file(self.sandbox, "foto_a.jpg")
        make_file(self.sandbox, "foto_b.jpg")
        make_file(self.sandbox, "foto_c.jpg")

        plan = self.plan(
            PlanOptions(rename_pattern="IMG-{seq:03d}{ext}", rename_only=True),
        )
        destinations = sorted(operation.destination.name for operation in plan.operations)

        self.assertEqual(destinations, ["IMG-001.jpg", "IMG-002.jpg", "IMG-003.jpg"])

    def test_colisao_com_arquivo_existente_gera_sufixo(self):
        make_file(self.sandbox, "relatorio.pdf")
        make_file(self.sandbox, "Documentos/relatorio.pdf")

        plan = self.plan()
        destination = plan.operations[0].destination

        self.assertEqual(destination.name, "relatorio (1).pdf")

    # ------------------------------------------------------------------
    # Journal, falhas parciais e configuração
    # ------------------------------------------------------------------
    def test_falha_parcial_preserva_operacoes_concluidas(self):
        primeiro = make_file(self.sandbox, "a.pdf")
        make_file(self.sandbox, "b.pdf")
        plan = self.plan()

        primeiro.unlink()  # simula arquivo removido entre planejamento e execução

        result = execute_plan(plan, Journal(self.state), self.logger, dry_run=False)

        self.assertEqual(result.failed, 1)
        self.assertEqual(result.moved, 1)
        self.assertTrue((self.sandbox / "Documentos" / "b.pdf").exists())
        self.assertTrue(any(op.status == Status.FAILED for op in result.run.operations))

    def test_journal_lista_e_recupera_execucao(self):
        criar_sandbox(self.sandbox)
        journal = Journal(self.state)
        result = execute_plan(self.plan(), journal, self.logger, dry_run=False)

        runs = journal.list_runs()
        self.assertEqual(len(runs), 1)
        loaded = journal.load(result.run.id)
        self.assertEqual(loaded.id, result.run.id)
        self.assertEqual(len(loaded.operations), len(result.run.operations))

    def test_cli_respeita_caoszero_target(self):
        criar_sandbox(self.sandbox)
        with mock.patch.dict(os.environ, {"CAOSZERO_TARGET": str(self.sandbox)}):
            code, output, _ = self.run_cli(["organize", "--json"])

        self.assertEqual(code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["mode"], "simulacao")
        self.assertTrue(payload["operations"])

    def test_relatorios_nos_tres_formatos(self):
        criar_sandbox(self.sandbox)
        plan = self.plan()
        result = execute_plan(plan, Journal(self.state), self.logger, dry_run=False)

        markdown = write_report(result.run, self.base / "relatorio.md")
        csv_path = write_report(result.run, self.base / "relatorio.csv")
        json_path = write_report(result.run, self.base / "relatorio.json")

        self.assertIn("| Indicador | Valor |", markdown.read_text(encoding="utf-8"))
        self.assertIn("id_execucao;acao", csv_path.read_text(encoding="utf-8-sig"))
        data = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(data["id"], result.run.id)
        self.assertIn("operations", data)

    def test_undo_nao_sobrescreve_origem_ocupada(self):
        make_file(self.sandbox, "documento.pdf")
        plan = self.plan()
        journal = Journal(self.state)
        result = execute_plan(plan, journal, self.logger, dry_run=False)

        # Recria manualmente a origem para forçar conflito no undo.
        make_file(self.sandbox, "documento.pdf", content=b"novo arquivo")

        undo = undo_run(result.run, journal, self.logger)

        self.assertEqual(undo.undone, 0)
        self.assertEqual(undo.undo_failed, 1)
        self.assertTrue((self.sandbox / "Documentos" / "documento.pdf").exists())
        self.assertEqual(
            (self.sandbox / "documento.pdf").read_bytes(),
            b"novo arquivo",
        )

    def test_configuracao_personalizada_altera_categoria(self):
        make_file(self.sandbox, "dados.xyz")
        config = Config(categories={"Especiais": [".xyz"], "Outros": []})

        plan = self.plan(config=config)

        self.assertEqual(plan.operations[0].destination.parent.name, "Especiais")


if __name__ == "__main__":
    unittest.main()
