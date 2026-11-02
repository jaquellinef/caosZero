# CaosZero — execução automatizada no Windows (PowerShell).
#
# Uso:
#   .\scripts\automacao.ps1
#   .\scripts\automacao.ps1 -Apply
#   .\scripts\automacao.ps1 -Target "$HOME\Downloads" -Apply -Report
#   .\scripts\automacao.ps1 -Doctor
param(
    [string]$Target = $env:CAOSZERO_TARGET,
    [switch]$Apply,
    [string]$Report,
    [switch]$Doctor
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

function Find-Python {
    if ($env:CAOSZERO_PYTHON) {
        return @($env:CAOSZERO_PYTHON)
    }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        return @($py.Source, "-3")
    }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return @($python.Source)
    }
    throw "Python 3 não encontrado. Instale o Python 3.10+ ou defina CAOSZERO_PYTHON."
}

$PythonCommand = Find-Python
$PythonExe = $PythonCommand[0]
$PythonPrefix = @()
if ($PythonCommand.Count -gt 1) {
    $PythonPrefix = $PythonCommand[1..($PythonCommand.Count - 1)]
}

if (-not $Target) {
    $downloads = Join-Path $HOME "Downloads"
    if (Test-Path $downloads) {
        $Target = $downloads
    } else {
        $Target = (Get-Location).Path
    }
}

$Arguments = @()
if ($Doctor) {
    $Arguments = @("$Root\caoszero.py", "doctor", $Target)
} else {
    $Arguments = @("$Root\caoszero.py", "organize", $Target)
    if ($Apply) {
        $Arguments += @("--apply", "--yes")
    }
    if ($Report) {
        $Arguments += @("--report", $Report)
    }
}

Write-Host "=============================================="
Write-Host "  CaosZero — automação de arquivos"
Write-Host "=============================================="
Write-Host "Python: $(& $PythonExe @PythonPrefix --version 2>&1)"
Write-Host "Alvo...: $Target"
Write-Host "Modo...: $(if ($Apply) { 'EXECUÇÃO' } else { 'SIMULAÇÃO' })"
Write-Host ""

& $PythonExe @PythonPrefix @Arguments
$ExitCode = $LASTEXITCODE

Write-Host ""
$StateDir = if ($env:CAOSZERO_HOME) { $env:CAOSZERO_HOME } else { Join-Path $env:LOCALAPPDATA "CaosZero" }
Write-Host "Execução finalizada. Consulte os relatórios em:"
Write-Host "  $StateDir\reports"

exit $ExitCode
