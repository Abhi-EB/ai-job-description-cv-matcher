# AI Job Description and CV Matcher

A practical Generative AI project that compares a candidate's CV with a job description using Google's Gemini API.

## Features
- PDF CV text extraction
- Job description validation
- Gemini-powered CV and JD comparison
- Matching and missing skills analysis
- Experience alignment and improvement recommendations
- TXT and PDF report generation
- Automatic retries for temporary Gemini API errors
- Nine automated pytest tests

## Technology Stack
- Python
- Google Gemini API (google-genai)
- PyPDF
- ReportLab
- pytest
- Google Colab

## Project Structure
```text
ai-job-description-cv-matcher/
|-- app.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|-- inputs/
|-- outputs/
|-- logs/
|-- tests/
    |-- test_cv_matcher.py
```

## Installation
```bash
pip install -r requirements.txt
```

## Gemini API Configuration
Store your Gemini API key in Google Colab Secrets as GEMINI_API_KEY.
Never hardcode API keys or upload them to GitHub.

Example:
```python
from google.colab import userdata
from google import genai
api_key = userdata.get('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)
MODEL_NAME = 'gemini-3.6-flash'
```

Use a model currently available to your Gemini API account.

## Run Tests
```bash
python -m pytest tests/test_cv_matcher.py -v
```

The nine tests cover validation, prompt creation, PDF file errors and Gemini retry behaviour.

## Limitations
- AI match scores are estimates, not hiring probabilities.
- Results depend on CV and job description quality.
- Recommendations must be checked against genuine experience.
- Scanned PDFs may require OCR.
- This is a learning prototype, not a production recruitment platform.

## Privacy and Security
- Never publish real CVs, reports or API credentials.
- Private inputs and generated reports are excluded through .gitignore.

## Project Status
Core CV analysis, retry handling and automated tests are implemented.
Report generation was developed in the accompanying Colab notebook.

Created as a practical Generative AI learning project.
