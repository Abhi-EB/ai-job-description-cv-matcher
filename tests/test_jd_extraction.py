from io import BytesIO
from types import SimpleNamespace

import pytest
from reportlab.pdfgen import canvas

from app import (
    extract_jd_text_from_pdf,
    extract_jd_text_from_image,
    validate_linkedin_job_url,
    extract_jd_from_public_url
)


def create_sample_pdf():
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    pdf.drawString(
        50, 750,
        "Senior Software Engineer Job Description"
    )
    pdf.drawString(
        50, 720,
        "Required skills: Python, cloud and communication."
    )

    pdf.save()
    return buffer.getvalue()


def test_extract_jd_text_from_pdf():
    pdf_bytes = create_sample_pdf()

    extracted = extract_jd_text_from_pdf(pdf_bytes)

    assert "Senior Software Engineer" in extracted
    assert "Python" in extracted


def test_empty_pdf_is_rejected():
    with pytest.raises(ValueError):
        extract_jd_text_from_pdf(b"")


def test_valid_linkedin_job_url():
    assert validate_linkedin_job_url(
        "https://www.linkedin.com/jobs/view/123456/"
    )


def test_linkedin_url_without_job_path_is_rejected():
    assert not validate_linkedin_job_url(
        "https://www.linkedin.com/company/example/"
    )


def test_lookalike_linkedin_domain_is_rejected():
    assert not validate_linkedin_job_url(
        "https://evil-linkedin.com/jobs/view/123456/"
    )


def test_non_linkedin_url_is_rejected():
    assert not validate_linkedin_job_url(
        "https://example.com/jobs/view/123456/"
    )


def test_extract_jd_text_from_image():
    class FakeModels:
        def generate_content(self, **kwargs):
            return SimpleNamespace(
                text="Extracted role: Data Analyst. Required skill: SQL."
            )

    fake_client = SimpleNamespace(
        models=FakeModels()
    )

    extracted = extract_jd_text_from_image(
        fake_client,
        b"sample-image-data",
        "image/jpeg"
    )

    assert "Data Analyst" in extracted
    assert "SQL" in extracted


def test_unsupported_image_type_is_rejected():
    with pytest.raises(ValueError):
        extract_jd_text_from_image(
            None,
            b"sample-data",
            "image/gif"
        )


def test_extract_jd_from_public_url(monkeypatch):
    class FakeResponse:
        text = """
        <html>
            <body>
                <h1>Software Engineer</h1>
                <p>
                    We are looking for an experienced Software Engineer
                    to join our technology team. The candidate should have
                    strong Python programming skills, SQL database knowledge,
                    cloud computing experience, problem-solving ability,
                    communication skills and experience working with
                    cross-functional teams. Responsibilities include
                    developing applications, troubleshooting production
                    issues, writing maintainable code and collaborating
                    with stakeholders to deliver reliable solutions.
                </p>
            </body>
        </html>
        """

        def raise_for_status(self):
            pass

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "requests.get",
        fake_get
    )

    extracted = extract_jd_from_public_url(
        "https://www.linkedin.com/jobs/view/123456/"
    )

    assert "Software Engineer" in extracted
    assert "Python" in extracted


def test_linkedin_login_page_rejected(monkeypatch):
    class FakeResponse:
        url = "https://www.linkedin.com/jobs/view/123456/"

        text = """
        <html>
            <body>
                <h1>Sign in to view more jobs</h1>
                <p>Join LinkedIn to continue.</p>
            </body>
        </html>
        """

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        "requests.get",
        lambda *args, **kwargs: FakeResponse()
    )

    with pytest.raises(ValueError, match="login"):
        extract_jd_from_public_url(
            "https://www.linkedin.com/jobs/view/123456/"
        )
