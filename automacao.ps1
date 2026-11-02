# Compatibilidade: a automação agora fica em scripts/automacao.ps1.
$ErrorActionPreference = "Stop"
$Script = Join-Path $PSScriptRoot "scripts\automacao.ps1"
& $Script @args
exit $LASTEXITCODE
