# Primeiros passos

## 1. Criar um sandbox

```bash
python caoszero.py demo
```

Cria `sandbox_teste/` com arquivos variados, inclusive antigos, ocultos e uma
colisão proposital.

## 2. Simular

```bash
python caoszero.py organize sandbox_teste
```

Nada é alterado. A saída mostra:

- arquivos analisados;
- operações planejadas;
- arquivos ignorados e o motivo;
- prévia origem → destino.

## 3. Executar e relatar

```bash
python caoszero.py organize sandbox_teste --apply --report
```

## 4. Desfazer

```bash
python caoszero.py undo --latest
```

## 5. Diagnóstico

```bash
python caoszero.py doctor
```

## Próximos passos

- [Guia de uso completo](https://github.com/julianasaunders/caosZero/blob/main/docs/GUIA-DE-USO.md)
- [Automação](Automacao)
- [Conceitos de SO](Conceitos-de-SO)
