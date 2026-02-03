"""
Tests unitaires pour les préférences utilisateur dans ConversationMemory.
"""
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from memory import SessionContext, ConversationMemory, create_session_id


class TestSessionContextPreferences(unittest.TestCase):
    """Tests pour les nouveaux champs de préférences dans SessionContext."""
    
    def test_default_preferences_none(self):
        """Test que les préférences sont None par défaut."""
        ctx = SessionContext(
            session_id="test_123",
            user_id="user_456"
        )
        
        self.assertIsNone(ctx.theme_preference)
        self.assertIsNone(ctx.language_preference)
    
    def test_preferences_set(self):
        """Test définition des préférences."""
        ctx = SessionContext(
            session_id="test_123",
            user_id="user_456",
            theme_preference="dark",
            language_preference="en"
        )
        
        self.assertEqual(ctx.theme_preference, "dark")
        self.assertEqual(ctx.language_preference, "en")
    
    def test_serialization_with_preferences(self):
        """Test sérialisation/désérialisation avec préférences."""
        ctx = SessionContext(
            session_id="test_123",
            user_id="user_456",
            theme_preference="light",
            language_preference="es"
        )
        
        # Sérialisation
        data = ctx.to_dict()
        
        # Vérification
        self.assertEqual(data["theme_preference"], "light")
        self.assertEqual(data["language_preference"], "es")
        
        # Désérialisation
        restored = SessionContext.from_dict(data)
        
        self.assertEqual(restored.theme_preference, "light")
        self.assertEqual(restored.language_preference, "es")


class TestConversationMemoryPreferences(unittest.TestCase):
    """Tests pour les méthodes de gestion des préférences."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.session_id = create_session_id("test_user")
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_set_and_get_theme(self):
        """Test définition et récupération du thème."""
        memory = ConversationMemory(
            session_id=self.session_id,
            storage_dir=Path(self.temp_dir)
        )
        
        # Définition
        result = memory.set_theme("dark")
        self.assertTrue(result)
        
        # Récupération
        theme = memory.get_theme()
        self.assertEqual(theme, "dark")
    
    def test_set_invalid_theme(self):
        """Test rejet d'un thème invalide."""
        memory = ConversationMemory(
            session_id=self.session_id,
            storage_dir=Path(self.temp_dir)
        )
        
        result = memory.set_theme("invalid_theme")
        self.assertFalse(result)
        
        # Le thème par défaut doit rester
        theme = memory.get_theme()
        self.assertEqual(theme, "system")
    
    def test_get_theme_default(self):
        """Test thème par défaut (system)."""
        memory = ConversationMemory(
            session_id=self.session_id,
            storage_dir=Path(self.temp_dir)
        )
        
        theme = memory.get_theme()
        self.assertEqual(theme, "system")
    
    def test_set_and_get_language(self):
        """Test définition et récupération de la langue."""
        memory = ConversationMemory(
            session_id=self.session_id,
            storage_dir=Path(self.temp_dir)
        )
        
        # Définition
        result = memory.set_language("en")
        self.assertTrue(result)
        
        # Récupération
        lang = memory.get_language()
        self.assertEqual(lang, "en")
    
    def test_set_invalid_language(self):
        """Test rejet d'une langue invalide."""
        memory = ConversationMemory(
            session_id=self.session_id,
            storage_dir=Path(self.temp_dir)
        )
        
        result = memory.set_language("invalid_lang")
        self.assertFalse(result)
        
        # La langue par défaut doit rester
        lang = memory.get_language()
        self.assertEqual(lang, "fr")
    
    def test_get_language_default(self):
        """Test langue par défaut (fr)."""
        memory = ConversationMemory(
            session_id=self.session_id,
            storage_dir=Path(self.temp_dir)
        )
        
        lang = memory.get_language()
        self.assertEqual(lang, "fr")
    
    def test_get_preferences(self):
        """Test récupération de toutes les préférences."""
        memory = ConversationMemory(
            session_id=self.session_id,
            storage_dir=Path(self.temp_dir)
        )
        
        # Définir des préférences
        memory.set_theme("dark")
        memory.set_language("en")
        memory.update_context(preferred_style="brutalist", mode="expert")
        
        # Récupérer
        prefs = memory.get_preferences()
        
        self.assertEqual(prefs["theme"], "dark")
        self.assertEqual(prefs["language"], "en")
        self.assertEqual(prefs["style"], "brutalist")
        self.assertEqual(prefs["mode"], "expert")
    
    def test_persistence_across_instances(self):
        """Test persistance des préférences entre instances."""
        # Première instance
        memory1 = ConversationMemory(
            session_id=self.session_id,
            storage_dir=Path(self.temp_dir)
        )
        memory1.set_theme("light")
        memory1.set_language("de")
        
        # Seconde instance (recharge la session)
        memory2 = ConversationMemory(
            session_id=self.session_id,
            storage_dir=Path(self.temp_dir)
        )
        
        # Vérifier que les préférences sont conservées
        self.assertEqual(memory2.get_theme(), "light")
        self.assertEqual(memory2.get_language(), "de")


class TestValidLanguagesAndThemes(unittest.TestCase):
    """Tests pour les valeurs valides."""
    
    def test_valid_themes(self):
        """Test que tous les thèmes valides sont acceptés."""
        temp_dir = tempfile.mkdtemp()
        memory = ConversationMemory(
            session_id="test_themes",
            storage_dir=Path(temp_dir)
        )
        
        valid_themes = ["light", "dark", "system"]
        for theme in valid_themes:
            with self.subTest(theme=theme):
                result = memory.set_theme(theme)
                self.assertTrue(result)
                self.assertEqual(memory.get_theme(), theme)
        
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_valid_languages(self):
        """Test que toutes les langues valides sont acceptées."""
        temp_dir = tempfile.mkdtemp()
        memory = ConversationMemory(
            session_id="test_langs",
            storage_dir=Path(temp_dir)
        )
        
        valid_languages = ["fr", "en", "es", "de", "it"]
        for lang in valid_languages:
            with self.subTest(lang=lang):
                result = memory.set_language(lang)
                self.assertTrue(result)
                self.assertEqual(memory.get_language(), lang)
        
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
