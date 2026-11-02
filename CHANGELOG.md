# Changelog

Todas as mudanças relevantes deste projeto são documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o
versionamento segue [SemVer](https://semver.org/lang/pt-BR/).

## [2.0.0] - 2026-11-02

### Adicionado

- CLI `caoszero` com os comandos `organize`, `undo`, `doctor`, `config`,
  `demo` e `interactive`.
- Organização de arquivos por extensão com categorias configuráveis.
- Modo de simulação seguro por padrão; execução real apenas com `--apply`.
- Filtros por padrão glob, idade, tamanho, categoria, subdiretórios e ocultos.
- Renomeação em massa com os tokens `{name}`, `{ext}`, `{seq}`, `{date}` e
  `{categoria}`.
- Arquivamento de arquivos antigos em `Arquivo/AAAA/`.
- Journal em JSON com status por operação.
- Comando `undo` para desfazer a última execução ou uma execução específica.
- Relatórios em Markdown, CSV e JSON.
- Diagnóstico de sistema (`doctor`) com processo, CPU, memória, disco,
  permissões, variáveis de ambiente e limites de cgroup.
- Configuração via JSON, com exemplo em `config/caoszero.example.json`.
- Scripts de automação para Bash e PowerShell.
- Agendamento via `cron` e Agendador de Tarefas do Windows.
- Hooks de `pre-commit` e `pre-push` com instaladores.
- Integração contínua em Ubuntu e Windows, Python 3.10 e 3.12.
- 77 testes automatizados (unitários, ponta a ponta e integração).
- Documentação técnica, wiki e página web no GitHub Pages.

### Segurança

- Recusa da raiz do sistema de arquivos como alvo.
- Links simbólicos ignorados pelo planejador e recusados pelo executor.
- Nenhum arquivo é sobrescrito; colisões geram nomes únicos.
- Verificação de espaço livre antes da execução.
- Confirmação obrigatória em operações reais (exceto com `--yes`).

### Corrigido

- Tratamento de extensões compostas (`.tar.gz` tem prioridade sobre `.gz`).
- Sanitização de nomes reservados do Windows (`CON`, `NUL`, `COM1` etc.).
- Detecção de arquivos ocultos em POSIX e Windows.
- Preservação do diretório de estado durante a varredura recursiva.

## [1.0.0] - 2026-10-20

### Adicionado

- Versão inicial do CaosZero com página web e script de organização.
- Estrutura de pastas por categoria.
- Scripts básicos para Linux/macOS e Windows.

[2.0.0]: https://github.com/julianasaunders/caosZero/releases/tag/v2.0.0
[1.0.0]: https://github.com/julianasaunders/caosZero/releases/tag/v1.0.0
