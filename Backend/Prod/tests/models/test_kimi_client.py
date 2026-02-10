import pytest
from Backend.Prod.models.kimi_client import KimiClient
from Backend.Prod.config.settings import settings
import os


@pytest.mark.asyncio
async def test_kimi_hf_validation():
    """Test KIMI validation via HuggingFace."""
    # Ensure HF_TOKEN is set for the test
    if "HF_TOKEN" not in os.environ:
        pytest.skip("HF_TOKEN environment variable not configured for this test.")

    client = KimiClient(use_hf=True)

    # Skip si pas de HF_TOKEN (via client.available)
    if not client.available:
        pytest.skip("HF_TOKEN not configured or client not available.")

    # A simple, valid Python output for validation
    output_code = "def hello_world():\\n    print('Hello, world!')"
    expected_lang = "python"

    result = await client.validate_output(
        output=output_code,
        expected_language=expected_lang
    )

    assert result["valid"] == True, f"KIMI HF validation failed: {result.get('reason')}"
    assert result["detected_issue"] is None, f"KIMI HF detected an issue: {result.get('detected_issue')}"

@pytest.mark.asyncio
@pytest.mark.skip(reason="Depends on KimiClient update from MISSION_GEMINI_KIMI_HF_CLIENT.md")
async def test_kimi_moonshot_fallback_validation():
    """Test KIMI validation via Moonshot fallback."""
    # Ensure KIMI_KEY is set for the test
    if "KIMI_KEY" not in os.environ:
        pytest.skip("KIMI_KEY environment variable not configured for Moonshot fallback test.")
    
    # Temporarily set use_kimi_hf to False for this test
    original_use_kimi_hf = settings.use_kimi_hf
    settings.use_kimi_hf = False
    
    client = KimiClient(use_hf=False) # Explicitly use Moonshot

    # Skip si pas de KIMI_KEY (via client.available)
    if not client.available:
        settings.use_kimi_hf = original_use_kimi_hf # Restore setting
        pytest.skip("KIMI_KEY not configured or client not available for Moonshot.")

    # A simple, valid Python output for validation
    output_code = "def greet(name):\\n    return f'Hello, {name}!'\\n"
    expected_lang = "python"

    result = await client.validate_output(
        output=output_code,
        expected_language=expected_lang
    )

    assert result["valid"] == True, f"KIMI Moonshot validation failed: {result.get('reason')}"
    assert result["detected_issue"] is None, f"KIMI Moonshot detected an issue: {result.get('detected_issue')}"
    
    settings.use_kimi_hf = original_use_kimi_hf # Restore setting