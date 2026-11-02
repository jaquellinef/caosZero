# Política de Segurança

## Objetivo

O CaosZero manipula arquivos do usuário: move, renomeia e arquiva. Por isso,
segurança e reversibilidade são requisitos centrais, não opcionais. Esta
política descreve como relatar vulnerabilidades e quais garantias o projeto
oferece.

## Versões contempladas

| Versão | Suporte |
| --- | --- |
| 2.0.x | Suporte ativo |
| 1.x | Sem suporte |

Como o projeto é acadêmico, não há garantia formal de suporte a aplicações
derivadas. Quem reutilizar o código deve avaliar seus próprios riscos.

## Como relatar uma vulnerabilidade

- **Não** publique senhas, tokens, chaves, dados pessoais ou detalhes
  exploráveis em issues ou pull requests públicos.
- Use a opção **Report a vulnerability** na aba **Security** do repositório,
  quando disponível. Esse é o canal privado preferencial.
- Se essa opção não estiver disponível, entre em contato com as pessoas
  responsáveis por um canal privado do GitHub:
  [@julianasaunders](https://github.com/julianasaunders) e
  [@jaquellinef](https://github.com/jaquellinef).
- Inclua, quando possível:
  - descrição objetiva do problema;
  - impacto potencial;
  - passos seguros para reproduzir;
  - versão do CaosZero, do Python e do sistema operacional;
  - sugestão de correção, se houver.

## O que evitar

- Testar vulnerabilidades contra sistemas ou contas de terceiros sem
  autorização.
- Publicar provas de conceito que exponham dados ou facilitem exploração antes
  de uma correção.
- Enviar credenciais reais. Use exemplos fictícios.
- Executar comandos destrutivos em diretórios reais para demonstrar um problema.
  Use `demo` e um diretório temporário.

## Garantias de segurança do projeto

O CaosZero foi projetado para reduzir o risco de perda de dados:

- **Simulação por padrão:** `organize` não altera arquivos sem `--apply`.
- **Confirmação:** operações reais pedem confirmação, exceto com `--yes`.
- **Sem sobrescrita:** destinos existentes recebem nomes únicos (`(1)`, `(2)`).
- **Sem exclusão:** o aplicativo não apaga arquivos.
- **Raiz do sistema recusada:** `/` e `C:\` não podem ser alvo.
- **Links simbólicos ignorados:** evita ciclos e movimentação fora do alvo.
- **Diretório de estado protegido:** journals e logs não são organizados.
- **Journal incremental:** cada operação é registrada antes e depois de
  executada.
- **Undo seguro:** não sobrescreve a origem e reporta conflitos.
- **Sem rede:** a aplicação não faz chamadas de rede.
- **Sem dependências externas obrigatórias:** reduz a superfície de ataque.
- **Configuração validada:** JSON inválido ou campos com tipo errado são
  recusados.
- **Encoding explícito:** leitura e escrita usam UTF-8 (CSV com BOM para
  planilhas).

## Limitações conhecidas

- **TOCTOU:** entre o planejamento e a execução, o sistema de arquivos pode
  mudar. O executor revalida origem e destino, mas não há bloqueio de arquivo.
- **Sem locking:** duas instâncias simultâneas no mesmo diretório podem competir.
  Recomenda-se uma instância por alvo ou agendamento sem sobreposição.
- **Confiança no usuário:** o CaosZero roda com as permissões de quem o executa.
  Ele não eleva privilégios.
- **Journal local:** o undo depende do journal e dos arquivos não terem sido
  movidos manualmente.
- **Sem sandbox de sistema:** a aplicação não isola processos; ela apenas valida
  caminhos e operações.
- **Permissões do SO:** o aplicativo não altera ACLs nem corrige permissões
  existentes.

## Boas práticas para uso seguro

1. Execute primeiro sem `--apply` e revise o plano.
2. Teste em uma pasta de demonstração (`python caoszero.py demo`).
3. Mantenha backups de diretórios importantes.
4. Não execute como administrador/root sem necessidade.
5. Não aponte o alvo para a raiz do sistema ou para a pasta pessoal inteira.
6. Verifique o journal após execuções automatizadas.
7. Use `CAOSZERO_HOME` em um diretório com permissões adequadas.
8. Revise scripts de agendamento antes de registrá-los.

## Segredos e dados sensíveis

- Nunca commite arquivos como `.env`, tokens, chaves ou credenciais.
- Use variáveis de ambiente ou o gerenciador de credenciais do sistema.
- Se um segredo for exposto, revogue-o imediatamente e registre o incidente.
- O `.gitignore` já bloqueia `.env`, logs e estado local.

## Tratamento dos relatos

Os relatos serão analisados conforme a disponibilidade e a natureza do projeto.
O processo busca:

1. Confirmar o problema e o impacto.
2. Desenvolver uma correção com teste de regressão.
3. Publicar a correção e, quando apropriado, um aviso de segurança.
4. Dar crédito a quem relatou, se houver consentimento.

Como projeto acadêmico, não há prazo formal de resposta nem programa de
recompensas.

## Escopo

Esta política cobre o código, os scripts e a documentação mantidos neste
repositório. Projetos derivados precisam estabelecer e manter sua própria
política de segurança.
