# Guia de contribuição

Obrigado por contribuir com o CaosZero. Este documento descreve o fluxo de
trabalho adotado pelo projeto.

## Código de conduta e segurança

- Todas as interações seguem o [Código de Conduta](CODE_OF_CONDUCT.md).
- Vulnerabilidades **não** devem ser relatadas em issues públicas. Siga a
  [Política de Segurança](SECURITY.md) e use o canal privado.
- Nunca commite credenciais, tokens, arquivos `.env` ou dados pessoais.
- Mudanças que envolvam movimentação de arquivos devem preservar as garantias
  de simulação, não sobrescrita e undo.

## Pré-requisitos

- Python 3.10+
- Git
- Conta no GitHub com acesso ao repositório

## Configuração inicial

```bash
git clone https://github.com/julianasaunders/caosZero.git
cd caosZero
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .\.venv\Scripts\Activate.ps1  # Windows
python -m pip install -e .
```

Instale os hooks locais:

```bash
./scripts/instalar_hooks.sh        # Linux/macOS
.\scripts\instalar_hooks.ps1       # Windows
```

## Modelo de branches

O projeto usa uma adaptação enxuta do **GitFlow**:

| Branch | Papel | Origem | Destino |
| --- | --- | --- | --- |
| `main` | Código estável e releases | — | — |
| `develop` | Integração contínua | `main` | `main` (release) |
| `feat/<n>-slug` | Nova funcionalidade | `develop` | `develop` |
| `fix/<n>-slug` | Correção | `develop` | `develop` |
| `docs/<n>-slug` | Documentação | `develop` | `develop` |
| `test/<n>-slug` | Testes | `develop` | `develop` |
| `chore/<n>-slug` | Infraestrutura | `develop` | `develop` |
| `release/<versão>` | Preparação de release | `develop` | `main` |

Regras:

- O `<n>` é o número da issue.
- O `slug` é curto e descritivo, em minúsculas e com hífens.
- Branches de feature partem sempre de `develop`.
- Nunca faça commit direto em `main` ou `develop`.
- Apague a branch após o merge.

Exemplos:

```text
feat/3-planejador
feat/4-executor-undo
docs/11-documentacao
test/10-integracao
release/v2.0.0
```

## Commits

Seguimos o padrão **Conventional Commits**:

```text
<tipo>(<escopo>): <descrição no imperativo>

[corpo opcional]

[rodapé opcional]
```

Tipos aceitos:

| Tipo | Uso |
| --- | --- |
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `refactor` | Refatoração sem mudança de comportamento |
| `docs` | Documentação |
| `test` | Testes |
| `perf` | Melhoria de desempenho |
| `chore` | Build, CI, ferramentas |
| `ci` | Configuração de integração contínua |

Exemplos:

```text
feat(planner): adiciona filtro por tamanho mínimo
fix(executor): evita sobrescrever destino existente
docs(readme): reescreve instruções de instalação
test(integracao): cobre fluxo completo de undo
```

Boas práticas:

- Uma mudança lógica por commit.
- Descrição no imperativo: “adiciona”, não “adicionado”.
- Referencie a issue no corpo ou no rodapé (`Refs #3`, `Closes #3`).
- Trabalhos conjuntos usam `Co-authored-by:`.

## Pull requests

Antes de abrir:

- [ ] A branch parte de `develop` e tem o número da issue.
- [ ] Os testes passam localmente.
- [ ] O código segue o estilo do projeto.
- [ ] A documentação foi atualizada, se necessário.
- [ ] Não há arquivos temporários ou segredos.
- [ ] O título segue Conventional Commits.

O corpo do PR deve conter:

```markdown
## O que muda
Descrição objetiva.

## Por quê
Contexto e motivação.

## Como testar
Passos para reproduzir.

## Checklist
- [ ] Testes
- [ ] Documentação
- [ ] Sem breaking change

Closes #N
```

O merge é feito em `develop` com **merge commit**, preservando o histórico das
branches. A release é mesclada em `main` e depois `main` é sincronizada de volta
em `develop`.

## Revisão de código

Quem revisa verifica:

- Correção e clareza da lógica.
- Cobertura de testes para o comportamento novo.
- Consistência com a arquitetura (planejador não altera arquivos).
- Mensagens de erro em português e acionáveis.
- Impacto em segurança (sobrescrita, links simbólicos, permissões).
- Atualização de README/docs quando o comportamento muda.

## Hooks

Os hooks ficam em `scripts/githooks/` e são copiados para `.git/hooks/` pelos
instaladores.

| Hook | Verificação |
| --- | --- |
| `pre-commit` | Compilação dos módulos e testes rápidos |
| `pre-push` | Suíte completa de testes |

Para pular temporariamente (use com cautela):

```bash
git commit --no-verify
git push --no-verify
```

## Proteção de branch

A branch `main` deve ter:

- Pull request obrigatório.
- Pelo menos uma revisão aprovada.
- CI verde antes do merge.
- Force push desabilitado.
- Exclusão desabilitada.

## Estilo de código

- Python 3.10+, com `from __future__ import annotations`.
- Tipos explícitos em funções públicas.
- Docstrings em português.
- Nomes de domínio em português (`Plano`, `Operacao` quando aplicável).
- Sem dependências externas obrigatórias.
- Formatação compatível com `python -m compileall`.

## Testes

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

Novos comportamentos exigem novos testes. Use `TemporaryDirectory` e nunca
dependa de arquivos do usuário.

## Documentação

- README: visão geral e primeiros passos.
- `docs/`: planejamento, arquitetura, conceitos, guia, testes e apresentação.
- Wiki: material de apoio e perguntas frequentes.
- CHANGELOG: mudanças relevantes por versão.

## Dúvidas

Abra uma issue com a label `question` ou procure a equipe:

- [@julianasaunders](https://github.com/julianasaunders)
- [@jaquellinef](https://github.com/jaquellinef)
