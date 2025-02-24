import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import time  # For simulating loading

# Set up Gemini API Key
genai.configure(api_key="AIzaSyDJrBU_Q0hWvuw6wL_lI4EClmutjP4PW5I")

# Streamlit app configuration
st.set_page_config(page_title="JD Matcher & Skill Gap Analysis", layout="wide")

# Custom CSS for styling
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
            border: 2px solid #1D9FF0;
            cursor: pointer;
            transition: 0.3s;
        }
        .stButton>button:hover {
            color: black !important;
        }
        .stButton>button:active {
            background-color: white !important;
            color: black !important;
            border: 2px solid #1D9FF0 !important;
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
        }
        /* Ensuring labels are black */
        label {
            color: #000000 !important;
            font-weight: bold !important;
        }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<div class="main-title">JD Matcher & Skill Gap Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Upload your resume and get a detailed comparison with a job description.</div>', unsafe_allow_html=True)

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    try:
        with uploaded_file as f:
            pdf_data = f.read()
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {str(e)}"

# File uploader for resume
resume_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if resume_file is not None:
    with st.spinner("Extracting text from resume..."):
        resume_text = extract_text_from_pdf(resume_file)
        if not resume_text:
            st.error("⚠️ Could not extract text from the uploaded resume.")
        else:
            st.success("✅ Resume processed successfully!")
            st.text_area("Extracted Resume Content:", resume_text, height=250)

# Function to get job description from Gemini AI
def get_job_description(role):
    prompt = f"Generate a job description for a {role} role."
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text if response else "Error generating job description."

# User selects job role
job_role = st.text_input("Enter the Job Role", "Software Engineer")

if st.button("Analyze"):
    loading_placeholder = st.empty()  # Placeholder for loading text

    # Show green "Fetching job description..." text
    loading_placeholder.markdown('<p style="color: green; font-weight: bold;">Fetching job description...</p>', unsafe_allow_html=True)
    
    time.sleep(2)  # Simulate API call delay

    job_desc = get_job_description(job_role)
    
    # Clear the loading message
    loading_placeholder.empty()

    if not job_desc or "Error" in job_desc:
        st.error("Failed to generate job description. Try again.")
    else:
        st.session_state["job_desc"] = job_desc
        st.text_area("Generated Job Description:", job_desc, height=250)

# Skill gap analysis
def analyze_skill_gap(resume_text, job_desc):
    prompt = f"Compare the following resume text with the job description and provide a skill gap analysis:\n\nResume:\n{resume_text}\n\nJob Description:\n{job_desc}\n\nHighlight missing skills and suggest improvements."
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text if response else "Error analyzing skill gap."

if resume_file and "job_desc" in st.session_state:
    with st.spinner("Analyzing skill gaps..."):
        skill_gap_analysis = analyze_skill_gap(resume_text, st.session_state["job_desc"])
        st.text_area("Skill Gap Analysis:", skill_gap_analysis, height=250)
