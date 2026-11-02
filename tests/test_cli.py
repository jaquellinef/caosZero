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


class CliTests(unittest.TestCase):
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

    def tearDown(self):
        self.env.stop()
        self.temporary.cleanup()

    def run_cli(self, arguments):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(arguments)
        return code, output.getvalue()

    def test_demo_cria_arquivos(self):
        code, output = self.run_cli(["demo", str(self.sandbox)])
        self.assertEqual(code, 0)
        self.assertIn("Ambiente de demonstração", output)
        self.assertTrue((self.sandbox / "foto_ferias.jpg").exists())
        self.assertTrue((self.sandbox / "IMG_001.jpg").exists())

    def test_organize_simula_por_padrao(self):
        self.run_cli(["demo", str(self.sandbox)])
        code, output = self.run_cli(["organize", str(self.sandbox)])
        self.assertEqual(code, 0)
        self.assertIn("SIMULAÇÃO", output)
        self.assertTrue((self.sandbox / "foto_ferias.jpg").exists())
        self.assertFalse((self.sandbox / "Imagens" / "foto_ferias (1).jpg").exists())

    def test_organize_aplica_e_gera_relatorio(self):
        self.run_cli(["demo", str(self.sandbox)])
        report = self.base / "relatorio.md"
        code, output = self.run_cli(
            [
                "organize",
                str(self.sandbox),
                "--apply",
                "--yes",
                "--report",
                str(report),
            ]
        )
        self.assertEqual(code, 0, output)
        self.assertIn("Execução", output)
        self.assertTrue(report.exists())
        self.assertTrue((self.sandbox / "Documentos" / "relatorio_final.pdf").exists())
        self.assertTrue((self.sandbox / "Imagens" / "foto_ferias (1).jpg").exists())
        self.assertIn("Relatório CaosZero", report.read_text(encoding="utf-8"))

    def test_undo_restaura(self):
        self.run_cli(["demo", str(self.sandbox)])
        self.run_cli(["organize", str(self.sandbox), "--apply", "--yes"])
        self.assertFalse((self.sandbox / "foto_ferias.jpg").exists())

        code, output = self.run_cli(["undo", "--latest", "--yes"])
        self.assertEqual(code, 0, output)
        self.assertIn("Undo concluído", output)
        self.assertTrue((self.sandbox / "foto_ferias.jpg").exists())

    def test_undo_list(self):
        self.run_cli(["demo", str(self.sandbox)])
        self.run_cli(["organize", str(self.sandbox), "--apply", "--yes"])
        code, output = self.run_cli(["undo", "--list"])
        self.assertEqual(code, 0)
        self.assertIn("INÍCIO", output)

    def test_doctor_json(self):
        code, output = self.run_cli(["doctor", "--json"])
        self.assertEqual(code, 0)
        data = json.loads(output)
        self.assertIn("sistema", data)
        self.assertIn("memoria", data)

    def test_config_show(self):
        code, output = self.run_cli(["config", "--show"])
        self.assertEqual(code, 0)
        self.assertIn("categories", output)
        self.assertIn("Imagens", output)

    def test_config_init(self):
        destination = self.base / "config.json"
        code, output = self.run_cli(["config", "--init", str(destination)])
        self.assertEqual(code, 0)
        self.assertTrue(destination.exists())
        self.assertIn("Configuração criada", output)

    def test_alvo_inexistente_retorna_erro(self):
        code, _ = self.run_cli(["organize", str(self.base / "nao-existe")])
        self.assertEqual(code, 1)

    def test_json_saida_em_simulacao(self):
        self.run_cli(["demo", str(self.sandbox)])
        code, output = self.run_cli(["organize", str(self.sandbox), "--json"])
        self.assertEqual(code, 0)
        data = json.loads(output)
        self.assertEqual(data["mode"], "simulacao")
        self.assertGreater(len(data["operations"]), 0)

    def test_filtro_por_padrao(self):
        self.run_cli(["demo", str(self.sandbox)])
        code, output = self.run_cli(
            ["organize", str(self.sandbox), "--pattern", "*.pdf", "--json"]
        )
        self.assertEqual(code, 0)
        data = json.loads(output)
        self.assertTrue(all(op["source"].endswith(".pdf") for op in data["operations"]))


if __name__ == "__main__":
    unittest.main()
