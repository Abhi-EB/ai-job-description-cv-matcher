# AI Job Description and CV Matcher

A Generative AI project that compares a candidate's CV with a job description using Google's Gemini API.

## Features
- PDF CV text extraction
- Job description validation
- Gemini-powered CV and JD comparison
- Matching and missing skills analysis
- Experience alignment and improvement recommendations
- TXT and PDF report downloads
- Automatic retries for temporary Gemini API errors
- Streamlit web interface
- Nine automated pytest tests

## Technology Stack
- Python
- Google Gemini API (google-genai)
- PyPDF
- Streamlit
- ReportLab
- pytest
- Google Colab
- GitHub

## Project Structure
```text
ai-job-description-cv-matcher/
|-- app.py
|-- streamlit_app.py
|-- report_utils.py
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
Never hardcode API keys or upload them to GitHub.

### Google Colab
1. Open the Colab Secrets panel.
2. Add a secret named GEMINI_API_KEY.
3. Store your Gemini API key as its value.
4. Enable notebook access for the secret.

### Streamlit Community Cloud
Add this in the app's Secrets settings:
```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```
Replace the placeholder with your actual key. Never commit it to GitHub.
The application reads the key from Colab Secrets, Streamlit Secrets, or an environment variable.

## Run the Streamlit Application
```bash
streamlit run streamlit_app.py
```

The application provides PDF CV upload, job description input, Gemini analysis, skills insights, recommendations, and TXT/PDF downloads.

## Run Tests
```bash
python -m pytest tests/test_cv_matcher.py -v
```
Nine automated tests cover validation, prompt creation, PDF file errors and Gemini retry behaviour.

## Deployment
1. Push the project files to GitHub.
2. Sign in to Streamlit Community Cloud.
3. Create a new app and connect the GitHub repository.
4. Select streamlit_app.py as the main file.
5. Configure GEMINI_API_KEY in the app's Secrets settings.
6. Deploy the application.

Never upload CVs, generated reports, API keys or other private information to the public repository.

## Limitations
- AI match scores are estimates, not hiring probabilities.
- Results depend on CV and job description quality.
- Recommendations must be checked against genuine experience.
- Scanned PDFs may require OCR.
- This is a learning prototype, not a production recruitment platform.

## Privacy and Security
- Never publish real CVs, reports or API credentials.
- Private inputs and generated reports are excluded through .gitignore.
- API credentials are read from secure configuration rather than hardcoded in source code.

## Project Status
- Core CV analysis implemented.
- Gemini API integration and retry handling implemented.
- Streamlit web interface implemented.
- TXT and PDF report generation implemented.
- Nine automated tests passed.

Created as a practical Generative AI learning project.
