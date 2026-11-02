# Verificação completa usada localmente (Windows).
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Python = if ($env:CAOSZERO_PYTHON) { $env:CAOSZERO_PYTHON } else { "python" }

Push-Location $Root
try {
    Write-Host "==> Compilando módulos"
    & $Python -m compileall -q src tests

    Write-Host "==> Executando testes automatizados"
    & $Python -m unittest discover -s tests -v

    Write-Host "==> Smoke test da CLI"
    $Temp = Join-Path ([System.IO.Path]::GetTempPath()) ("caoszero-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $Temp | Out-Null
    try {
        $env:CAOSZERO_HOME = Join-Path $Temp "estado"
        & $Python caoszero.py demo (Join-Path $Temp "sandbox") | Out-Null
        & $Python caoszero.py organize (Join-Path $Temp "sandbox") --apply --yes --report (Join-Path $Temp "relatorio.md") | Out-Null
        & $Python caoszero.py doctor --json | Out-Null
        if (-not (Test-Path (Join-Path $Temp "relatorio.md"))) {
            throw "Relatório não foi gerado."
        }
    } finally {
        Remove-Item -Recurse -Force $Temp -ErrorAction SilentlyContinue
    }

    Write-Host "==> Tudo certo."
} finally {
    Pop-Location
}
