# Arquitetura

## Fluxo

```text
CLI → Planejador → Plano → Executor → Journal → Undo
                        └→ Relatórios
```

## Módulos

| Módulo | Papel |
| --- | --- |
| `cli.py` | Argumentos, confirmação e códigos de saída |
| `config.py` | Configuração JSON e diretórios padrão |
| `planner.py` | Planejamento sem efeitos colaterais |
| `executor.py` | Execução e undo |
| `journal.py` | Persistência das execuções |
| `reporter.py` | Relatórios MD/CSV/JSON |
| `system_info.py` | Diagnóstico do SO |
| `models.py` | Modelos de domínio |
| `utils.py` | Utilitários |
| `demo.py` | Sandbox de demonstração |

## Princípios

1. **Planejar antes de agir.** O planejador nunca altera arquivos.
2. **Uma camada com permissão de escrita.** Apenas o executor move arquivos.
3. **Registrar antes e depois.** O journal é salvo a cada operação.
4. **Nunca sobrescrever.** Colisões geram nomes únicos.
5. **Ignorar links simbólicos.** Segurança contra ciclos e escapes.
6. **Recusar a raiz do sistema.** Evita danos irreversíveis.

## Journal

Cada execução gera `<estado>/runs/<id>.json` com:

- ID, início, fim, alvo e modo;
- operações com origem, destino, tamanho e status;
- arquivos ignorados e motivos;
- avisos.

## Diagrama detalhado

Consulte
[ARQUITETURA.md](https://github.com/julianasaunders/caosZero/blob/main/docs/ARQUITETURA.md).

Voltar para [Home](Home).
