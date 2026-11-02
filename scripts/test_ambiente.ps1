# Cria um ambiente de demonstração com arquivos variados.
#
# Uso:
#   .\scripts\test_ambiente.ps1
#   .\scripts\test_ambiente.ps1 -Destino "C:\Temp\caoszero-demo"
param(
    [string]$Destino = (Join-Path (Split-Path -Parent $PSScriptRoot) "sandbox_teste")
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

$Python = if ($env:CAOSZERO_PYTHON) { $env:CAOSZERO_PYTHON } else { "python" }
& $Python "$Root\caoszero.py" demo $Destino
exit $LASTEXITCODE
