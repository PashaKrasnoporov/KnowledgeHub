$ErrorActionPreference = "Stop"

$Repo = $PSScriptRoot
Set-Location $Repo

Write-Host ""
Write-Host "=== KNOWLEDGEHUB V2 CHECKS ===" -ForegroundColor Cyan

git diff --check
if ($LASTEXITCODE -ne 0) {
    throw "git diff --check FAILED."
}

Set-Location "$Repo\frontend"
npm run build
if ($LASTEXITCODE -ne 0) {
    throw "Frontend build FAILED."
}

Set-Location $Repo

$PythonExe = $null
$PythonPrefix = @()

$Candidates = @(
    "$Repo\.venv\Scripts\python.exe",
    "$Repo\backend\.venv\Scripts\python.exe"
)

foreach ($Candidate in $Candidates) {
    if (Test-Path $Candidate) {
        $PythonExe = $Candidate
        break
    }
}

if (-not $PythonExe) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $PythonExe = "py"
        $PythonPrefix = @("-3")
    }
    elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $PythonExe = "python"
    }
}

if (-not $PythonExe) {
    throw "Python interpreter not found."
}

function Invoke-KHPython {
    param(
        [string[]]$PythonArgs
    )

    $InvokeArgs = @($PythonPrefix) + @($PythonArgs)
    & $PythonExe @InvokeArgs

    if ($LASTEXITCODE -ne 0) {
        throw "Python check FAILED."
    }
}

Invoke-KHPython -PythonArgs @(
    "-m",
    "compileall",
    "-q",
    "backend\app"
)

Invoke-KHPython -PythonArgs @(
    "backend\tests\test_v2_contracts.py"
)

Invoke-KHPython -PythonArgs @(
    "backend\tests\test_rag_quality_smoke.py"
)

Invoke-KHPython -PythonArgs @(
    "backend\tests\test_railway_readiness.py"
)

Invoke-KHPython -PythonArgs @(
    "backend\tests\test_production_parity_contract.py"
)

Invoke-KHPython -PythonArgs @(
    "backend\tests\test_llm_service_contract.py"
)



try {
    $Health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health" -Method Get -TimeoutSec 3
    Write-Host "Local API health : PASS ($($Health.app_version))" -ForegroundColor Green
}
catch {
    Write-Host "Local API health : SKIPPED (backend is not running)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "V2 AUTOMATED CHECKS : PASS" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
