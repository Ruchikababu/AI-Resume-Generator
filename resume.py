import streamlit as st
import io
from fpdf import FPDF
import google.generativeai as genai

# --- CONFIG ---
st.set_page_config(page_title="AI Resume Generator", page_icon="📝")
GEMINI_API_KEY = "AIzaSyCi8KQh1GNP_IqdFYtlOIIu5eiYChXGiF0"  # Replace with your real key

# --- SETUP Gemini ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

# --- Unicode fixer ---
def clean_text(text):
    replacements = {
        '\u2013': '-', '\u2014': '-', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2026': '...'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

# --- UI ---
st.title("📝 AI Resume Generator")

with st.form("resume_form"):
    name = st.text_input("Your Name")
    skills = st.text_area("Skills (comma-separated)")
    experience = st.text_area("Work Experience")
    role = st.text_input("Describe Desired Role")
    submitted = st.form_submit_button("Generate Resume")

if submitted:
    if not name:
        name = "John Doe"
    if not skills:
        skills = "Java, SQL, Git"
    if not experience:
        experience = "1 year as a Junior Developer"
    if not role:
        role = "Backend Developer"

    with st.spinner("Generating your resume..."):
        prompt = f"""
        You are an expert resume writer.
        Generate a complete, realistic resume with:
        - No placeholders like [ ] or ( )
        - Generic, realistic details if input is short
        - Sections: NAME/CONTACT, SUMMARY, SKILLS, WORK EXPERIENCE, OBJECTIVE
        Return plain text with bullet points and line breaks.
        Info:
        Name: {name}
        Skills: {skills}
        Experience: {experience}
        Role: {role}
        """

        response = model.generate_content(prompt)
        resume_text = response.text.strip()

        cleaned_text = clean_text(resume_text)

        if '[' in cleaned_text or '(' in cleaned_text:
            st.warning("⚠️ Incomplete placeholders found. Please regenerate.")
            st.stop()

        # --- Show exactly what will go in PDF ---
        st.subheader("✅ Your AI-Generated Resume")
        st.text(cleaned_text)

        # --- PDF ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        for line in cleaned_text.splitlines():
            headers = ["SUMMARY", "PROFESSIONAL SUMMARY", "SKILLS", "WORK EXPERIENCE", "OBJECTIVE"]
            if line.strip().upper() in headers:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, line.strip(), ln=True)
                pdf.set_font("Arial", '', 12)
            else:
                pdf.multi_cell(0, 10, line.strip())

        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)

        st.download_button(
            label="📄 Download Resume as PDF",
            data=pdf_buffer,
            file_name="resume.pdf",
            mime="application/pdf"
        )
