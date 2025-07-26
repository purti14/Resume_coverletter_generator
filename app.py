import streamlit as st
import requests
import os
from fpdf import FPDF
import tempfile
import re

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
            {"role": "system", "content": "You are a professional resume writer. Create concise, one-page resumes with clear sections. Use ### for section headers and - for bullet points. Keep bullet points brief and impactful. Prioritize the most relevant information. For resumes, focus on achievements and quantifiable results. Use professional language and action verbs. Ensure the content fits on one page by being selective and concise."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1200,
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"Error: {response.status_code} - {response.text}"

def clean_text(text):
    """Clean text to be compatible with FPDF latin-1 encoding"""
    # Replace Unicode bullet points with ASCII equivalents
    text = text.replace('•', '-')
    text = text.replace('–', '-')
    text = text.replace('—', '-')
    text = text.replace('"', '"')
    text = text.replace('"', '"')
    text = text.replace(''', "'")
    text = text.replace(''', "'")
    text = text.replace('…', '...')
    
    # Remove or replace other problematic Unicode characters
    # Keep only printable ASCII characters and common punctuation
    text = re.sub(r'[^\x20-\x7E\n\r\t]', '', text)
    
    return text

def create_pdf(text, filename):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=10)
        pdf.set_margins(15, 15, 15)

        # Clean the text first
        text = clean_text(text)
        
        # Split text into lines
        lines = text.split('\n')
        
        # Header section with name and contact info
        if len(lines) > 0:
            pdf.set_font("Arial", "B", 24)
            pdf.cell(0, 15, lines[0], ln=True, align="C")
        
        # Contact information in smaller font
        contact_lines = []
        for i in range(1, min(4, len(lines))):
            if lines[i].strip() and not lines[i].strip().startswith("###"):
                contact_lines.append(lines[i])
        
        if contact_lines:
            pdf.set_font("Arial", "", 10)
            contact_text = " | ".join(contact_lines)
            pdf.cell(0, 8, contact_text, ln=True, align="C")
        
        pdf.ln(8)
        
        # Professional line separator
        pdf.set_draw_color(100, 100, 100)
        pdf.set_line_width(0.5)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(8)

        # Main content with improved formatting
        current_y = pdf.get_y()
        for line in lines[3:]:
            # Check if we're approaching page limit
            if pdf.get_y() > 250:  # Leave space for footer
                break
                
            line = line.strip()
            if not line:
                pdf.ln(3)
                continue
                
            # Section headers
            if line.startswith("###"):
                pdf.ln(2)
                pdf.set_font("Arial", "B", 14)
                pdf.set_text_color(50, 50, 150)  # Dark blue for headers
                header_text = line.replace("###", "").strip()
                pdf.cell(0, 10, header_text.upper(), ln=True)
                pdf.set_text_color(0, 0, 0)  # Reset to black
                pdf.set_font("Arial", "", 11)
                pdf.ln(2)
                
            # Bullet points with better formatting
            elif line.startswith("- "):
                pdf.set_x(20)
                pdf.set_font("Arial", "", 10)
                bullet_text = line[2:].strip()
                # Wrap long bullet points
                if len(bullet_text) > 80:
                    words = bullet_text.split()
                    lines_wrapped = []
                    current_line = ""
                    for word in words:
                        if len(current_line + " " + word) <= 80:
                            current_line += " " + word if current_line else word
                        else:
                            lines_wrapped.append(current_line)
                            current_line = word
                    if current_line:
                        lines_wrapped.append(current_line)
                    
                    for i, wrapped_line in enumerate(lines_wrapped):
                        if i == 0:
                            pdf.cell(0, 6, "- " + wrapped_line, ln=True)
                        else:
                            pdf.set_x(25)
                            pdf.cell(0, 6, wrapped_line, ln=True)
                else:
                    pdf.cell(0, 6, "- " + bullet_text, ln=True)
                    
            # Regular text
            else:
                pdf.set_font("Arial", "", 10)
                pdf.multi_cell(0, 5, line)

        pdf.output(filename)
        return True
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return False

st.title("AI Resume & Cover Letter Generator (Mistral)")

# Create tabs for different document types
tab1, tab2 = st.tabs(["Resume Generator", "Cover Letter Generator"])

with tab1:
    st.header("Resume Generator")
    st.info("💡 Tip: Fill in the most relevant information. The AI will create a concise, professional one-page resume.")
    
    # Personal Information
    st.subheader("Personal Information")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", key="resume_name")
        email = st.text_input("Email", key="resume_email")
        phone = st.text_input("Phone Number", key="resume_phone")
    with col2:
        location = st.text_input("Location (City, State)", key="resume_location")
        linkedin = st.text_input("LinkedIn Profile", key="resume_linkedin")
        portfolio = st.text_input("Portfolio/Website", key="resume_portfolio")
    
    # Professional Summary
    st.subheader("Professional Summary")
    summary = st.text_area("Professional Summary/Objective (2-3 sentences)", key="resume_summary", 
                          placeholder="e.g., Experienced software developer with 5+ years in web development...")
    
    # Education
    st.subheader("Education")
    education = st.text_area("Education (Include degree, institution, graduation year, GPA if relevant)", 
                            key="resume_education", placeholder="e.g., Bachelor of Science in Computer Science, University of XYZ, 2020, GPA: 3.8")
    
    # Experience
    st.subheader("Work Experience")
    experience = st.text_area("Work Experience (Include job titles, companies, dates, and key responsibilities)", 
                             key="resume_experience", placeholder="e.g., Software Developer at ABC Corp (2020-2023): Developed web applications using React and Node.js...")
    
    # Skills
    st.subheader("Skills")
    skills = st.text_area("Technical Skills (comma-separated or list format)", 
                         key="resume_skills", placeholder="e.g., Python, JavaScript, React, Node.js, SQL, Git")
    
    # Projects
    st.subheader("Projects")
    projects = st.text_area("Projects (Include project names, technologies used, and brief descriptions)", 
                           key="resume_projects", placeholder="e.g., E-commerce Website: Built using React and Node.js, implemented payment processing...")
    
    # Achievements
    st.subheader("Achievements & Certifications")
    achievements = st.text_area("Achievements, Awards, Certifications", 
                               key="resume_achievements", placeholder="e.g., AWS Certified Developer, Led team of 5 developers, Increased performance by 40%")
    
    # Additional Information
    st.subheader("Additional Information")
    languages = st.text_input("Languages (if applicable)", key="resume_languages", placeholder="e.g., English (Native), Spanish (Fluent)")
    interests = st.text_input("Interests/Hobbies (optional)", key="resume_interests", placeholder="e.g., Open source contribution, Machine learning")

