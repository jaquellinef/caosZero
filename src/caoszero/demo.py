"""Criação do ambiente de demonstração com arquivos simulados."""

from __future__ import annotations

import os
import time
from pathlib import Path

_SAMPLES: dict[str, bytes] = {
    "relatorio_final.pdf": b"%PDF-1.4\n% CaosZero: relatorio de exemplo\n",
    "planilha_orcamento.xlsx": b"PK\x03\x04 planilha de exemplo",
    "foto_ferias.jpg": b"\xff\xd8\xff\xe0 imagem de exemplo",
    "captura_tela.png": b"\x89PNG\r\n\x1a\n imagem de exemplo",
    "video_aula.mp4": b"\x00\x00\x00\x18ftypmp42 video de exemplo",
    "musica_favorita.mp3": b"ID3 musica de exemplo",
    "backup_projeto.zip": b"PK\x03\x04 backup de exemplo",
    "instalador_app.exe": b"MZ instalador de exemplo",
    "script_automacao.py": b"print('exemplo')\n",
    "notas.txt": "Anotações do projeto CaosZero.\n".encode("utf-8"),
    "dados.csv": b"nome,tamanho\nfoto.jpg,2048\n",
    "arquivo_sem_extensao": b"sem extensao",
    "IMG_001.jpg": b"\xff\xd8\xff\xe0 foto para renomear",
    "IMG_002.jpg": b"\xff\xd8\xff\xe0 outra foto para renomear",
    "documento_antigo.pdf": b"%PDF-1.4\n% documento antigo\n",
    ".arquivo_oculto.txt": b"arquivo oculto de exemplo",
}

_NESTED: dict[str, bytes] = {
    "projetos/anotacoes.md": b"# Anotacoes\n",
    "projetos/codigo.py": b"print('projeto')\n",
    "projetos/rascunho.tmp": b"temporario\n",
}


def criar_sandbox(destination: Path | str = "sandbox_teste") -> Path:
    """Cria uma pasta com arquivos variados para demonstração e testes manuais."""
    root = Path(destination).expanduser()
    root.mkdir(parents=True, exist_ok=True)

    for name, content in _SAMPLES.items():
        path = root / name
        path.write_bytes(content)

    for relative, content in _NESTED.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    # Pasta de categoria já existente, usada para demonstrar colisão de nomes.
    collision_dir = root / "Imagens"
    collision_dir.mkdir(exist_ok=True)
    (collision_dir / "foto_ferias.jpg").write_bytes(b"\xff\xd8\xff\xe0 copia existente")

    # Dois arquivos antigos (400 dias) para demonstrar --archive-old.
    old_timestamp = time.time() - 400 * 86400
    for name in ("documento_antigo.pdf", "backup_projeto.zip"):
        os.utime(root / name, (old_timestamp, old_timestamp))

    return root
