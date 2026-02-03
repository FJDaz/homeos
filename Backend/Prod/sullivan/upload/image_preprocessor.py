"""
ImagePreprocessor - Réduit la taille des images pour Gemini Vision.

OPTIMISATION LATENCE : Réduction agressive pour Gemini Vision
- Gemini travaille en 512x512 ou 1024x1024 interne
- Au-delà = latence sans gain de qualité
- Cible : <500KB, <1024px, qualité 70%

Base64 ajoute ~33% → image brute max ~375KB pour rester sous 500KB.
"""

import io
from pathlib import Path
from typing import Tuple, Optional
from loguru import logger

# === CONFIGURATION LATENCE OPTIMISÉE ===
# Ancienne config (lente) : 3MB, 1920px, qualité 85%
# Nouvelle config (rapide) : 500KB, 1024px, qualité 70%
TARGET_MAX_BYTES = 500 * 1024  # 500 KB (was 3MB)
MAX_DIMENSION = 1024  # px côté long (was 1920)
JPEG_QUALITY = 70  # was 85

# Timeout pour analyses Gemini (en secondes)
GEMINI_TIMEOUT_SECONDS = 15


def preprocess_for_gemini(
    image_path: Path,
    target_max_bytes: int = TARGET_MAX_BYTES,
    max_dimension: int = MAX_DIMENSION,
) -> Tuple[bytes, str]:
    """
    Pré-traite une image pour l'envoi à Gemini Vision (version rapide).

    Args:
        image_path: Chemin vers l'image (PNG, JPG, JPEG, WEBP)
        target_max_bytes: Taille max cible en bytes (défaut 500KB)
        max_dimension: Dimension max côté long en px (défaut 1024)

    Returns:
        (bytes, mime_type) - Données prêtes pour base64.b64encode()
    """
    preprocessor = ImagePreprocessor(
        target_max_bytes=target_max_bytes,
        max_dimension=max_dimension,
    )
    return preprocessor.process(image_path)


def preprocess_bytes_for_gemini(
    image_bytes: bytes,
    target_max_bytes: int = TARGET_MAX_BYTES,
    max_dimension: int = MAX_DIMENSION,
) -> Tuple[bytes, str]:
    """
    Pré-traite des bytes d'image pour Gemini Vision.

    Args:
        image_bytes: Bytes de l'image
        target_max_bytes: Taille max cible en bytes (défaut 500KB)
        max_dimension: Dimension max côté long en px (défaut 1024)

    Returns:
        (bytes, mime_type) - "image/jpeg"
    """
    preprocessor = ImagePreprocessor(
        target_max_bytes=target_max_bytes,
        max_dimension=max_dimension,
    )
    return preprocessor.process_bytes(image_bytes)


