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
    PLAN_MODELS = {
        "go": {
            "orchestrator": "mimo/MiMo-V2.5-Pro",
            "code-analyst": "deepseek/DeepSeek-V4-Pro", 
            "validator": "moonshot/Kimi-K2.6",
            "bulk-processor": "deepseek/DeepSeek-V4-Flash",
            "fallback": "qwen/Qwen3.5-Plus"  # Si algún modelo falla
        },
        "zen": {
            "orchestrator": "github/copilot-chat",  # o "anthropic/claude-sonnet-4"
            "code-analyst": "github/copilot-code",
            "validator": "anthropic/claude-haiku-3",
            "bulk-processor": "deepseek/DeepSeek-V4-Flash",  # requiere API key
            "fallback": "openai/gpt-4o-mini"
        },
        "api": {
            "orchestrator": os.getenv("ORCHESTRATOR_MODEL", "anthropic/claude-sonnet-4"),
            "code-analyst": os.getenv("CODE_ANALYST_MODEL", "deepseek/DeepSeek-V4-Pro"),
            "validator": os.getenv("VALIDATOR_MODEL", "anthropic/claude-haiku-3"),
            "bulk-processor": os.getenv("BULK_MODEL", "deepseek/DeepSeek-V4-Flash"),
            "fallback": os.getenv("FALLBACK_MODEL", "openai/gpt-4o-mini")
        },
        "enterprise": {
            "orchestrator": os.getenv("ENT_ORCHESTRATOR", "mimo/MiMo-V2.5-Pro"),
            "code-analyst": os.getenv("ENT_ANALYST", "deepseek/DeepSeek-V4-Pro"),
            "validator": os.getenv("ENT_VALIDATOR", "moonshot/Kimi-K2.6"),
            "bulk-processor": os.getenv("ENT_BULK", "deepseek/DeepSeek-V4-Flash"),
            "fallback": os.getenv("ENT_FALLBACK", "qwen/Qwen3.5-Plus")
        }
    }
    
    # Límites aproximados por plan (para monitoreo)
    PLAN_LIMITS = {
        "go": {"daily": 5000, "weekly": 25000, "monthly": 100000},
        "zen": {"daily": 2000, "weekly": 10000, "monthly": 40000},
        "api": {"daily": "variable", "weekly": "variable", "monthly": "variable"},
        "enterprise": {"daily": "custom", "weekly": "custom", "monthly": "custom"}
    }
    
    def __init__(self, plan: Optional[str] = None):
        self.plan = plan or self._detect_plan()
        self.models = self.PLAN_MODELS.get(self.plan, self.PLAN_MODELS["api"])
        self.limits = self.PLAN_LIMITS.get(self.plan, self.PLAN_LIMITS["api"])
    
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
                    return json.load(f).get("plan", "api")
            except:
                pass
        
        # 3. Detectar por variables de API key
        if os.getenv("OPENCODE_API_KEY") or os.getenv("ANTHROPIC_API_KEY"):
            return "api"
        
        # 4. Detectar GitHub Copilot (Zen)
        if os.getenv("GITHUB_TOKEN") or os.getenv("COPILOT_TOKEN"):
            return "zen"
        
        # 5. Default: asumir Go si opencode CLI funciona sin keys
        try:
            import subprocess
            result = subprocess.run(
                ["opencode", "models", "--json"], 
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and "mimo" in result.stdout.lower():
                return "go"
        except:
            pass
        
        return "api"  # Fallback más seguro
    
    def get_model(self, role: str) -> str:
        """Obtiene el modelo para un rol, con fallback si no está disponible"""
        model = self.models.get(role) or self.models["fallback"]
        
        # Si es plan API, validar que haya API key configurada
        if self.plan == "api" and "provider/" in model:
            provider = model.split("/")[0]
            key_var = f"{provider.upper()}_API_KEY".replace("-", "_")
            if not os.getenv(key_var):
                print(f"⚠️  Warning: {key_var} no configurada, usando fallback")
                return self.models["fallback"]
        
        return model
    
    def generate_config_snippet(self) -> Dict:
        """Genera snippet de configuración para opencode.json"""
        return {
            "plan": self.plan,
            "models": {role: self.get_model(role) for role in ["orchestrator", "code-analyst", "validator", "bulk-processor"]},
            "limits": self.limits,
            "requires_api_keys": self.plan == "api",
            "auto_fallback": True
        }