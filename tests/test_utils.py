from __future__ import annotations

import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import _bootstrap  # noqa: F401
from caoszero.utils import (
    human_size,
    is_hidden,
    matches_any,
    parse_size,
    relative_label,
    render_pattern,
    sanitize_filename,
    unique_destination,
)


class UtilsTests(unittest.TestCase):
    def test_human_size(self):
        self.assertEqual(human_size(0), "0 B")
        self.assertEqual(human_size(512), "512 B")
        self.assertEqual(human_size(1024), "1.0 KB")
        self.assertEqual(human_size(1536), "1.5 KB")
        self.assertEqual(human_size(1024 * 1024), "1.0 MB")

    def test_parse_size(self):
        self.assertEqual(parse_size("1024"), 1024)
        self.assertEqual(parse_size("1 KB"), 1024)
        self.assertEqual(parse_size("10MB"), 10 * 1024 * 1024)
        self.assertEqual(parse_size("1,5GB"), int(1.5 * 1024**3))
        with self.assertRaises(ValueError):
            parse_size("muito grande")

    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename('a<b>c:d"e/f\\g|h?i*j'), "a-b-c-d-e-f-g-h-i-j")
        self.assertEqual(sanitize_filename("   "), "arquivo")
        self.assertEqual(sanitize_filename("CON"), "_CON")

    def test_unique_destination(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = root / "foto.jpg"
            original.write_bytes(b"x")
            alternative = unique_destination(original)
            self.assertEqual(alternative.name, "foto (1).jpg")
            alternative.write_bytes(b"y")
            self.assertEqual(unique_destination(original).name, "foto (2).jpg")

    def test_unique_destination_com_extensao_composta(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = root / "backup.tar.gz"
            original.write_bytes(b"x")
            self.assertEqual(unique_destination(original).name, "backup (1).tar.gz")

    def test_matches_any(self):
        self.assertTrue(matches_any("Arquivo.TMP", ["*.tmp"]))
        self.assertFalse(matches_any("arquivo.txt", ["*.tmp"]))

    def test_render_pattern(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "IMG_001.jpg"
            path.write_bytes(b"x")
            fixed = datetime(2026, 1, 2, 12, 0, 0).timestamp()
            os.utime(path, (fixed, fixed))
            self.assertEqual(
                render_pattern("ferias-{seq:03d}{ext}", path, 1, "Imagens"),
                "ferias-001.jpg",
            )
            self.assertEqual(
                render_pattern("foto-{date}{ext}", path, 1, "Imagens"),
                "foto-2026-01-02.jpg",
            )
            self.assertEqual(
                render_pattern("{name}-editado", path, 1, "Imagens"),
                "IMG_001-editado.jpg",
            )

    def test_relative_label(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(relative_label(root / "a" / "b.txt", root), str(Path("a") / "b.txt"))

    def test_hidden_posix(self):
        with tempfile.TemporaryDirectory() as temporary:
            hidden = Path(temporary) / ".oculto"
            hidden.write_bytes(b"x")
            self.assertTrue(is_hidden(hidden))


if __name__ == "__main__":
    unittest.main()
