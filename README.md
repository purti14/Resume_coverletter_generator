📄 AI Resume & Cover Letter Generator

An AI-powered web application that generates professional resumes and cover letters instantly.
Built with Python and Streamlit, powered by the Mistral API, and supports PDF download.

🚀 Features

✨ AI-generated resume and cover letter from user input

⚡ Built with Python + Streamlit for quick deployment

🤖 Uses Mistral AI API for smart text generation

📂 Export results as a PDF file

🌐 Easy-to-use web interface

🛠 Tech Stack

Python 3
Streamlit (for hosting the web app)
Mistral API (AI model for text generation)
FPDF / ReportLab (to generate PDFs)

📂 Project Structure
├── app.py            # Main Streamlit app
├── requirements.txt  # Dependencies
├── utils/            # Helper functions (PDF generation, formatting)
└── README.md         # Project documentation

⚙️ Installation & Setup

Clone the repository
git clone https://github.com/your-username/ai-resume-coverletter.git
cd ai-resume-coverletter

Create a virtual environment & install dependencies
pip install -r requirements.txt

Add your Mistral API Key

Create a .env file and add:
MISTRAL_API_KEY=your_api_key_here

Run the Streamlit app
streamlit run app.py

📤 Usage

Open the app in your browser (http://localhost:8501)
Enter your details (name, skills, experience, job role)
Click Generate → AI creates a resume and cover letter
Download as PDF with one click


📌 Future Improvements

🎨 Add multiple resume templates & designs
🌍 Support for multiple languages
📊 AI-powered resume score/feedback
☁ Deploy on Streamlit Cloud or HuggingFace Spaces

👩‍💻 Author

Purti Ojha
Generative AI Project | Resume & Cover Letter Builder
