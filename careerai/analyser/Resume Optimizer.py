import streamlit as st
import fitz  # PyMuPDF
import docx
import google.generativeai as genai
import re

# Set up Gemini API Key
genai.configure(api_key="AIzaSyDJrBU_Q0hWvuw6wL_lI4EClmutjP4PW5I")

# Streamlit Page Config
st.set_page_config(page_title="Resume Optimizer", layout="wide")

# Custom CSS Styling
st.markdown("""
    <style>
        body, [data-testid="stAppViewContainer"] {
            background-color: #f4f4f4 !important;
        }
        .main-title {
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            color: #1D9FF0;
            margin-top: 20px;
        }
        .st.file_uploader label, .stTextInput>label, .stTextArea>label, .st.subheader, .stFileUploader label {
            color: #000000 !important; 
            font-weight: bold;
        }
        .description {
            font-size: 18px;
            text-align: center;
            color: #666666;
            margin-bottom: 20px;
        }
        .stButton>button {
            background-color: #1D9FF0;
            color: white;
            font-size: 16px;
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #1578C2;
            color: white !important;
        }
        .stTextInput>div>div>input, .stTextArea>div>textarea {
            background-color: #ffffff !important;
            color: #333333 !important;
            font-size: 16px !important;
            border: 1px solid #cccccc !important;
            border-radius: 8px !important;
            padding: 10px !important;
        }
        .stFileUploader>div {
            border: 2px dashed #1D9FF0 !important;
            border-radius: 10px !important;
            padding: 20px !important;
            color: black !important; /* Black text for uploaded file name */
        }
        .st.subheader, .extracted-text-label {
            color: black !important; /* Black text for "Extracted Resume Text" */
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# App Title
st.markdown('<div class="main-title">Resume Optimizer</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Enhance your resume for ATS compatibility and your desired job role.</div>', unsafe_allow_html=True)

# Upload Resume
uploaded_file = st.file_uploader("Upload your Resume (PDF/DOCX)", type=["pdf", "docx"])

# Function to Extract Text from PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "".join([page.get_text("text") for page in doc])
    return text

# Function to Extract Text from DOCX
def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Clean Resume Text
def clean_text(text):
    text = re.sub(r'[*-]+', '', text)  # Remove markdown symbols
    return text.strip()

# AI Optimization Function
def optimize_resume_gemini(resume_text, job_role):
    prompt = f"""
    Optimize my resume by improving clarity, readability, and keyword relevance for {job_role}. 
    Ensure the content is ATS-friendly by incorporating relevant industry-specific keywords naturally. 
    Enhance bullet points to be more action-oriented and results-driven, 
    using strong verbs and quantifiable achievements where possible. 
    Keep the formatting concise and professional while improving overall flow. 
    
    Here is my resume content: 
    {resume_text}
    """
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text if response else "Error generating resume."

# Process Uploaded File
if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1]

    if file_extension == "pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    elif file_extension == "docx":
        resume_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file format!")
        resume_text = ""

    if resume_text:
        st.markdown('<div class="extracted-text-label">Extracted Resume Text</div>', unsafe_allow_html=True)
        st.text_area("", resume_text, height=250)

        job_role = st.text_input("Target Job Role", "Software Engineer")

        if st.button("Optimize Resume"):
            with st.spinner("Enhancing your resume with AI..."):
                optimized_resume = optimize_resume_gemini(resume_text, job_role)

                st.subheader("Optimized Resume")
                st.text_area("", optimized_resume, height=250)
