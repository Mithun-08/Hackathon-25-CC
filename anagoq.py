import streamlit as st
import fitz  # PyMuPDF
import groq  # Groq API client
import time  # For simulating loading
import streamlit.components.v1 as components
import json

# Set up Groq API Key
client = groq.Client(api_key="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")

# Streamlit app configuration
st.set_page_config(page_title="JD Matcher & Skill Gap Analysis", layout="wide")

# Custom Header Component
def render_header():
    header_html = """
    <div style="background: linear-gradient(90deg, #003366, #1D9FF0); padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h1 style="color: white; font-size: 36px; margin-bottom: 10px;">JD Matcher & Skill Gap Analysis</h1>
        <p style="color: white; font-size: 18px;">Upload your resume and get a detailed comparison with a job description.</p>
    </div>
    """
    components.html(header_html, height=150)

# Function to render job description with custom styling
def render_job_description(job_desc):
    job_desc_html = job_desc.replace("\n", "<br>")
    html = f"""
    <div style="background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 20px 0;">
        <h3 style="color: #1D9FF0; margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 10px;">Job Description</h3>
        <div style="max-height: 300px; overflow-y: auto; padding: 10px 5px;">
            {job_desc_html}
        </div>
    </div>
    """
    components.html(html, height=350)

# Simple skill gap visualization component
def render_skill_gap_analysis(analysis_text):
    # Extract missing skills with simple parsing
    missing_skills = []
    recommendations = ""
    
    # Very basic parsing - in a real app you'd want more robust parsing
    for line in analysis_text.split('\n'):
        if "missing" in line.lower() and ":" in line:
            skills = line.split(":", 1)[1].strip()
            missing_skills.extend([s.strip() for s in skills.split(',')])
        if "recommend" in line.lower() and ":" in line:
            recommendations = line.split(":", 1)[1].strip()
    
    # Create a simple visualization
    html = f"""
    <div style="background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="color: #333; margin-top: 0; border-bottom: 2px solid #1D9FF0; padding-bottom: 10px;">Skill Gap Analysis</h2>
        
        <div style="margin-top: 20px;">
            <h3 style="color: #F44336;">Missing Skills</h3>
            <ul id="missing-skills" style="padding-left: 20px; line-height: 1.6;">
                {' '.join(f'<li>{skill}</li>' for skill in missing_skills[:5])}
            </ul>
        </div>
        
        <div style="margin-top: 20px;">
            <h3 style="color: #1D9FF0;">Recommendations</h3>
            <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #1D9FF0; border-radius: 4px;">
                {recommendations}
            </div>
        </div>
        
        <div style="margin-top: 20px; background-color: #e8f4fd; padding: 15px; border-radius: 8px;">
            <h3 style="color: #1D9FF0; margin-top: 0;">Full Analysis</h3>
            <div style="white-space: pre-line;">{analysis_text}</div>
        </div>
    </div>
    """
    components.html(html, height=600)

# Loading animation component
def render_loading_animation(message="Processing..."):
    html = f"""
    <div style="text-align: center; padding: 30px;">
        <div style="display: inline-block; width: 50px; height: 50px; border: 5px solid rgba(29, 159, 240, 0.2); border-radius: 50%; border-top-color: #1D9FF0; animation: spin 1s linear infinite;"></div>
        <p style="margin-top: 15px; font-size: 18px; color: #1D9FF0;">{message}</p>
    </div>
    <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
    """
    return components.html(html, height=150)

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

# Function to get job description using Groq API
def get_job_description(role):
    prompt = f"Generate a detailed job description for a {role} role."
    
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
    )
    
    return response.choices[0].message.content if response.choices else "Error generating job description."

# Function to analyze skill gaps
def analyze_skill_gap(resume_text, job_desc):
    prompt = f"""
    Compare the following resume text with the job description and provide a skill gap analysis:

    Resume:
    {resume_text}

    Job Description:
    {job_desc}

    Highlight missing skills and suggest improvements. Include the following sections:
    1. Match Summary
    2. Missing Skills
    3. Recommendations for improvement
    """

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content if response.choices else "Error analyzing skill gap."

# Add custom CSS
st.markdown("""
    <style>
        .stButton>button {
            background-color: #1D9FF0;
            color: white;
            font-size: 16px;
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #0077be;
        }
        div[data-testid="stFileUploader"] > section > div > div:first-child {
            border: 2px dashed #1D9FF0;
            border-radius: 10px;
            padding: 20px;
        }
        div[data-testid="stFileUploader"] > section > div > button {
            background-color: #1D9FF0;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Main app
def main():
    # Render custom header
    render_header()
    
    # Create two columns for resume and job description
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Upload Your Resume")
        resume_file = st.file_uploader("Drop your resume here", type=["pdf"])
        
        if resume_file is not None:
            loading_placeholder = st.empty()
            with loading_placeholder:
                render_loading_animation("Extracting resume content...")
            
            resume_text = extract_text_from_pdf(resume_file)
            loading_placeholder.empty()
            
            if not resume_text:
                st.error("⚠️ Could not extract text from the uploaded resume.")
            else:
                st.session_state["resume_text"] = resume_text
                st.success("✅ Resume processed successfully!")
                
                # Display resume content in a collapsible section
                with st.expander("View Resume Content", expanded=False):
                    st.text_area("Extracted Content:", resume_text, height=250)
    
    with col2:
        st.markdown("### Job Description")
        job_role = st.text_input("Enter the Job Role", "Software Engineer")
        
        if st.button("Get Job Description"):
            loading_placeholder = st.empty()
            with loading_placeholder:
                render_loading_animation("Fetching job description...")
            
            job_desc = get_job_description(job_role)
            loading_placeholder.empty()
            
            if not job_desc or "Error" in job_desc:
                st.error("Failed to generate job description. Try again.")
            else:
                st.session_state["job_desc"] = job_desc
                # Display with custom component
                render_job_description(job_desc)
    
    # Display analysis section if both resume and job description are available
    if "resume_text" in st.session_state and "job_desc" in st.session_state:
        st.markdown("## Analysis Results")
        
        if st.button("Analyze Match"):
            loading_placeholder = st.empty()
            with loading_placeholder:
                render_loading_animation("Performing detailed analysis...")
            
            analysis_text = analyze_skill_gap(st.session_state["resume_text"], st.session_state["job_desc"])
            loading_placeholder.empty()
            
            # Render analysis with custom component
            render_skill_gap_analysis(analysis_text)

if __name__ == "__main__":
    main()