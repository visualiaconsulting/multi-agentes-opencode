#!/bin/bash
# setup.sh — Bootstrap for Linux/Mac
# oh-my-agents — OpenCode Multi-Agent Framework

echo ""
echo "========================================"
echo "  oh-my-agents — Setup"
echo "========================================"
echo ""

# 1. Verificar Python
echo "[1/4] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "  ERROR: Python no encontrado. Instala Python 3.8+ desde https://python.org"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "  OK: $PYTHON_VERSION"

# 2. Instalar dependencias
echo "[2/4] Instalando dependencias..."
$PYTHON_CMD -m pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "  ERROR: Fallo al instalar dependencias"
    exit 1
fi
echo "  OK: Dependencias instaladas"

# 3. Verificar OpenCode CLI
echo "[3/4] Verificando OpenCode CLI..."
if command -v opencode &> /dev/null; then
    echo "  OK: OpenCode CLI encontrado"
else
    echo "  ADVERTENCIA: OpenCode CLI no encontrado"
    echo "  Instala desde: https://opencode.ai"
    echo ""
fi

# 4. Ejecutar CLI
echo "[4/4] Iniciando sistema..."
echo ""
$PYTHON_CMD main.py
