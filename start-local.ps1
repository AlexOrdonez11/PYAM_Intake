$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

$bundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$python = if (Test-Path -LiteralPath $bundledPython) { $bundledPython } else { "python" }
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
  & $python -m venv .venv
}

& $venvPython -m pip install -r requirements.txt
& $venvPython -m uvicorn backend.main:app --host 127.0.0.1 --port 5177 --reload
