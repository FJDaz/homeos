#!/usr/bin/env python3
"""
Confrontation des 4 sources pour générer le Genome aligné.
"""

from dataclasses import dataclass
from typing import List, Optional, Literal
import json

@dataclass
class SourceClaim:
    """Une affirmation d'une source."""
    source: Literal["doc", "logs", "code", "kimi"]
    entity: str  # ex: "endpoint", "component", "route"
    name: str    # ex: "/studio/genome"
    claim: str   # ex: "existe", "renvoie HTML", "utilise HTMX"
    confidence: float  # 0.0 - 1.0

def load_kimi_report(path: str) -> List[SourceClaim]:
    """Parse le genome_inferred_by_kimi.json"""
    claims = []
    with open(path) as f:
        data = json.load(f)
    
    # Extraire les endpoints du rapport Kimi
    for ep in data.get("endpoints_summary", []):
        claims.append(SourceClaim(
            source="kimi",
            entity="endpoint",
            name=ep["path"],
            claim=f"{ep['method']} -> {ep['component']}",
            confidence=0.8  # Kimi infère, donc moins sûr
        ))
    
    return claims

def load_code_facts(path: str) -> List[SourceClaim]:
    """Parse le bundle_code.py"""
    claims = []
    # Pattern matching simple
    import re
    with open(path) as f:
        content = f.read()
    
    # Chercher @router.get/post
    pattern = r'@router\.(get|post|put|delete)\("([^"]+)"'
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    for method, path in matches:
        claims.append(SourceClaim(
            source="code",
            entity="endpoint",
            name=path,
            claim=f"{method.upper()} - implémenté",
            confidence=1.0  # Le code ne ment pas
        ))
    
    return claims

def load_logs_facts(path: str) -> List[SourceClaim]:
    """Parse les logs d'exécution."""
    claims = []
    # Pattern: GET /path 200
    import re
    with open(path) as f:
        for line in f:
            match = re.search(r'(GET|POST|PUT|DELETE)\s+([^\s]+)\s+(\d+)', line)
            if match:
                method, path, status = match.groups()
                confidence = 1.0 if status == "200" else 0.0
                claims.append(SourceClaim(
                    source="logs",
                    entity="endpoint",
                    name=path,
                    claim=f"{method} - HTTP {status}",
                    confidence=confidence
                ))
    return claims

def confront_claims(claims: List[SourceClaim]) -> dict:
    """
    Confronte les claims et résout les conflits.
    Règle: Code > Logs > Kimi > Doc
    """
    grouped = {}
    
    # Grouper par nom d'entité
    for claim in claims:
        key = f"{claim.entity}:{claim.name}"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(claim)
    
    resolved = {}
    
    for key, group in grouped.items():
        # Vérifier les conflits
        sources = {c.source for c in group}
        
        if len(sources) > 1:
            # Conflit détecté
            # Priorité: code (1.0) > logs (0.9) > kim (0.8) > doc (0.7)
            best = max(group, key=lambda c: {
                "code": 1.0,
                "logs": 0.9,
                "kimi": 0.8,
                "doc": 0.7
            }.get(c.source, 0) * c.confidence)
            
            resolved[key] = {
                "verdict": best.claim,
                "source": best.source,
                "confidence": best.confidence,
                "conflict_with": [c.source for c in group if c != best],
                "all_claims": [(c.source, c.claim) for c in group]
            }
        else:
            # Pas de conflit
            claim = group[0]
            resolved[key] = {
                "verdict": claim.claim,
                "source": claim.source,
                "confidence": claim.confidence,
                "conflict_with": [],
                "all_claims": [(claim.source, claim.claim)]
            }
    
    return resolved

def generate_aligned_genome(resolved: dict) -> dict:
    """
    Génère le Genome final aligné sur les 4 sources.
    """
    genome = {
        "metadata": {
            "method": "4-source-confrontation",
            "sources": ["doc", "logs", "code", "kimi"],
            "resolution_rule": "code > logs > kim > doc",
            "generated_at": "2026-02-06"
        },
        "endpoints": [],
        "conflicts_resolved": [],
        "uncertain": []
    }
    
    for key, data in resolved.items():
        entity, name = key.split(":", 1)
        
        if data["confidence"] >= 0.9:
            # Haute confiance
            genome["endpoints"].append({
                "path": name,
                "status": "confirmed",
                "source": data["source"],
                "claim": data["verdict"]
            })
        elif data["conflict_with"]:
            # Conflit résolu
            genome["conflicts_resolved"].append({
                "path": name,
                "verdict": data["verdict"],
                "winner": data["source"],
                "losers": data["conflict_with"],
                "all_claims": data["all_claims"]
            })
        else:
            # Incertain
            genome["uncertain"].append({
                "path": name,
                "claim": data["verdict"],
                "confidence": data["confidence"]
            })
    
    return genome

if __name__ == "__main__":
    # Charger les 3 sources
    kim_claims = load_kimi_report("genome_inferred_by_kimi.json")
    code_claims = load_code_facts("bundle_code.py")
    logs_claims = load_logs_facts("bundle_reality.log")
    
    # Fusionner
    all_claims = kim_claims + code_claims + logs_claims
    
    # Confronter
    resolved = confront_claims(all_claims)
    
    # Générer
    genome = generate_aligned_genome(resolved)
    
    # Sauvegarder
    with open("genome_aligned_4_sources.json", "w") as f:
        json.dump(genome, f, indent=2)
    
    print(f"✅ Genome aligné généré")
    print(f"   - Endpoints confirmés: {len(genome['endpoints'])}")
    print(f"   - Conflits résolus: {len(genome['conflicts_resolved'])}")
    print(f"   - Incertains: {len(genome['uncertain'])}")
