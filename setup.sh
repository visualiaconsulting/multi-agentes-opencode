#!/bin/bash
# setup.sh — Bootstrap for Linux/Mac
# oh-my-agents — OpenCode Multi-Agent Framework

echo ""
echo "========================================"
echo "  oh-my-agents — Setup"
echo "========================================"
echo ""

# Change to the script's directory so relative paths work correctly
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Check Python
echo "[1/5] Checking Python..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "  ERROR: Python not found. Install Python 3.8+ from https://python.org"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "  OK: $PYTHON_VERSION"

# 2. Install dependencies
echo "[2/5] Installing dependencies..."
$PYTHON_CMD -m pip install -r "$SCRIPT_DIR"/requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "  ERROR: Failed to install dependencies"
    exit 1
fi
echo "  OK: Dependencies installed"

# 3. Check OpenCode CLI
echo "[3/5] Checking OpenCode CLI..."
if command -v opencode &> /dev/null; then
    echo "  OK: OpenCode CLI found"
else
    echo "  WARNING: OpenCode CLI not found"
    echo "  Install from: https://opencode.ai"
    echo ""
fi

# 4. Handle --install-global flag (checked BEFORE running main.py)
if [ "$1" = "--install-global" ]; then
    echo "[4/5] Installing CLI globally..."
    TARGET="/usr/local/bin/oh-my-agents"

    # Fall back to ~/.local/bin if /usr/local/bin doesn't exist
    if [ ! -d "/usr/local/bin" ] && [ -d "$HOME/.local/bin" ]; then
        TARGET="$HOME/.local/bin/oh-my-agents"
    fi

    cat > "$TARGET" << GLOBALEOF
#!/bin/bash
cd "$SCRIPT_DIR" && $PYTHON_CMD main.py "\$@"
GLOBALEOF

    chmod +x "$TARGET"
    echo "  OK: 'oh-my-agents' installed at $TARGET"
    echo "  Usage: oh-my-agents"
    exit 0
fi

# 5. Run CLI (interactive mode)
echo "[4/5] Starting system..."
echo ""
$PYTHON_CMD main.py

# 6. Global install (makes agents available from any directory)
echo ""
echo "[5/5] Global install..."
echo ""
echo "  OpenCode looks for .opencode/ in the current directory by default."
echo "  Without a global install, agents only work when you are inside this project."
echo ""
echo "  Global install copies agent definitions to ~/.opencode/agents/ so"
echo "  opencode --agent orchestrator works from ANY folder on your system."
echo ""

read -p "  Install agents globally? [Y/n] " -r
if [[ $REPLY =~ ^$|^[Yy]$ ]]; then
    echo ""
    $PYTHON_CMD main.py --install-global
    if [ $? -ne 0 ]; then
        echo "  WARNING: Global install reported an error. Check the output above."
    fi
else
    echo ""
    echo "  Skipped. Agents will only work inside this project directory."
    echo "  Run later: python main.py --install-global"
fi

echo ""
echo "========================================"
echo "  Setup complete!"
echo "========================================"
echo ""
echo "  Run: opencode --agent orchestrator"
echo ""
