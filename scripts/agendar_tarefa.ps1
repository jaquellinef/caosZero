# Agenda a organização automática de uma pasta no Windows.
#
# Sem -Register, apenas mostra o comando que seria registrado.
# Com -Register, cria uma tarefa diária no Agendador de Tarefas.
#
# Uso:
#   .\scripts\agendar_tarefa.ps1
#   .\scripts\agendar_tarefa.ps1 -Target "$HOME\Downloads" -Time "09:00" -Register
param(
    [string]$Target = (Join-Path $HOME "Downloads"),
    [string]$Time = "09:00",
    [switch]$Register
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Python = if ($env:CAOSZERO_PYTHON) { $env:CAOSZERO_PYTHON } else { "python" }
$Script = Join-Path $Root "caoszero.py"
$ArgumentList = "`"$Script`" organize `"$Target`" --apply --yes --report auto"
$TaskName = "CaosZero - Organizar $(Split-Path -Leaf $Target)"

Write-Host "Tarefa....: $TaskName"
Write-Host "Horário...: $Time (diariamente)"
Write-Host "Alvo......: $Target"
Write-Host "Comando...: $Python $ArgumentList"

if (-not $Register) {
    Write-Host ""
    Write-Host "Nada foi alterado. Use -Register para criar a tarefa."
    exit 0
}

$Action = New-ScheduledTaskAction -Execute $Python -Argument $ArgumentList
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Organização automática de arquivos com CaosZero" | Out-Null
Write-Host ""
Write-Host "Tarefa registrada. Verifique com: Get-ScheduledTask -TaskName '$TaskName'"
