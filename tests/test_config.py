from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _bootstrap  # noqa: F401
from caoszero.config import (
    Config,
    config_from_dict,
    default_state_dir,
    init_config,
    load_config,
)
from caoszero.errors import ConfigError


class ConfigTests(unittest.TestCase):
    def test_categoria_por_extensao(self):
        config = Config()
        self.assertEqual(config.category_for("foto.JPG"), "Imagens")
        self.assertEqual(config.category_for("relatorio.pdf"), "Documentos")
        self.assertEqual(config.category_for("planilha.csv"), "Planilhas")
        self.assertEqual(config.category_for("programa.py"), "Codigo")

    def test_extensao_composta_tem_prioridade(self):
        config = Config()
        self.assertEqual(config.category_for("backup.tar.gz"), "Compactados")
        self.assertEqual(config.category_for("arquivo.tar"), "Compactados")

    def test_extensao_desconhecida_vai_para_outros(self):
        config = Config()
        self.assertEqual(config.category_for("arquivo.xyz"), "Outros")
        self.assertEqual(config.category_for("sem_extensao"), "Outros")

    def test_carrega_json_personalizado(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "categories": {"Fotos": ["jpg", "png"]},
                        "ignore_names": ["segredo.txt"],
                        "archive_dir": "Velhos",
                        "min_free_mb": 10,
                    }
                ),
                encoding="utf-8",
            )
            config = load_config(path)
            self.assertEqual(config.category_for("a.jpg"), "Fotos")
            self.assertEqual(config.ignore_names, ["segredo.txt"])
            self.assertEqual(config.archive_dir, "Velhos")
            self.assertEqual(config.min_free_mb, 10)

    def test_json_invalido_gera_erro_amigavel(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config.json"
            path.write_text("{invalido", encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(path)

    def test_configuracao_inexistente_explicita_gera_erro(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(ConfigError):
                load_config(Path(temporary) / "nao-existe.json")

    def test_validacao_de_campos(self):
        with self.assertRaises(ConfigError):
            config_from_dict({"categories": []})
        with self.assertRaises(ConfigError):
            config_from_dict({"min_free_mb": -1})
        with self.assertRaises(ConfigError):
            config_from_dict({"ignore_names": "nao-e-lista"})

    def test_normaliza_extensoes_sem_ponto(self):
        config = config_from_dict({"categories": {"Fotos": ["JPG"]}})
        self.assertEqual(config.categories["Fotos"], [".jpg"])

    def test_state_dir_respeita_variavel_de_ambiente(self):
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.dict(os.environ, {"CAOSZERO_HOME": temporary}):
                self.assertEqual(default_state_dir(), Path(temporary).resolve())

    def test_init_config_nao_sobrescreve_sem_force(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config.json"
            init_config(path)
            with self.assertRaises(ConfigError):
                init_config(path)
            init_config(path, force=True)
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
