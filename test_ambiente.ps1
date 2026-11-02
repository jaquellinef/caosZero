# Compatibilidade: o ambiente de teste agora fica em scripts/test_ambiente.ps1.
$ErrorActionPreference = "Stop"
$Script = Join-Path $PSScriptRoot "scripts\test_ambiente.ps1"
& $Script @args
exit $LASTEXITCODE
