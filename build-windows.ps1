$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Crie .venv e instale requirements-build.txt antes de gerar a distribuição.'
}
New-Item -ItemType Directory -Force -Path build, dist | Out-Null
$assetArgument = "$(Join-Path $PSScriptRoot 'assets');assets"
& $python -m PyInstaller --noconfirm --clean --onedir --windowed --contents-directory . `
    --name ArcaneTrials --add-data $assetArgument --specpath build `
    --workpath build\pyinstaller --distpath dist main.py
if ($LASTEXITCODE -ne 0) { throw 'O PyInstaller não conseguiu gerar a distribuição.' }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'INSTRUCOES.txt') -Destination (Join-Path $PSScriptRoot 'dist\ArcaneTrials\INSTRUCOES.txt') -Force

$archive = Join-Path $PSScriptRoot 'dist\ArcaneTrials_V1_Windows.zip'
Compress-Archive -LiteralPath (Join-Path $PSScriptRoot 'dist\ArcaneTrials') -DestinationPath $archive -Force
Write-Host "Distribuição criada: $archive"
