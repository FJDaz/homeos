"""
VisionCache - Cache pour analyses Gemini Vision (DesignAnalyzer, etc.)

Objectif : Éviter les appels répétés à Gemini Vision pour les mêmes images.
Clé de cache : hash perceptuel de l'image (pas le hash exact, pour tolérer compression légère)
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from loguru import logger


class VisionCache:
    """
    Cache LRU pour résultats d'analyse d'images.
    Stockage : fichier JSON local avec TTL.
    """
    
    DEFAULT_TTL_HOURS = 24  # Cache valide 24h
    MAX_CACHE_SIZE_MB = 100  # Limite taille cache
    
    def __init__(self, cache_dir: Optional[Path] = None, ttl_hours: int = DEFAULT_TTL_HOURS):
        """
        Args:
            cache_dir: Répertoire de cache (défaut: ~/.aetherflow/vision_cache/)
            ttl_hours: Durée de vie du cache en heures
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".aetherflow" / "vision_cache"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = ttl_hours
        
        logger.info(f"VisionCache initialized: {self.cache_dir} (TTL: {ttl_hours}h)")
    
    def _compute_hash(self, image_bytes: bytes) -> str:
        """
        Calcule un hash de l'image pour la clé de cache.
        Utilise les premiers/derniers KB pour tolérer les métadonnées modifiées.
        """
        # Hash des premiers 8KB + derniers 8KB + taille totale
        head = image_bytes[:8192]
        tail = image_bytes[-8192:] if len(image_bytes) > 8192 else b""
        size = str(len(image_bytes)).encode()
        
        hasher = hashlib.blake2b(digest_size=16)
        hasher.update(head)
        hasher.update(tail)
        hasher.update(size)
        return hasher.hexdigest()
    
    def _get_cache_path(self, image_hash: str) -> Path:
        """Chemin du fichier de cache pour un hash donné."""
        # Structure: cache_dir/AB/CD/ABCDEF...json
        return self.cache_dir / image_hash[:2] / image_hash[2:4] / f"{image_hash}.json"
    
    def get(self, image_bytes: bytes) -> Optional[Dict[str, Any]]:
        """
        Récupère un résultat du cache s'il existe et est valide.
        
        Args:
            image_bytes: Bytes de l'image
            
        Returns:
            Résultat caché ou None
        """
        image_hash = self._compute_hash(image_bytes)
        cache_path = self._get_cache_path(image_hash)
        
        if not cache_path.exists():
            return None
        
        try:
            cache_data = json.loads(cache_path.read_text())
            cached_at = datetime.fromisoformat(cache_data["cached_at"])
            
            # Vérifier TTL
            if datetime.now() - cached_at > timedelta(hours=self.ttl_hours):
                logger.debug(f"[VisionCache] Expired: {image_hash[:16]}...")
                cache_path.unlink(missing_ok=True)
                return None
            
            logger.info(f"[VisionCache] HIT: {image_hash[:16]}... (age: {datetime.now() - cached_at})")
            return cache_data["result"]
            
        except Exception as e:
            logger.warning(f"[VisionCache] Error reading cache: {e}")
            return None
    
    def set(self, image_bytes: bytes, result: Dict[str, Any]) -> None:
        """
        Stocke un résultat dans le cache.
        
        Args:
            image_bytes: Bytes de l'image
            result: Résultat à cacher
        """
        image_hash = self._compute_hash(image_bytes)
        cache_path = self._get_cache_path(image_hash)
        
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            cache_data = {
                "cached_at": datetime.now().isoformat(),
                "image_hash": image_hash,
                "image_size_bytes": len(image_bytes),
                "result": result,
            }
            
            cache_path.write_text(json.dumps(cache_data, indent=2))
            logger.info(f"[VisionCache] STORED: {image_hash[:16]}...")
            
            # Cleanup périodique (1 chance sur 10)
            import random
            if random.random() < 0.1:
                self._cleanup_old_entries()
                
        except Exception as e:
            logger.warning(f"[VisionCache] Error writing cache: {e}")
    
    def _cleanup_old_entries(self) -> None:
        """Nettoie les entrées expirées et limite la taille du cache."""
        try:
            total_size = 0
            entries = []
            
            for cache_file in self.cache_dir.rglob("*.json"):
                try:
                    stat = cache_file.stat()
                    entries.append((cache_file, stat.st_mtime, stat.st_size))
                    total_size += stat.st_size
                except:
                    pass
            
            # Supprimer les expirés
            cutoff_time = time.time() - (self.ttl_hours * 3600)
            for cache_file, mtime, size in entries:
                if mtime < cutoff_time:
                    cache_file.unlink(missing_ok=True)
                    total_size -= size
            
            # Si toujours trop gros, supprimer les plus vieux
            max_bytes = self.MAX_CACHE_SIZE_MB * 1024 * 1024
            if total_size > max_bytes:
                entries.sort(key=lambda x: x[1])  # Par date modif
                for cache_file, _, size in entries:
                    if total_size <= max_bytes:
                        break
                    cache_file.unlink(missing_ok=True)
                    total_size -= size
                    
        except Exception as e:
            logger.warning(f"[VisionCache] Cleanup error: {e}")


# Instance globale pour réutilisation
_vision_cache: Optional[VisionCache] = None


def get_vision_cache() -> VisionCache:
    """Retourne l'instance globale du cache."""
    global _vision_cache
    if _vision_cache is None:
        _vision_cache = VisionCache()
    return _vision_cache


def clear_vision_cache() -> None:
    """Vide le cache (utile pour tests)."""
    global _vision_cache
    if _vision_cache is not None:
        import shutil
        shutil.rmtree(_vision_cache.cache_dir, ignore_errors=True)
        _vision_cache = None


__all__ = ["VisionCache", "get_vision_cache", "clear_vision_cache"]
