import streamlit as st
import requests
import os
from fpdf import FPDF
import tempfile

MISTRAL_API_KEY = "USE YOUR API KEY HERE"  # Replace with your Mistral API key

def generate_with_mistral(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistral-medium",  # or "mistral-small", "mistral-medium" if available
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that writes resumes and cover letters."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"Error: {response.status_code} - {response.text}"

def clean_text(text):
    return text.encode("latin-1", "ignore").decode("latin-1")

def create_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Split text into lines
    lines = clean_text(text).split('\n')

    # Header: Name and Email (first two lines)
    if len(lines) > 0:
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 12, lines[0], ln=True, align="C")
    if len(lines) > 1:
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, lines[1], ln=True, align="C")
    pdf.ln(5)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # Main content
    pdf.set_font("Arial", "", 12)
    for line in lines[2:]:
        # Section headers (lines starting with ###)
        if line.strip().startswith("###"):
            pdf.ln(4)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, line.replace("###", "").strip(), ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.ln(1)
        # Bullet points
        elif line.strip().startswith("- "):
            pdf.set_x(20)
            pdf.cell(0, 8, "- " + line[2:], ln=True)
        # Horizontal rule
        elif line.strip() == "---":
            pdf.ln(2)
            pdf.set_draw_color(180, 180, 180)
            pdf.set_line_width(0.2)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(2)
        # Normal text
        elif line.strip():
            pdf.multi_cell(0, 8, line.strip())
        else:
            pdf.ln(2)

    pdf.output(filename)

st.title("AI Resume & Cover Letter Generator (Mistral)")

# User input fields
name = st.text_input("Name")
email = st.text_input("Email")
role = st.text_input("Target Role")
experience = st.text_area("Experience")
skills = st.text_input("Skills (comma-separated)")
goals = st.text_area("Career Goals")
doc_type = st.selectbox("Document Type", ["Resume", "Cover Letter"])

result = None
if st.button("Generate"):
    prompt = (
        f"Write a professional {doc_type.lower()} for the following details:\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Target Role: {role}\n"
        f"Experience: {experience}\n"
        f"Skills: {skills}\n"
        f"Career Goals: {goals}\n"
    )
    with st.spinner("Generating..."):
        result = generate_with_mistral(prompt)
    st.subheader(f"{doc_type}")
    st.code(result)

    # PDF download button
    if result and not result.startswith("Error"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            create_pdf(result, tmpfile.name)
            tmpfile.seek(0)
            st.download_button(
                label=f"Download {doc_type} as PDF",
                data=tmpfile.read(),
                file_name=f"{doc_type}_{name.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )