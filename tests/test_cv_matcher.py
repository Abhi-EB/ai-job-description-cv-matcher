from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
import app


def test_validate_job_description():
    jd = (
        "Data Analyst required with Python, SQL, Excel and Power BI. "
        "Must have experience in data analysis and reporting."
    )

    valid, message = app.validate_job_description(jd)

    assert valid is True
    assert message == "Job description is valid."


def test_empty_job_description():
    valid, message = app.validate_job_description("")

    assert valid is False
    assert "empty" in message.lower()


def test_short_job_description():
    valid, message = app.validate_job_description("Data Analyst")

    assert valid is False
    assert "short" in message.lower()


def test_analysis_prompt():
    prompt = app.create_analysis_prompt(
        "Candidate has Python and SQL skills.",
        "Data Analyst with Python and SQL experience required."
    )

    assert "CANDIDATE CV:" in prompt
    assert "JOB DESCRIPTION:" in prompt
    assert "Overall match score" in prompt


def test_missing_cv_file():
    with pytest.raises(FileNotFoundError):
        app.extract_cv_text("inputs/nonexistent_cv.pdf")


def test_invalid_cv_format():
    with pytest.raises(ValueError):
        app.extract_cv_text("inputs/sample_cv.txt")


def test_gemini_success_without_retry():
    client = MagicMock()

    client.models.generate_content.return_value = SimpleNamespace(
        text="Analysis successful"
    )

    result = app.analyse_cv_with_gemini(
        client, "test-model", "test prompt"
    )

    assert result == "Analysis successful"
    assert client.models.generate_content.call_count == 1


def test_gemini_retries_after_503():
    client = MagicMock()

    client.models.generate_content.side_effect = [
        RuntimeError("503 UNAVAILABLE"),
        SimpleNamespace(text="Analysis successful")
    ]

    with patch("time.sleep") as mock_sleep:
        result = app.analyse_cv_with_gemini(
            client, "test-model", "test prompt"
        )

    assert result == "Analysis successful"
    assert client.models.generate_content.call_count == 2
    mock_sleep.assert_called_once_with(2)


def test_gemini_stops_after_three_failed_attempts():
    client = MagicMock()

    client.models.generate_content.side_effect = (
        RuntimeError("503 UNAVAILABLE")
    )

    with patch("time.sleep") as mock_sleep:
        with pytest.raises(RuntimeError, match="503"):
            app.analyse_cv_with_gemini(
                client, "test-model", "test prompt"
            )

    assert client.models.generate_content.call_count == 3
    assert mock_sleep.call_count == 2
