
import streamlit as st
import tempfile
import os

from google import genai
from report_utils import generate_pdf_report

from app import (
    extract_cv_text,
    validate_job_description,
    create_analysis_prompt,
    analyse_cv_with_gemini
)

st.set_page_config(
    page_title="AI CV Matcher",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Job Description & CV Matcher")

st.write(
    "Upload your CV and paste a job description "
    "to receive an AI-powered compatibility analysis."
)

st.divider()

# CV upload
st.subheader("1. Upload your CV")

uploaded_cv = st.file_uploader(
    "Choose your CV in PDF format",
    type=["pdf"]
)

# Job description
st.subheader("2. Enter the Job Description")

jd_text = st.text_area(
    "Paste the complete job description here",
    height=250,
    placeholder="Paste the job description..."
)

# Analysis
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

                # Google Colab Secrets
                try:
                    from google.colab import userdata
                    api_key = userdata.get("GEMINI_API_KEY")
                except Exception:
                    pass

                # Streamlit deployment secrets
                if not api_key:
                    try:
                        api_key = st.secrets.get("GEMINI_API_KEY")
                    except Exception:
                        pass

                # Environment variable fallback
                if not api_key:
                    api_key = os.environ.get("GEMINI_API_KEY")

                if not api_key:
                    st.error(
                        "Gemini API key not found. "
                        "Configure GEMINI_API_KEY in Colab Secrets "
                        "or Streamlit Secrets."
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

                    prompt = create_analysis_prompt(cv_text, jd_text)

                    with st.spinner("Gemini is analysing your CV..."):
                        analysis = analyse_cv_with_gemini(
                            client,
                            "gemini-3.6-flash",
                            prompt
                        )

                    st.success("Analysis completed successfully!")

                    st.subheader("3. Your CV Matching Report")

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
