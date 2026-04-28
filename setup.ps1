# setup.ps1 — Bootstrap for Windows
# oh-my-agents — OpenCode Multi-Agent Framework

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  oh-my-agents — Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "[1/4] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-Host "  ERROR: Se requiere Python 3.8+. Version detectada: $pythonVersion" -ForegroundColor Red
            exit 1
        }
        Write-Host "  OK: $pythonVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "  ERROR: Python no encontrado. Instala Python 3.8+ desde https://python.org" -ForegroundColor Red
    exit 1
}

# 2. Instalar dependencias
Write-Host "[2/4] Instalando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Fallo al instalar dependencias" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: Dependencias instaladas" -ForegroundColor Green

# 3. Verificar OpenCode CLI
Write-Host "[3/4] Verificando OpenCode CLI..." -ForegroundColor Yellow
$opencodeAvailable = Get-Command opencode -ErrorAction SilentlyContinue
if ($opencodeAvailable) {
    Write-Host "  OK: OpenCode CLI encontrado" -ForegroundColor Green
} else {
    Write-Host "  ADVERTENCIA: OpenCode CLI no encontrado" -ForegroundColor Yellow
    Write-Host "  Instala desde: https://opencode.ai" -ForegroundColor Yellow
    Write-Host ""
}

# 4. Ejecutar CLI
Write-Host "[4/4] Iniciando sistema..." -ForegroundColor Yellow
Write-Host ""
python main.py
