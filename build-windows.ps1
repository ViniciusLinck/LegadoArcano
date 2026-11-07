$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Crie .venv e instale requirements-build.txt.' }
New-Item -ItemType Directory -Force -Path build, dist | Out-Null
$assetArgument = "$(Join-Path $PSScriptRoot 'assets');assets"
& $python -m PyInstaller --noconfirm --clean --onedir --windowed --contents-directory . `
    --name LegadoArcano --add-data $assetArgument --specpath build `
    --workpath build\legado-pyinstaller --distpath dist main.py
if ($LASTEXITCODE -ne 0) { throw 'Falha na compilação PyInstaller.' }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'INSTRUCOES.txt') -Destination (Join-Path $PSScriptRoot 'dist\LegadoArcano\INSTRUCOES.txt') -Force
$archive = Join-Path $PSScriptRoot 'dist\LegadoArcano_Entrega.zip'
& $python -m zipfile -c $archive (Join-Path $PSScriptRoot 'dist\LegadoArcano')
if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar ZIP.' }
Write-Host "Distribuição criada: $archive"
