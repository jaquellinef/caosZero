from __future__ import annotations

import unittest
from pathlib import Path

import _bootstrap  # noqa: F401
from caoszero.system_info import collect_system_info, render_text


class SystemInfoTests(unittest.TestCase):
    def test_coleta_estrutura_esperada(self):
        info = collect_system_info(Path.cwd())
        for key in ("sistema", "processo", "cpu", "memoria", "disco", "alvo", "ambiente"):
            self.assertIn(key, info)
        self.assertGreater(info["cpu"]["nucleos"], 0)
        self.assertGreater(info["disco"]["total"], 0)
        self.assertGreater(info["processo"]["pid"], 0)
        self.assertIn("python", info["sistema"])
        self.assertIn("permissoes", info["alvo"])

    def test_render_texto(self):
        info = collect_system_info(Path.cwd())
        text = render_text(info)
        self.assertIn("CaosZero — Diagnóstico do Sistema", text)
        self.assertIn("PID", text)
        self.assertIn("Memória total", text)
        self.assertIn("Disco", text.replace("Armazenamento", "Disco"))

    def test_alvo_inexistente_nao_quebra(self):
        info = collect_system_info(Path("caminho/que/nao/existe"))
        self.assertFalse(info["alvo"]["existe"])
        self.assertIn("disco", info)


if __name__ == "__main__":
    unittest.main()
