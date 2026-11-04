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
