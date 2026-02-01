"""Test du fallback automatique Groq -> Gemini en cas de rate limit."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from Backend.Prod.models.agent_router import AgentRouter
from Backend.Prod.models.plan_reader import Step
from Backend.Prod.models.deepseek_client import GenerationResult


@pytest.mark.asyncio
async def test_groq_rate_limit_fallback_to_gemini():
    """Test que le fallback vers Gemini fonctionne quand Groq retourne 429."""
    
    # Créer un step de test
    step = Step(
        id="step_1",
        description="Test step",
        type="code_generation",
        complexity=0.5,
        estimated_tokens=100,
        dependencies=[],
        validation_criteria=[],
        context={"language": "python"}
    )
    
    # Mock des clients
    mock_groq_client = AsyncMock()
    mock_gemini_client = AsyncMock()
    
    # Groq retourne une erreur 429 (rate limit)
    mock_groq_client.generate = AsyncMock(return_value=GenerationResult(
        success=False,
        code="",
        tokens_used=0,
        input_tokens=0,
        output_tokens=0,
        cost_usd=0.0,
        execution_time_ms=100,
        error="HTTP 429: Rate limit exceeded",
        provider="groq"
    ))
    
    # Gemini réussit
    mock_gemini_client.generate = AsyncMock(return_value=GenerationResult(
        success=True,
        code="def test(): pass",
        tokens_used=50,
        input_tokens=30,
        output_tokens=20,
        cost_usd=0.0001,
        execution_time_ms=200,
        provider="gemini"
    ))
    
    # Créer le router avec les mocks
    with patch('Backend.Prod.models.agent_router.GroqClient') as MockGroqClient, \
         patch('Backend.Prod.models.agent_router.GeminiClient') as MockGeminiClient:
        
        MockGroqClient.return_value = mock_groq_client
        MockGeminiClient.return_value = mock_gemini_client
        
        router = AgentRouter(execution_mode="FAST")
        router._clients = {
            "groq": mock_groq_client,
            "gemini": mock_gemini_client
        }
        
        # Exécuter le step
        result = await router.execute_step(step, context="test")
        
        # Vérifier que Groq a été appelé
        assert mock_groq_client.generate.called
        
        # Vérifier que Gemini a été appelé en fallback
        assert mock_gemini_client.generate.called, "Gemini should be called as fallback"
        
        # Vérifier que le résultat vient de Gemini
        assert result.success, "Result should be successful from Gemini fallback"
        assert result.output == "def test(): pass"
        assert result.cost_usd == 0.0001


@pytest.mark.asyncio
async def test_groq_rate_limit_fallback_to_deepseek():
    """Test que le fallback vers DeepSeek fonctionne quand Groq retourne 429 et Gemini n'est pas disponible."""
    
    step = Step(
        id="step_1",
        description="Test step",
        type="code_generation",
        complexity=0.5,
        estimated_tokens=100,
        dependencies=[],
        validation_criteria=[],
        context={"language": "python"}
    )
    
    # Mock des clients
    mock_groq_client = AsyncMock()
    mock_deepseek_client = AsyncMock()
    
    # Groq retourne une erreur 429
    mock_groq_client.generate = AsyncMock(return_value=GenerationResult(
        success=False,
        code="",
        tokens_used=0,
        input_tokens=0,
        output_tokens=0,
        cost_usd=0.0,
        execution_time_ms=100,
        error="HTTP 429: Rate limit exceeded",
        provider="groq"
    ))
    
    # DeepSeek réussit
    mock_deepseek_client.generate = AsyncMock(return_value=GenerationResult(
        success=True,
        code="def test(): return 42",
        tokens_used=60,
        input_tokens=40,
        output_tokens=20,
        cost_usd=0.0002,
        execution_time_ms=300,
        provider="deepseek"
    ))
    
    with patch('Backend.Prod.models.agent_router.GroqClient') as MockGroqClient, \
         patch('Backend.Prod.models.agent_router.DeepSeekClient') as MockDeepSeekClient:
        
        MockGroqClient.return_value = mock_groq_client
        MockDeepSeekClient.return_value = mock_deepseek_client
        
        router = AgentRouter(execution_mode="FAST")
        router._clients = {
            "groq": mock_groq_client,
            "deepseek": mock_deepseek_client
        }
        
        # Exécuter le step
        result = await router.execute_step(step, context="test")
        
        # Vérifier que Groq a été appelé
        assert mock_groq_client.generate.called
        
        # Vérifier que DeepSeek a été appelé en fallback
        assert mock_deepseek_client.generate.called, "DeepSeek should be called as fallback"
        
        # Vérifier que le résultat vient de DeepSeek
        assert result.success, "Result should be successful from DeepSeek fallback"
        assert result.output == "def test(): return 42"


@pytest.mark.asyncio
async def test_groq_success_no_fallback():
    """Test que le fallback n'est pas déclenché quand Groq réussit."""
    
    step = Step(
        id="step_1",
        description="Test step",
        type="code_generation",
        complexity=0.5,
        estimated_tokens=100,
        dependencies=[],
        validation_criteria=[],
        context={"language": "python"}
    )
    
    # Mock des clients
    mock_groq_client = AsyncMock()
    mock_gemini_client = AsyncMock()
    
    # Groq réussit
    mock_groq_client.generate = AsyncMock(return_value=GenerationResult(
        success=True,
        code="def test(): pass",
        tokens_used=50,
        input_tokens=30,
        output_tokens=20,
        cost_usd=0.0001,
        execution_time_ms=100,
        provider="groq"
    ))
    
    with patch('Backend.Prod.models.agent_router.GroqClient') as MockGroqClient, \
         patch('Backend.Prod.models.agent_router.GeminiClient') as MockGeminiClient:
        
        MockGroqClient.return_value = mock_groq_client
        MockGeminiClient.return_value = mock_gemini_client
        
        router = AgentRouter(execution_mode="FAST")
        router._clients = {
            "groq": mock_groq_client,
            "gemini": mock_gemini_client
        }
        
        # Exécuter le step
        result = await router.execute_step(step, context="test")
        
        # Vérifier que Groq a été appelé
        assert mock_groq_client.generate.called
        
        # Vérifier que Gemini n'a PAS été appelé
        assert not mock_gemini_client.generate.called, "Gemini should not be called when Groq succeeds"
        
        # Vérifier que le résultat vient de Groq
        assert result.success
        assert result.output == "def test(): pass"
