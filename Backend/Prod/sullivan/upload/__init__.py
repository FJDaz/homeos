"""
Sullivan Upload - Mode upload pour images compatibles Gemini.

Pré-traite les images (resize, compression) avant envoi à Gemini Vision
pour éviter les dépassements de limite (inline base64 ~20MB).
"""

from .image_preprocessor import ImagePreprocessor, preprocess_for_gemini

__all__ = ["ImagePreprocessor", "preprocess_for_gemini"]