with tab2:
    st.header("Cover Letter Generator")
    st.info("💡 Tip: Customize your cover letter for each specific job application to increase your chances.")
    
    # Personal Information for Cover Letter
    st.subheader("Personal Information")
    cl_name = st.text_input("Full Name", key="cl_name")
    cl_email = st.text_input("Email", key="cl_email")
    cl_phone = st.text_input("Phone Number", key="cl_phone")
    cl_address = st.text_area("Address", key="cl_address")
    
    # Company Information
    st.subheader("Company Information")
    company_name = st.text_input("Company Name", key="cl_company")
    hiring_manager = st.text_input("Hiring Manager Name (if known)", key="cl_manager")
    position = st.text_input("Position Title", key="cl_position")
    
    # Cover Letter Content
    st.subheader("Cover Letter Content")
    experience_cl = st.text_area("Relevant Experience", key="cl_experience", 
                                placeholder="Describe your relevant experience that matches the job requirements")
    skills_cl = st.text_area("Relevant Skills", key="cl_skills", 
                            placeholder="Highlight skills that are specifically relevant to this position")
    motivation = st.text_area("Why you want this position", key="cl_motivation", 
                             placeholder="Explain why you're interested in this role and company")
    achievements_cl = st.text_area("Key Achievements", key="cl_achievements", 
                                  placeholder="Mention specific achievements that demonstrate your value")

# Generate button and results
if st.button("Generate Document", type="primary"):
    # Determine which tab is active
    if tab1:
        active_tab = "resume"
    else:
        active_tab = "cover_letter"
    
    if active_tab == "resume":
        # Generate Resume
        prompt = (
            f"Create a professional, one-page resume with the following information:\n\n"
            f"PERSONAL INFORMATION:\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n"
            f"Location: {location}\n"
            f"LinkedIn: {linkedin}\n"
            f"Portfolio: {portfolio}\n\n"
            f"PROFESSIONAL SUMMARY:\n{summary}\n\n"
            f"EDUCATION:\n{education}\n\n"
            f"WORK EXPERIENCE:\n{experience}\n\n"
            f"SKILLS:\n{skills}\n\n"
            f"PROJECTS:\n{projects}\n\n"
            f"ACHIEVEMENTS:\n{achievements}\n\n"
            f"ADDITIONAL:\n"
            f"Languages: {languages}\n"
            f"Interests: {interests}\n\n"
            f"IMPORTANT INSTRUCTIONS:\n"
            f"- Create a concise, one-page resume\n"
            f"- Use ### for section headers: ### PROFESSIONAL SUMMARY, ### EDUCATION, ### WORK EXPERIENCE, ### SKILLS, ### PROJECTS, ### ACHIEVEMENTS\n"
            f"- Use - for bullet points\n"
            f"- Keep bullet points brief and impactful (max 1-2 lines each)\n"
            f"- Focus on achievements and quantifiable results\n"
            f"- Use action verbs and professional language\n"
            f"- Prioritize the most relevant information\n"
            f"- Ensure all content fits on one page by being selective\n"
            f"- Start with name as the first line, then contact information\n"
            f"- Format contact info as: email | phone | location | LinkedIn (if provided)"
        )
        doc_type = "Resume"
    else:
        # Generate Cover Letter
        prompt = (
            f"Write a professional cover letter for the following details:\n\n"
            f"PERSONAL INFORMATION:\n"
            f"Name: {cl_name}\n"
            f"Email: {cl_email}\n"
            f"Phone: {cl_phone}\n"
            f"Address: {cl_address}\n\n"
            f"COMPANY INFORMATION:\n"
            f"Company: {company_name}\n"
            f"Hiring Manager: {hiring_manager}\n"
            f"Position: {position}\n\n"
            f"CONTENT:\n"
            f"Relevant Experience: {experience_cl}\n"
            f"Relevant Skills: {skills_cl}\n"
            f"Motivation: {motivation}\n"
            f"Key Achievements: {achievements_cl}\n\n"
            f"Write a compelling cover letter that connects your experience and skills to the position requirements."
        )
        doc_type = "Cover Letter"
    
    with st.spinner("Generating..."):
        result = generate_with_mistral(prompt)
    
    st.subheader(f"Generated {doc_type}")
    st.text_area("Generated Content", result, height=400)
    
    # PDF download button
    if result and not result.startswith("Error"):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                if create_pdf(result, tmpfile.name):
                    tmpfile.seek(0)
                    st.download_button(
                        label=f"Download {doc_type} as PDF",
                        data=tmpfile.read(),
                        file_name=f"{doc_type}_{(name if doc_type == 'Resume' else cl_name).replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Failed to generate PDF. Please try again.")
        except Exception as e:
            st.error(f"Error creating PDF: {str(e)}")
            st.info("You can still copy the generated text above.")