class ImagePreprocessor:
    """
    Pré-traite les images pour rester sous les limites Gemini (version latence optimisée).
    """

    def __init__(
        self,
        target_max_bytes: int = TARGET_MAX_BYTES,
        max_dimension: int = MAX_DIMENSION,
        jpeg_quality: int = JPEG_QUALITY,
    ):
        self.target_max_bytes = target_max_bytes
        self.max_dimension = max_dimension
        self.jpeg_quality = jpeg_quality

    def process(self, image_path: Path) -> Tuple[bytes, str]:
        """
        Traite l'image : resize si trop grande, compress si nécessaire.

        Returns:
            (bytes, mime_type) - "image/jpeg"
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        try:
            from PIL import Image
        except ImportError:
            logger.warning("Pillow not installed, skipping image preprocessing")
            return image_path.read_bytes(), self._mime_from_path(image_path)

        with Image.open(image_path) as img:
            return self._process_image(img)

    def process_bytes(self, image_bytes: bytes) -> Tuple[bytes, str]:
        """
        Traite des bytes d'image.

        Returns:
            (bytes, mime_type) - "image/jpeg"
        """
        try:
            from PIL import Image
        except ImportError:
            logger.warning("Pillow not installed, skipping image preprocessing")
            return image_bytes, "image/jpeg"

        with Image.open(io.BytesIO(image_bytes)) as img:
            return self._process_image(img)

    def _process_image(self, img) -> Tuple[bytes, str]:
        """Traite une image PIL ouverte."""
        from PIL import Image

        # Convertir en RGB si nécessaire (PNG RGBA, etc.)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Redimensionner si trop grande
        w, h = img.size
        original_size = f"{w}x{h}"
        
        if max(w, h) > self.max_dimension:
            ratio = self.max_dimension / max(w, h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            logger.info(f"[LATENCE] Resized {original_size} -> {new_w}x{new_h} (max {self.max_dimension}px)")

        # Exporter en JPEG avec qualité réduite
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=self.jpeg_quality, optimize=True)
        data = buffer.getvalue()

        # Si encore trop gros, réduire agressivement
        quality = self.jpeg_quality
        while len(data) > self.target_max_bytes and quality > 40:
            quality -= 10
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality, optimize=True)
            data = buffer.getvalue()
            logger.info(f"[LATENCE] Reduced quality to {quality}, size {len(data) / 1024:.1f}KB")

        final_size_kb = len(data) / 1024
        if final_size_kb > (self.target_max_bytes / 1024):
            logger.warning(
                f"[LATENCE] Image still {final_size_kb:.1f}KB after aggressive compression "
                f"(target {self.target_max_bytes / 1024:.0f}KB)"
            )
        else:
            logger.info(f"[LATENCE] Final image: {final_size_kb:.1f}KB, {img.size[0]}x{img.size[1]}px")

        return data, "image/jpeg"

    def _mime_from_path(self, path: Path) -> str:
        ext = path.suffix.lower()
        return {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }.get(ext, "image/png")


# === UTILITAIRES POUR CLIENT-SIDE PREPROCESSING ===

def get_recommended_upload_limits() -> dict:
    """
    Retourne les limites recommandées pour l'upload côté client.
    À utiliser dans l'API pour informer le frontend.
    """
    return {
        "max_dimension": MAX_DIMENSION,
        "max_file_size_bytes": TARGET_MAX_BYTES,
        "recommended_format": "JPEG",
        "recommended_quality": JPEG_QUALITY,
        "gemini_timeout_seconds": GEMINI_TIMEOUT_SECONDS,
        "estimated_processing_time": "2-5s",  # Pour une image <500KB
    }


def validate_image_before_upload(image_path: Path) -> Tuple[bool, str]:
    """
    Valide si une image respecte les limites avant upload.
    
    Returns:
        (is_valid, message)
    """
    if not image_path.exists():
        return False, f"Image non trouvée: {image_path}"
    
    size_bytes = image_path.stat().st_size
    if size_bytes > TARGET_MAX_BYTES * 4:  # 2MB avant preprocessing
        return False, (
            f"Image trop grande ({size_bytes / 1024 / 1024:.1f}MB). "
            f"Maximum recommandé: 2MB (sera compressé à {TARGET_MAX_BYTES / 1024:.0f}KB)."
        )
    
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            w, h = img.size
            if max(w, h) > MAX_DIMENSION * 2:  # 2048px avant resize
                return False, (
                    f"Image trop grande ({w}x{h}). "
                    f"Maximum recommandé: {MAX_DIMENSION * 2}px (sera redimensionnée à {MAX_DIMENSION}px)."
                )
    except Exception as e:
        return False, f"Impossible d'analyser l'image: {e}"
    
    return True, "OK"


# Pour compatibilité avec code existant
__all__ = [
    "preprocess_for_gemini",
    "preprocess_bytes_for_gemini",
    "ImagePreprocessor",
    "TARGET_MAX_BYTES",
    "MAX_DIMENSION",
    "JPEG_QUALITY",
    "GEMINI_TIMEOUT_SECONDS",
    "get_recommended_upload_limits",
    "validate_image_before_upload",
]
