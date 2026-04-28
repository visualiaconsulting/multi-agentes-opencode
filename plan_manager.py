# config/plan_manager.py
"""
Plan Manager — Detecta el plan OpenCode y adapta configuración de agentes
"""
import os
import json
from pathlib import Path
from typing import Dict, Optional

class PlanManager:
    # Mapeo de planes a modelos disponibles por rol
    # Usando IDs de registro (provider/model-id) que OpenCode reconoce
    PLAN_MODELS = {
        "go": {
            "orchestrator": "opencode-go/mimo-v2.5-pro",
            "code-analyst": "opencode-go/deepseek-v4-pro",
            "validator": "opencode-go/kimi-k2.6",
            "bulk-processor": "opencode-go/deepseek-v4-flash",
            "subagent": "opencode-go/glm-5.1",
            "fallback": "opencode-go/minimax-m2.5",
            "all_available": [
                "opencode-go/glm-5", "opencode-go/glm-5.1",
                "opencode-go/kimi-k2.5", "opencode-go/kimi-k2.6",
                "opencode-go/mimo-v2-pro", "opencode-go/mimo-v2-omni",
                "opencode-go/mimo-v2.5-pro", "opencode-go/mimo-v2.5",
                "opencode-go/minimax-m2.5", "opencode-go/minimax-m2.7",
                "opencode-go/deepseek-v4-pro", "opencode-go/deepseek-v4-flash"
            ]
        },
        "zen": {
            "orchestrator": "opencode/claude-sonnet-4.5",
            "code-analyst": "opencode/gpt-5.1-codex",
            "validator": "opencode/claude-haiku-4.5",
            "bulk-processor": "opencode/gemini-3-flash",
            "subagent": "opencode/gpt-5.4-mini",
            "fallback": "opencode/gpt-5.4-mini",
            "all_available": [
                "opencode/big-pickle",
                "opencode/minimax-m2.5-free", "opencode/minimax-m2.5",
                "opencode/claude-haiku-4.5", "opencode/claude-opus-4.5",
                "opencode/claude-sonnet-4.5",
                "opencode/gpt-5.1-codex", "opencode/gpt-5.4-mini",
                "opencode/gemini-3-flash",
                "opencode-go/glm-5", "opencode-go/glm-5.1",
                "opencode/hy3-preview-free",
                "opencode-go/kimi-k2.5", "opencode-go/kimi-k2.6",
                "opencode/ling-2.6-flash-free",
                "opencode/nemotron-3-super-free"
            ]
        },
        "api": {
            "orchestrator": os.getenv("ORCHESTRATOR_MODEL", "anthropic/claude-sonnet-4"),
            "code-analyst": os.getenv("CODE_ANALYST_MODEL", "deepseek/DeepSeek-V4-Pro"),
            "validator": os.getenv("VALIDATOR_MODEL", "anthropic/claude-haiku-3"),
            "bulk-processor": os.getenv("BULK_MODEL", "deepseek/DeepSeek-V4-Flash"),
            "subagent": os.getenv("SUBAGENT_MODEL", "openai/gpt-4o-mini"),
            "fallback": os.getenv("FALLBACK_MODEL", "openai/gpt-4o-mini")
        },
        "enterprise": {
            "orchestrator": os.getenv("ENT_ORCHESTRATOR", "opencode-go/mimo-v2.5-pro"),
            "code-analyst": os.getenv("ENT_ANALYST", "opencode-go/deepseek-v4-pro"),
            "validator": os.getenv("ENT_VALIDATOR", "opencode-go/kimi-k2.6"),
            "bulk-processor": os.getenv("ENT_BULK", "opencode-go/deepseek-v4-flash"),
            "subagent": os.getenv("ENT_SUBAGENT", "opencode-go/glm-5.1"),
            "fallback": os.getenv("ENT_FALLBACK", "opencode-go/minimax-m2.5")
        },
        "openrouter": {
            "orchestrator": os.getenv("OR_OPENROUTER", "openrouter/anthropic/claude-sonnet-4.5"),
            "code-analyst": os.getenv("OR_ANALYST", "openrouter/google/gemini-2.5-pro"),
            "validator": os.getenv("OR_VALIDATOR", "openrouter/anthropic/claude-haiku-4.5"),
            "bulk-processor": os.getenv("OR_BULK", "openrouter/deepseek/deepseek-v3"),
            "subagent": os.getenv("OR_SUBAGENT", "openrouter/meta-llama/llama-3.3-70b"),
            "fallback": os.getenv("OR_FALLBACK", "openrouter/openai/gpt-4o-mini")
        },
        "copilot": {
            "orchestrator": "copilot/claude-sonnet-4",
            "code-analyst": "copilot/gpt-4.1",
            "validator": "copilot/claude-haiku-4",
            "bulk-processor": "copilot/gpt-4.1-mini",
            "subagent": "copilot/claude-haiku-4",
            "fallback": "copilot/gpt-4.1-nano"
        },
        "ollama": {
            "orchestrator": os.getenv("OLLAMA_ORCH", "ollama/llama3.3:70b"),
            "code-analyst": os.getenv("OLLAMA_ANALYST", "ollama/qwen2.5-coder:32b"),
            "validator": os.getenv("OLLAMA_VALIDATOR", "ollama/llama3.2:3b"),
            "bulk-processor": os.getenv("OLLAMA_BULK", "ollama/qwen2.5-coder:7b"),
            "subagent": os.getenv("OLLAMA_SUB", "ollama/llama3.1:8b"),
            "fallback": os.getenv("OLLAMA_FALLBACK", "ollama/phi3:3.8b")
        }
    }
    
    # Límites aproximados por plan (para monitoreo)
    PLAN_LIMITS = {
        "go": {"daily": 5000, "weekly": 25000, "monthly": 100000},
        "zen": {"daily": 2000, "weekly": 10000, "monthly": 40000},
        "api": {"daily": "variable", "weekly": "variable", "monthly": "variable"},
        "enterprise": {"daily": "custom", "weekly": "custom", "monthly": "custom"},
        "openrouter": {"daily": "variable", "weekly": "variable", "monthly": "variable"},
        "copilot": {"daily": "included", "weekly": "included", "monthly": "included"},
        "ollama": {"daily": "unlimited", "weekly": "unlimited", "monthly": "unlimited"}
    }
    
    def __init__(self, plan: Optional[str] = None):
        self.plan = plan or self._detect_plan()
        self.models = self.PLAN_MODELS.get(self.plan, self.PLAN_MODELS["go"])
        self.limits = self.PLAN_LIMITS.get(self.plan, self.PLAN_LIMITS["go"])
    
    def _detect_plan(self) -> str:
        """Detecta automáticamente el plan basado en entorno/config"""
        # 1. Variable de entorno explícita
        if env_plan := os.getenv("OPENCODE_PLAN"):
            return env_plan.lower()
        
        # 2. Archivo de configuración local
        config_path = Path(".opencode/plan.json")
        if config_path.exists():
            try:
                with open(config_path) as f:
                    return json.load(f).get("plan", "go")
            except (json.JSONDecodeError, OSError):
                pass
        
        # 3. Detectar por variables de API key (Go usa OPENCODE_API_KEY)
        if os.getenv("ANTHROPIC_API_KEY"):
            return "api"
        
        # 4. Detectar GitHub Copilot (Zen)
        if os.getenv("GITHUB_TOKEN") or os.getenv("COPILOT_TOKEN"):
            return "zen"
        
        # 5. Detectar OpenRouter
        if os.getenv("OPENROUTER_API_KEY"):
            return "openrouter"

        # 6. Detectar Ollama (local)
        if os.getenv("OLLAMA_HOST"):
            return "ollama"
        
        return "go"

    def get_available_models(self) -> list:
        """Retorna una lista de nombres de modelos disponibles para el plan actual"""
        if "all_available" in self.models:
            return self.models["all_available"]
        return list(set(self.models.values()))

    def get_model(self, role: str) -> str:
        """Obtiene el modelo para un rol, con fallback si no está disponible"""
        return self.models.get(role, self.models.get("fallback"))
    
    def generate_config_snippet(self) -> Dict:
        """Genera snippet de configuración para opencode.json"""
        return {
            "plan": self.plan,
            "models": {role: self.get_model(role) for role in ["orchestrator", "code-analyst", "validator", "bulk-processor"]},
            "limits": self.limits,
            "requires_api_keys": self.plan == "api",
            "auto_fallback": True
        }
