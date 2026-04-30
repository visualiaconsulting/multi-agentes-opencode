# install.ps1 — Quick install for oh-my-agents on a new Windows machine
# Run after cloning the repo:
#   git clone https://github.com/visualiaconsulting/oh-my-agents.git
#   cd oh-my-agents
#   .\install.ps1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  oh-my-agents — Quick Install" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find Python
$PythonCmd = $null
$candidates = @("py -3", "python3", "python")
foreach ($cmd in $candidates) {
    $exe = ($cmd -split ' ')[0]
    $arg = ($cmd -split ' ')[1]
    try {
        $null = Get-Command $exe -ErrorAction Stop
        if ($arg) {
            $ver = & $exe $arg --version 2>&1
        } else {
            $ver = & $exe --version 2>&1
        }
        if ($ver -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -ge 3 -and $minor -ge 8) {
                $PythonCmd = if ($arg) { "$exe $arg" } else { $exe }
                break
            }
        }
    } catch { continue }
}

if (-not $PythonCmd) {
    Write-Host "  ERROR: Python 3.8+ not found. Install from https://python.org" -ForegroundColor Red
    exit 1
}

Write-Host "[1/3] Python: $(& $PythonCmd --version 2>&1)" -ForegroundColor Green

# Install deps
Write-Host "[2/3] Installing dependencies..." -ForegroundColor Yellow
& $PythonCmd -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Dependency installation failed" -ForegroundColor Red
    exit 1
}

# Global install
Write-Host "[3/3] Installing agents globally..." -ForegroundColor Yellow
& $PythonCmd main.py --install-global
if ($LASTEXITCODE -ne 0) {
    Write-Host "  WARNING: Global install had issues" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  opencode --agent orchestrator" -ForegroundColor White
Write-Host ""
