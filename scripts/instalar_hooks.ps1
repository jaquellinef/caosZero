# Instala os hooks locais de Git no Windows.
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$HooksDir = Join-Path $Root ".git\hooks"

if (-not (Test-Path $HooksDir)) {
    throw "$Root não parece ser um repositório Git."
}

foreach ($Hook in @("pre-commit", "pre-push")) {
    $Source = Join-Path $PSScriptRoot "githooks\$Hook"
    $Destination = Join-Path $HooksDir $Hook
    Copy-Item $Source $Destination -Force
    Write-Host "Hook instalado: $Hook"
}

Write-Host ""
Write-Host "Pronto. Os hooks rodam via Git Bash antes de commit e push."
