from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

import _bootstrap  # noqa: F401
from caoszero.config import Config
from caoszero.executor import execute_plan
from caoszero.journal import Journal
from caoszero.logging_setup import close_logging, configure_logging
from caoszero.planner import PlanOptions, build_plan
from caoszero.reporter import build_csv, build_markdown, write_report
from helpers import make_file


class ReporterTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        base = Path(self.temporary.name)
        self.root = base / "alvo"
        self.root.mkdir()
        self.state = base / "estado"
        self.logger = configure_logging(self.state)
        self.journal = Journal(self.state)

        make_file(self.root, "foto.jpg", b"x" * 100)
        make_file(self.root, "documento.pdf", b"y" * 200)
        plan = build_plan(self.root, Config(), PlanOptions(), self.state)
        self.run = execute_plan(plan, self.journal, self.logger, dry_run=False).run

    def tearDown(self):
        close_logging()
        self.temporary.cleanup()

    def test_markdown_contem_resumo_e_operacoes(self):
        content = build_markdown(self.run)
        self.assertIn("# Relatório CaosZero", content)
        self.assertIn("foto.jpg", content)
        self.assertIn("documento.pdf", content)
        self.assertIn("Resumo", content)
        self.assertIn("Conceitos de Sistemas Operacionais", content)

    def test_csv_tem_cabecalho_e_linhas(self):
        content = build_csv(self.run)
        rows = list(csv.reader(content.splitlines(), delimiter=";"))
        self.assertEqual(rows[0][0], "id_execucao")
        self.assertTrue(any("foto.jpg" in row[2] for row in rows))

    def test_relatorio_md(self):
        path = Path(self.temporary.name) / "relatorio.md"
        written = write_report(self.run, path)
        self.assertEqual(written, path)
        self.assertIn("Relatório CaosZero", path.read_text(encoding="utf-8"))

    def test_relatorio_csv(self):
        path = Path(self.temporary.name) / "relatorio.csv"
        write_report(self.run, path)
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle, delimiter=";"))
        self.assertEqual(rows[0][1], "acao")

    def test_relatorio_json(self):
        path = Path(self.temporary.name) / "relatorio.json"
        write_report(self.run, path)
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["id"], self.run.id)
        self.assertEqual(data["mode"], "execucao")
        self.assertEqual(len(data["operations"]), 2)

    def test_destino_sem_extensao_recebe_md(self):
        path = Path(self.temporary.name) / "saida"
        written = write_report(self.run, path)
        self.assertEqual(written.suffix, ".md")
        self.assertTrue(written.exists())


if __name__ == "__main__":
    unittest.main()
