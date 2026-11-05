from pathlib import Path


def extract_cv_text(pdf_path):
    from pypdf import PdfReader

    pdf_path = Path(pdf_path)

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    if not pdf_path.exists():
        raise FileNotFoundError(f"CV file not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))

    extracted_text = []

    for page in reader.pages:
        extracted_text.append(page.extract_text() or "")

    full_text = "\\n".join(extracted_text).strip()

    if not full_text:
        raise ValueError("No readable text found in the PDF.")

    return full_text


def validate_job_description(jd_text):
    if not isinstance(jd_text, str):
        return False, "Job description must be text."

    if not jd_text.strip():
        return False, "Job description cannot be empty."

    if len(jd_text.strip()) < 50:
        return False, "Job description is too short."

    return True, "Job description is valid."


def create_analysis_prompt(cv_text, jd_text):
    return f"""You are an expert recruitment and career analysis assistant.

Compare the candidate CV with the supplied job description.

CANDIDATE CV:
{cv_text}

JOB DESCRIPTION:
{jd_text}

Provide a structured analysis covering:

1. Overall match score out of 100.
2. Matching skills and experience.
3. Missing or weak skills.
4. Experience alignment.
5. Relevant strengths.
6. Areas requiring improvement.
7. Practical recommendations to improve the CV.
8. Suggested interview preparation topics.

Be factual. Do not invent candidate experience or qualifications.
Clearly distinguish demonstrated skills from suggested improvements.
"""


def analyse_cv_with_gemini(client, model_name, prompt):
    import time

    if client is None:
        raise ValueError("Gemini client is not configured.")

    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response.")

            return response.text

        except Exception as error:
            error_message = str(error)
            temporary_errors = ["429", "500", "502", "503", "504"]

            is_temporary = any(
                code in error_message
                for code in temporary_errors
            )

            if not is_temporary or attempt == max_attempts - 1:
                raise

            wait_seconds = 2 ** (attempt + 1)

            print(
                f"Temporary Gemini error. "
                f"Retrying in {wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)

    raise RuntimeError(
        "Gemini analysis failed after all retry attempts."
    )



def extract_jd_text_from_pdf(pdf_bytes):
    """Extract job description text from uploaded PDF bytes."""
    from io import BytesIO
    from pypdf import PdfReader

    if not pdf_bytes:
        raise ValueError("The uploaded PDF is empty.")

    try:
        reader = PdfReader(BytesIO(pdf_bytes))

        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        ).strip()

    except Exception as error:
        raise ValueError(
            "Unable to read the PDF. Please upload a valid PDF file."
        ) from error

    if not text:
        raise ValueError(
            "No readable text found in the job description PDF."
        )

    return text

def extract_jd_text_from_image(
    client,
    image_bytes,
    mime_type,
    model_name="gemini-3.6-flash"
):
    """Extract job description text from a screenshot using Gemini."""
    from google.genai import types

    supported_types = ["image/jpeg", "image/png"]

    if mime_type not in supported_types:
        raise ValueError("Please upload a JPEG or PNG image.")

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

    prompt = """
    Extract all readable job description content from this image.
    Preserve headings, responsibilities, required skills,
    qualifications, experience, and location.
    Do not invent missing text.
    Return only the extracted text.
    """

    response = client.models.generate_content(
        model=model_name,
        contents=[prompt, image_part]
    )

    if not response.text or not response.text.strip():
        raise ValueError("Gemini could not extract readable text.")

    return response.text.strip()


def validate_linkedin_job_url(url):
    """Check whether the supplied URL is a genuine LinkedIn job URL."""
    from urllib.parse import urlparse

    if not isinstance(url, str) or not url.strip():
        return False

    parsed = urlparse(url.strip())
    hostname = (parsed.hostname or "").lower()

    return (
        parsed.scheme in ["http", "https"]
        and (hostname == "linkedin.com"
             or hostname.endswith(".linkedin.com"))
        and "/jobs/view/" in parsed.path.lower()
    )



def extract_jd_from_public_url(url):
    """
    Extract text from a publicly accessible LinkedIn job page.
    Does not bypass login or access restrictions.
    """
    import requests
    from bs4 import BeautifulSoup

    if not validate_linkedin_job_url(url):
        raise ValueError("Please provide a valid LinkedIn job URL.")

    response = requests.get(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
            )
        },
        timeout=15
    )

    response.raise_for_status()

    final_url = getattr(response, "url", url)

    if not validate_linkedin_job_url(final_url):
        raise ValueError(
            "LinkedIn redirected the request to another page. "
            "Please copy and paste the job description manually."
        )

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup(
        ["script", "style", "nav", "footer", "header"]
    ):
        element.decompose()

    page_text = soup.get_text(
        separator="\n",
        strip=True
    )

    lower_text = page_text.lower()

    blocked_markers = [
        "sign in to view more jobs",
        "join linkedin",
        "linkedin sign in",
        "authwall",
        "please sign in to continue"
    ]

    if any(marker in lower_text for marker in blocked_markers):
        raise ValueError(
            "LinkedIn requires login or has restricted access. "
            "Please copy and paste the job description manually."
        )

    if len(page_text) < 100:
        raise ValueError(
            "The job page did not provide enough readable text. "
            "Please copy and paste the job description manually."
        )

    return page_text
