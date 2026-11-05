import streamlit as st
import tempfile
import os

from google import genai
from report_utils import generate_pdf_report

from app import (
    extract_cv_text,
    validate_job_description,
    create_analysis_prompt,
    analyse_cv_with_gemini,
    extract_jd_text_from_pdf,
    extract_jd_text_from_image,
    validate_linkedin_job_url,
    extract_jd_from_public_url
)

st.set_page_config(
    page_title="AI CV Matcher",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Job Description & CV Matcher")

st.write(
    "Upload your CV and provide a job description "
    "using text, LinkedIn URL, PDF, or image."
)

st.divider()

# Step 1: CV upload
st.subheader("1. Upload your CV")

uploaded_cv = st.file_uploader(
    "Choose your CV in PDF format",
    type=["pdf"],
    key="cv_upload"
)

# Step 2: Select JD input method
st.subheader("2. Provide the Job Description")

input_method = st.radio(
    "Choose how you want to provide the job description:",
    [
        "Paste Text",
        "LinkedIn URL",
        "Upload PDF",
        "Upload Image"
    ],
    horizontal=True
)

# Prevent stale job descriptions from carrying over
previous_method = st.session_state.get("previous_input_method")

if previous_method is not None and previous_method != input_method:
    st.session_state.pop("extracted_jd", None)
    st.session_state.pop("reviewed_jd", None)

st.session_state["previous_input_method"] = input_method

jd_text = ""

# Paste text
if input_method == "Paste Text":
    jd_text = st.text_area(
        "Paste the complete job description",
        height=250,
        placeholder="Paste the job description here..."
    )

# LinkedIn URL
elif input_method == "LinkedIn URL":
    linkedin_url = st.text_input(
        "LinkedIn Job URL",
        placeholder="https://www.linkedin.com/jobs/view/..."
    )

    if st.button("Extract from LinkedIn URL"):
        if not validate_linkedin_job_url(linkedin_url):
            st.error("Please enter a valid LinkedIn job URL.")
        else:
            try:
                with st.spinner("Attempting to read the public job page..."):
                    extracted = extract_jd_from_public_url(
                        linkedin_url
                    )

                st.session_state["extracted_jd"] = extracted
                st.session_state["reviewed_jd"] = extracted
                st.success("Job description extracted.")

            except Exception as error:
                st.warning(
                    "Automatic extraction was unsuccessful. "
                    "LinkedIn may restrict public access. "
                    "Please copy the job description from LinkedIn "
                    "and use the Paste Text option."
                )
                st.caption(f"Technical detail: {error}")

# PDF upload
elif input_method == "Upload PDF":
    jd_pdf = st.file_uploader(
        "Upload job description PDF",
        type=["pdf"],
        key="jd_pdf"
    )

    if jd_pdf is not None:
        if st.button("Extract Text from PDF"):
            try:
                extracted = extract_jd_text_from_pdf(
                    jd_pdf.getvalue()
                )

                st.session_state["extracted_jd"] = extracted
                st.session_state["reviewed_jd"] = extracted
                st.success("PDF text extracted successfully.")

            except Exception as error:
                st.error(f"PDF extraction failed: {error}")

# Image upload
elif input_method == "Upload Image":
    jd_image = st.file_uploader(
        "Upload a JD screenshot",
        type=["jpg", "jpeg", "png"],
        key="jd_image"
    )

    if jd_image is not None:
        st.image(
            jd_image,
            caption="Uploaded job description screenshot",
            use_container_width=True
        )

        if st.button("Extract Text from Image"):
            try:
                api_key = None

                try:
                    from google.colab import userdata
                    api_key = userdata.get("GEMINI_API_KEY")
                except Exception:
                    pass

                if not api_key:
                    try:
                        api_key = st.secrets.get("GEMINI_API_KEY")
                    except Exception:
                        pass

                if not api_key:
                    api_key = os.environ.get("GEMINI_API_KEY")

                if not api_key:
                    st.error(
                        "Gemini API key not found. "
                        "Configure GEMINI_API_KEY in Streamlit Secrets."
                    )
                    st.stop()

                client = genai.Client(api_key=api_key)

                mime_type = (
                    "image/png"
                    if jd_image.type == "image/png"
                    else "image/jpeg"
                )

                with st.spinner("Gemini is reading your screenshot..."):
                    extracted = extract_jd_text_from_image(
                        client,
                        jd_image.getvalue(),
                        mime_type
                    )

                st.session_state["extracted_jd"] = extracted
                st.session_state["reviewed_jd"] = extracted
                st.success("Image text extracted successfully.")

            except Exception as error:
                st.error(f"Image extraction failed: {error}")

st.divider()

# Step 3: Review extracted content
st.subheader("3. Review Job Description")

if input_method == "Paste Text":
    st.caption(
        "Review your pasted job description in the text area above."
    )
else:
    if "reviewed_jd" not in st.session_state:
        st.session_state["reviewed_jd"] = (
            st.session_state.get("extracted_jd", "")
        )

    jd_text = st.text_area(
        "Verify or edit the extracted job description before analysis",
        height=250,
        key="reviewed_jd"
    )

# Step 4: Analysis
if st.button("Analyse CV", type="primary"):

    if uploaded_cv is None:
        st.error("Please upload your CV first.")

    else:
        valid_jd, jd_message = validate_job_description(jd_text)

        if not valid_jd:
            st.error(jd_message)

        else:
            try:
                api_key = None

                try:
                    from google.colab import userdata
                    api_key = userdata.get("GEMINI_API_KEY")
                except Exception:
                    pass

                if not api_key:
                    try:
                        api_key = st.secrets.get("GEMINI_API_KEY")
                    except Exception:
                        pass

                if not api_key:
                    api_key = os.environ.get("GEMINI_API_KEY")

                if not api_key:
                    st.error(
                        "Gemini API key not found. "
                        "Configure GEMINI_API_KEY in Streamlit Secrets."
                    )
                    st.stop()

                client = genai.Client(api_key=api_key)

                with tempfile.NamedTemporaryFile(
                    suffix=".pdf",
                    delete=False
                ) as temp_file:
                    temp_file.write(uploaded_cv.getvalue())
                    temp_path = temp_file.name

                try:
                    with st.spinner("Extracting CV content..."):
                        cv_text = extract_cv_text(temp_path)

                    prompt = create_analysis_prompt(
                        cv_text,
                        jd_text
                    )

                    with st.spinner("Gemini is analysing your CV..."):
                        analysis = analyse_cv_with_gemini(
                            client,
                            "gemini-3.6-flash",
                            prompt
                        )

                    st.success("Analysis completed successfully!")

                    st.subheader("4. Your CV Matching Report")
                    st.markdown(analysis)

                    st.download_button(
                        label="Download Analysis as TXT",
                        data=analysis,
                        file_name="cv_matching_report.txt",
                        mime="text/plain"
                    )

                    pdf_data = generate_pdf_report(analysis)

                    st.download_button(
                        label="Download Analysis as PDF",
                        data=pdf_data,
                        file_name="cv_matching_report.pdf",
                        mime="application/pdf"
                    )

                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

            except Exception as error:
                st.error(f"Analysis failed: {error}")

st.divider()

st.caption(
    "AI-generated analysis is advisory. "
    "Always verify that your CV accurately represents your experience."
)
