from typing import Dict, Any, List

PLAN_LIMITS = {
    "FREE": {
        "max_projects": 3,
        "ai_models": ["qwen", "llama", "gemini-flash-lite"],
        "stitch": False,
        "byok": False,
        "monthly_tokens": 50_000,
        "max_screens_per_upload": 4
    },
    "PRO": {
        "max_projects": 20,
        "ai_models": ["*"],
        "stitch": True,
        "byok": True,
        "monthly_tokens": 500_000,
        "max_screens_per_upload": 20
    },
    "MAX": {
        "max_projects": 999,
        "ai_models": ["*"],
        "stitch": True,
        "byok": True,
        "monthly_tokens": None,
        "max_screens_per_upload": 100
    },
}

def resolve_entitlements(plan: str, role: str) -> Dict[str, Any]:
    """
    M283a: Résout les droits d'un utilisateur selon son plan et son rôle.
    Les admins et profs ont des droits PRO par défaut ou plus.
    """
    # Profs et Admins sont au moins PRO
    effective_plan = plan
    if role in ["admin", "prof"] and plan == "FREE":
        effective_plan = "PRO"
    
    limits = PLAN_LIMITS.get(effective_plan, PLAN_LIMITS["FREE"])
    
    # Entitlements supplémentaires selon le rôle
    entitlements = {
        **limits,
        "is_teacher": role in ["admin", "prof"],
        "can_manage_classes": role in ["admin", "prof"],
        "effective_plan": effective_plan
    }
    
    return entitlements
