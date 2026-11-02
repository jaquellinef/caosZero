from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import _bootstrap  # noqa: F401
from caoszero.config import Config
from caoszero.errors import PlanError
from caoszero.models import Action
from caoszero.planner import PlanOptions, build_plan
from helpers import make_file


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "alvo"
        self.root.mkdir()
        self.state = Path(self.temporary.name) / "estado"

    def tearDown(self):
        self.temporary.cleanup()

    def plan(self, options=None):
        return build_plan(self.root, Config(), options or PlanOptions(), self.state)

    def test_organiza_por_categoria_sem_alterar_arquivos(self):
        make_file(self.root, "foto.jpg")
        make_file(self.root, "relatorio.pdf")
        make_file(self.root, "backup.tar.gz")
        make_file(self.root, "sem_extensao")

        plan = self.plan()
        destinations = {op.source.name: op.destination for op in plan.operations}

        self.assertEqual(len(plan.operations), 4)
        self.assertEqual(destinations["foto.jpg"].parent.name, "Imagens")
        self.assertEqual(destinations["relatorio.pdf"].parent.name, "Documentos")
        self.assertEqual(destinations["backup.tar.gz"].parent.name, "Compactados")
        self.assertEqual(destinations["sem_extensao"].parent.name, "Outros")
        self.assertTrue(plan.operations[0].action is Action.MOVE)
        self.assertTrue((self.root / "foto.jpg").exists(), "planejar não deve mover")

    def test_ignora_ocultos_temporarios_e_nomes_conhecidos(self):
        make_file(self.root, ".oculto.txt")
        make_file(self.root, "rascunho.tmp")
        make_file(self.root, "Thumbs.db")
        make_file(self.root, "real.txt")

        plan = self.plan()
        self.assertEqual([op.source.name for op in plan.operations], ["real.txt"])
        reasons = {item.path.name: item.reason for item in plan.skipped}
        self.assertIn("oculto", reasons[".oculto.txt"])
        self.assertIn("temporário", reasons["rascunho.tmp"])

    def test_inclui_ocultos_quando_solicitado(self):
        make_file(self.root, ".oculto.txt")
        plan = self.plan(PlanOptions(include_hidden=True))
        self.assertEqual([op.source.name for op in plan.operations], [".oculto.txt"])

    def test_recursivo_e_ignora_pastas_de_categoria_existentes(self):
        make_file(self.root, "sub/nota.md")
        make_file(self.root, "Imagens/antiga.jpg")
        make_file(self.root, "Arquivo/2025/velho.pdf")

        plan = self.plan(PlanOptions(recursive=True))
        self.assertEqual([op.source.name for op in plan.operations], ["nota.md"])
        self.assertEqual(plan.operations[0].destination.parent.name, "Documentos")

    def test_colisao_gera_nome_unico(self):
        make_file(self.root, "foto.jpg")
        make_file(self.root, "Imagens/foto.jpg")

        plan = self.plan()
        self.assertEqual(plan.operations[0].destination.name, "foto (1).jpg")

    def test_arquiva_antigos(self):
        make_file(self.root, "antigo.pdf", days_old=400)
        make_file(self.root, "novo.pdf")

        plan = self.plan(PlanOptions(archive_old_days=365))
        self.assertEqual(len(plan.operations), 2)
        archived = [op for op in plan.operations if op.action == Action.ARCHIVE]
        self.assertEqual(len(archived), 1)
        operation = archived[0]
        self.assertEqual(operation.destination.parent.parent.name, "Arquivo")
        self.assertIn("antigo", operation.reason)

    def test_arquiva_somente_antigos_com_filtro(self):
        make_file(self.root, "antigo.pdf", days_old=400)
        make_file(self.root, "novo.pdf")

        plan = self.plan(PlanOptions(archive_old_days=365, older_than=365))
        self.assertEqual(len(plan.operations), 1)
        self.assertEqual(plan.operations[0].action, Action.ARCHIVE)

    def test_renomeia_no_lugar(self):
        make_file(self.root, "IMG_001.jpg")
        make_file(self.root, "IMG_002.jpg")

        plan = self.plan(
            PlanOptions(rename_pattern="ferias-{seq:03d}{ext}", rename_only=True)
        )
        names = [op.destination.name for op in plan.operations]
        self.assertEqual(names, ["ferias-001.jpg", "ferias-002.jpg"])
        self.assertTrue(all(op.action is Action.RENAME for op in plan.operations))
        self.assertTrue(all(op.destination.parent == self.root for op in plan.operations))

    def test_filtro_por_padrao(self):
        make_file(self.root, "a.pdf")
        make_file(self.root, "b.jpg")
        plan = self.plan(PlanOptions(pattern="*.pdf"))
        self.assertEqual([op.source.name for op in plan.operations], ["a.pdf"])

    def test_filtro_por_idade(self):
        make_file(self.root, "antigo.pdf", days_old=100)
        make_file(self.root, "novo.pdf")
        plan = self.plan(PlanOptions(older_than=90))
        self.assertEqual([op.source.name for op in plan.operations], ["antigo.pdf"])

    def test_filtro_por_tamanho(self):
        make_file(self.root, "pequeno.txt", b"x" * 10)
        make_file(self.root, "grande.txt", b"x" * 1000)
        plan = self.plan(PlanOptions(min_size=100))
        self.assertEqual([op.source.name for op in plan.operations], ["grande.txt"])

    def test_filtro_por_categoria(self):
        make_file(self.root, "a.pdf")
        make_file(self.root, "b.jpg")
        plan = self.plan(PlanOptions(category="Imagens"))
        self.assertEqual([op.source.name for op in plan.operations], ["b.jpg"])

    def test_estado_dentro_do_alvo_e_ignorado(self):
        self.state = self.root / ".estado"
        make_file(self.state, "journal.json")
        make_file(self.root, "real.txt")
        plan = build_plan(self.root, Config(), PlanOptions(), self.state)
        self.assertEqual([op.source.name for op in plan.operations], ["real.txt"])
        self.assertTrue(any("estado" in warning for warning in plan.warnings))

    def test_recusa_raiz_do_sistema(self):
        with self.assertRaises(PlanError):
            build_plan(Path(Path.cwd().anchor), Config(), PlanOptions(), self.state)

    def test_alvo_inexistente(self):
        with self.assertRaises(PlanError):
            build_plan(self.root / "nao-existe", Config(), PlanOptions(), self.state)

    def test_rename_only_exige_padrao(self):
        with self.assertRaises(PlanError):
            self.plan(PlanOptions(rename_only=True))

    def test_pasta_vazia(self):
        plan = self.plan()
        self.assertEqual(plan.operations, [])


if __name__ == "__main__":
    unittest.main()
