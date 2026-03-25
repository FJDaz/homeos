#!/usr/bin/env python3
"""
archetype_detector.py — Mission 40C
Module de reconnaissance de pattern fonctionnel (Archétypes).
Fait le pont entre l'analyse visuelle brute et les services API/Inférences.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger

class ArchetypeDetector:
    def __init__(self):
        self.archetypes_path = Path(__file__).parent / "functional_archetypes.json"
        self.archetypes = self._load_archetypes()

    def _load_archetypes(self) -> List[Dict]:
        try:
            if not self.archetypes_path.exists():
                logger.error(f"Archetypes file not found: {self.archetypes_path}")
                return []
            with open(self.archetypes_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading archetypes: {e}")
            return []

    def detect(self, visual_analysis: Dict) -> Dict:
        """
        Analyse les signaux visuels (visual_hints, structural_roles, texte)
        pour identifier l'archétype fonctionnel dominant.
        """
        elements = visual_analysis.get("elements", [])
        regions = visual_analysis.get("regions", [])
        
        # 1. Collecte des signaux
        hints = [e.get("visual_hint", "").lower() for e in elements if e.get("visual_hint")]
        roles = [r.get("structural_role", "").lower() for r in visual_analysis.get("regions", []) if r.get("structural_role")]
        # Ajout des IDs et Noms (Classes) pour pallier le manque de metadata af
        ids = [e.get("id", "").lower() for e in elements if e.get("id")]
        names = [e.get("name", "").lower() for e in elements if e.get("name")]
        texts = " ".join([e.get("text_content", "").lower() for e in elements if e.get("text_content")]).lower()
        
        best_match = None
        max_score = -1

        # 2. Scoring heuristique (Déterministe)
        for arch in self.archetypes:
            score = 0
            triggers = arch.get("visual_triggers", [])
            
            # Match triggers against hints, roles, ids, names and texts
            for trigger in triggers:
                t = trigger.lower()
                matched = False
                # Score pondéré
                if any(t in h for h in hints): score += 3; matched = True
                if any(t in r for r in roles): score += 3; matched = True
                if any(t in i for i in ids): score += 2; matched = True
                if any(t in n for n in names): score += 1; matched = True
                if t in texts: score += 1; matched = True
                
                # Cas spécial : mots composés (ex: "sidebar tree" -> "sidebar" AND "tree")
                if " " in t:
                    sub_t = t.split()
                    if all(st in texts or any(st in i for i in ids) for st in sub_t):
                        score += 2; matched = True
                
            if score > max_score:
                max_score = score
                best_match = arch

        # 3. Seuil de confiance
        confidence = 0
        if max_score > 0:
            # Normalisation simplifiée
            confidence = min(0.95, 0.3 + (max_score / 10))
        
        if not best_match or max_score < 2:
            return {
                "archetype_id": "unknown",
                "label": "Interface Personnalisée / Mixte",
                "confidence": 0.2,
                "artifact_type": "layout_component",
                "dev_brief": "Structure non-standard ou hybride détectée. Focus sur l'organisation spatiale libre."
            }

        # Retourne une copie enrichie avec la confiance
        result = best_match.copy()
        result["confidence"] = round(confidence, 2)
        
        logger.info(f"🎯 Archetype detected: {result['archetype_id']} (score: {max_score}, confidence: {result['confidence']})")
        return result

if __name__ == "__main__":
    # Test
    detector = ArchetypeDetector()
    test_analysis = {
      "elements": [{"visual_hint": "tree-view"}, {"visual_hint": "code-editor"}],
      "regions": [{"structural_role": "sidebar"}]
    }
    print(json.dumps(detector.detect(test_analysis), indent=2))
