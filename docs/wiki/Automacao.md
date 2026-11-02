# Automação

## Linux/macOS

```bash
chmod +x scripts/*.sh

# Simular
./scripts/automacao.sh --target ~/Downloads

# Executar e gerar relatório
./scripts/automacao.sh --target ~/Downloads --apply --report

# Diagnóstico
./scripts/automacao.sh --target ~/Downloads --doctor

# Agendar diariamente às 09:00
./scripts/agendar_cron.sh --target ~/Downloads --time 09:00 --apply
```

## Windows

```powershell
.\scripts\automacao.ps1 -Target "$HOME\Downloads"
.\scripts\automacao.ps1 -Target "$HOME\Downloads" -Apply -Report
.\scripts\automacao.ps1 -Target "$HOME\Downloads" -Doctor

.\scripts\agendar_tarefa.ps1 -Target "$HOME\Downloads" -Time "09:00" -Register
```

## Segurança

- Sem `--apply`/`-Register`, os scripts apenas mostram o que fariam.
- Caminhos absolutos para Python e para o projeto.
- Relatório automático em cada execução.
- Códigos de saída propagados para o agendador.

## Variáveis de ambiente

| Variável | Efeito |
| --- | --- |
| `CAOSZERO_HOME` | Diretório de estado |
| `CAOSZERO_CONFIG` | Configuração |
| `CAOSZERO_TARGET` | Alvo padrão |
| `CAOSZERO_PYTHON` | Interpretador |

Voltar para [Home](Home).
