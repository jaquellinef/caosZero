from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import _bootstrap  # noqa: F401
from caoszero.config import Config
from caoszero.executor import execute_plan, undo_run
from caoszero.journal import Journal
from caoszero.logging_setup import close_logging, configure_logging
from caoszero.models import Status
from caoszero.planner import PlanOptions, build_plan
from helpers import make_file


class ExecutorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        base = Path(self.temporary.name)
        self.root = base / "alvo"
        self.root.mkdir()
        self.state = base / "estado"
        self.journal = Journal(self.state)
        self.logger = configure_logging(self.state)

    def tearDown(self):
        close_logging()
        self.temporary.cleanup()

    def build(self, options=None):
        return build_plan(self.root, Config(), options or PlanOptions(), self.state)

    def test_simulacao_nao_move_e_nao_grava_journal(self):
        make_file(self.root, "foto.jpg")
        plan = self.build()
        result = execute_plan(plan, self.journal, self.logger, dry_run=True)

        self.assertTrue((self.root / "foto.jpg").exists())
        self.assertEqual(result.moved, 0)
        self.assertEqual(self.journal.list_runs(), [])

    def test_execucao_move_e_registra(self):
        make_file(self.root, "foto.jpg")
        make_file(self.root, "documento.pdf")
        plan = self.build()
        result = execute_plan(plan, self.journal, self.logger, dry_run=False)

        self.assertEqual(result.moved, 2)
        self.assertEqual(result.failed, 0)
        self.assertTrue((self.root / "Imagens" / "foto.jpg").exists())
        self.assertTrue((self.root / "Documentos" / "documento.pdf").exists())

        saved = self.journal.load(result.run.id)
        self.assertEqual(saved.counts()["concluidas"], 2)
        self.assertTrue(all(op.status == Status.DONE for op in saved.operations))

    def test_undo_restaura_arquivos(self):
        make_file(self.root, "foto.jpg")
        make_file(self.root, "documento.pdf")
        plan = self.build()
        result = execute_plan(plan, self.journal, self.logger, dry_run=False)

        undo = undo_run(result.run, self.journal, self.logger, dry_run=False)
        self.assertEqual(undo.undone, 2)
        self.assertEqual(undo.undo_failed, 0)
        self.assertTrue((self.root / "foto.jpg").exists())
        self.assertTrue((self.root / "documento.pdf").exists())

        saved = self.journal.load(result.run.id)
        self.assertTrue(all(op.status == Status.UNDONE for op in saved.operations))

    def test_undo_simulado_nao_altera_nada(self):
        make_file(self.root, "foto.jpg")
        result = execute_plan(self.build(), self.journal, self.logger, dry_run=False)
        undo = undo_run(result.run, self.journal, self.logger, dry_run=True)

        self.assertEqual(undo.undone, 1)
        self.assertTrue((self.root / "Imagens" / "foto.jpg").exists())
        self.assertTrue(all(op.status == Status.DONE for op in result.run.operations))

    def test_falha_quando_origem_desaparece(self):
        source = make_file(self.root, "foto.jpg")
        plan = self.build()
        source.unlink()

        result = execute_plan(plan, self.journal, self.logger, dry_run=False)
        self.assertEqual(result.moved, 0)
        self.assertEqual(result.failed, 1)
        self.assertEqual(result.run.operations[0].status, Status.FAILED)
        self.assertIn("origem", result.run.operations[0].error or "")

    def test_undo_falha_quando_destino_sumiu(self):
        make_file(self.root, "foto.jpg")
        result = execute_plan(self.build(), self.journal, self.logger, dry_run=False)
        destination = result.run.operations[0].destination
        destination.unlink()

        undo = undo_run(result.run, self.journal, self.logger, dry_run=False)
        self.assertEqual(undo.undone, 0)
        self.assertEqual(undo.undo_failed, 1)
        self.assertEqual(result.run.operations[0].status, Status.UNDO_FAILED)

    def test_colisao_no_momento_da_execucao(self):
        make_file(self.root, "foto.jpg")
        plan = self.build()
        # Simula um arquivo criado por outro processo após o planejamento.
        collision = self.root / "Imagens" / "foto.jpg"
        collision.parent.mkdir(parents=True, exist_ok=True)
        collision.write_bytes(b"outro")

        result = execute_plan(plan, self.journal, self.logger, dry_run=False)
        self.assertEqual(result.moved, 1)
        self.assertTrue((self.root / "Imagens" / "foto (1).jpg").exists())
        self.assertEqual(collision.read_bytes(), b"outro")

    def test_latest_retorna_execucao_com_operacoes(self):
        make_file(self.root, "a.txt")
        result = execute_plan(self.build(), self.journal, self.logger, dry_run=False)
        latest = self.journal.latest()
        self.assertIsNotNone(latest)
        self.assertEqual(latest.id, result.run.id)

    def test_undo_de_simulacao_e_recusado(self):
        make_file(self.root, "a.txt")
        plan = self.build()
        simulation = execute_plan(plan, self.journal, self.logger, dry_run=True)
        with self.assertRaises(ValueError):
            undo_run(simulation.run, self.journal, self.logger)


if __name__ == "__main__":
    unittest.main()
