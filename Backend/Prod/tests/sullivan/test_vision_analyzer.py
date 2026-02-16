import pytest
import asyncio
from pathlib import Path
import json
import base64
from unittest.mock import AsyncMock, patch

from Backend.Prod.sullivan.vision_analyzer import analyze_design_png, parse_gemini_vision_response
from Backend.Prod.models.gemini_client import GenerationResult


# Create a dummy PNG file for testing
@pytest.fixture(scope="module")
def dummy_png_file(tmp_path_factory):
    """Creates a dummy PNG file for testing."""
    img_path = tmp_path_factory.mktemp("data") / "dummy.png"
    # Create a very simple 1x1 black PNG (minimal data)
    png_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    )
    with open(img_path, "wb") as f:
        f.write(png_data)
    return img_path

@pytest.mark.asyncio
async def test_analyze_design_png_success(dummy_png_file, tmp_path):
    """Test successful analysis and report saving."""
    session_id = "test_session_123"
    expected_report = {
        "metadata": {"analyzed_at": "2024-07-30T12:00:00Z", "model": "gemini-2.0-flash-exp", "source_png": "design.png"},
        "style": {"colors": {"bg": "#000000"}},
        "layout": {"zones": [{"id": "zone_header"}]}
    }
    mock_response_text = f"""```json
{json.dumps(expected_report, indent=2)}
```"""

    with patch('Backend.Prod.sullivan.vision_analyzer.GeminiClient') as MockGeminiClient:
        mock_instance = MockGeminiClient.return_value
        mock_instance.generate_with_image = AsyncMock(return_value=GenerationResult(
            success=True,
            code=mock_response_text,
            tokens_used=100,
            input_tokens=50,
            output_tokens=50,
            cost_usd=0.01,
            execution_time_ms=500.0,
        ))
        report = await analyze_design_png(str(dummy_png_file), session_id)

    assert report == expected_report
    # Verify report was saved
    report_path = Path(f"~/.aetherflow/sessions/{session_id}/visual_report.json").expanduser()
    assert report_path.exists()
    with open(report_path, "r") as f:
        saved_report = json.load(f)
    assert saved_report == expected_report
    
    # Verify generate_with_image was called
    mock_instance.generate_with_image.assert_awaited_once()

@pytest.mark.asyncio
async def test_analyze_design_png_missing_png(tmp_path):
    """Test error handling for missing PNG file."""
    session_id = "test_session_456"
    missing_png_path = tmp_path / "non_existent.png"

    with pytest.raises(FileNotFoundError):
        await analyze_design_png(str(missing_png_path), session_id)

def test_parse_gemini_vision_response_valid_json_block():
    """Test parsing a response with a JSON block."""
    json_data = {"key": "value", "number": 123}
    response_text = f"""Some introductory text.
```json
{json.dumps(json_data, indent=2)}
```
Some concluding remarks."""
    parsed_json = parse_gemini_vision_response(response_text)
    assert parsed_json == json_data

def test_parse_gemini_vision_response_direct_json():
    """Test parsing a response that is directly JSON."""
    json_data = {"another_key": "another_value"}
    response_text = json.dumps(json_data)
    parsed_json = parse_gemini_vision_response(response_text)
    assert parsed_json == json_data

def test_parse_gemini_vision_response_invalid_json():
    """Test parsing an invalid JSON response."""
    response_text = "This is not valid JSON."
    parsed_json = parse_gemini_vision_response(response_text)
    assert "error" in parsed_json
    assert "JSON parsing failed" in parsed_json["error"]

@pytest.mark.asyncio
async def test_analyze_design_png_gemini_api_failure(dummy_png_file, tmp_path):
    """Test error handling when Gemini API call fails."""
    session_id = "test_session_789"
    
    with patch('Backend.Prod.sullivan.vision_analyzer.GeminiClient') as MockGeminiClient:
        mock_instance = MockGeminiClient.return_value
        mock_instance.generate_with_image = AsyncMock(return_value=GenerationResult(
            success=False,
            code="",
            tokens_used=0,
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            execution_time_ms=0.0,
            error="API call failed for some reason"
        ))
        with pytest.raises(Exception, match="Gemini Vision API call failed"):
            await analyze_design_png(str(dummy_png_file), session_id)