import streamlit as st
import streamlit.components.v1 as components
import fitz  # PyMuPDF
import docx
import groq
import re
import base64
from io import BytesIO

# Set up Groq API Key
GROQ_API_KEY = "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"

# Initialize Groq Client
client = groq.Groq(api_key=GROQ_API_KEY)

# Function to get image as base64 string (for custom components)
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Function to serve local CSS
def local_css(style):
    st.markdown(f'<style>{style}</style>', unsafe_allow_html=True)

# Extract functions
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.getvalue(), filetype="pdf")
    text = "".join([page.get_text("text") for page in doc])
    return text

def extract_text_from_docx(docx_file):
    doc = docx.Document(BytesIO(docx_file.getvalue()))
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Clean Resume Text
def clean_text(text):
    text = re.sub(r'[*-]+', '', text)  # Remove markdown symbols
    text = re.sub(r'\s+', ' ', text)    # Normalize whitespace
    return text.strip()

# AI Optimization Function using Groq API
def optimize_resume_groq(resume_text, job_role, skills=None, optimization_focus=None):
    # Build a more comprehensive prompt based on user preferences
    prompt = f"""
    Optimize my resume for the role of {job_role}. 
    
    {'Focus on highlighting these skills: ' + ', '.join(skills) if skills else ''}
    {'Specifically focus on: ' + optimization_focus if optimization_focus else ''}
    
    Please improve:
    1. ATS compatibility by incorporating relevant keywords naturally
    2. Clarity and readability while maintaining professional tone
    3. Action-oriented bullet points with quantifiable achievements 
    4. Overall structure and flow
    
    Return the optimized resume in a clean, well-formatted structure.
    
    Here is my resume content: 
    {resume_text}
    """

    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an expert resume optimizer with extensive knowledge of ATS systems."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        return response.choices[0].message.content if response.choices else "Error generating resume."
    except Exception as e:
        return f"Error: {str(e)}"

# Custom HTML/CSS/JS components
def render_header():
    header_html = """
    <div style="padding: 20px; background: linear-gradient(90deg, #1D9FF0, #0F7EBD); border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <h1 style="color: white; text-align: center; margin: 0; font-size: 42px; font-weight: 700;">Resume Optimizer</h1>
        <p style="color: white; text-align: center; margin-top: 10px; font-size: 18px; opacity: 0.9;">
            Enhance your resume's ATS compatibility and alignment with your target role
        </p>
    </div>
    """
    components.html(header_html, height=150)

def render_file_upload_area():
    upload_area_html = """
    <div id="upload-area" style="border: 2px dashed #1D9FF0; border-radius: 12px; padding: 40px 20px; text-align: center; margin-bottom: 20px; transition: all 0.3s;">
        <i class="fas fa-file-upload" style="font-size: 48px; color: #1D9FF0; margin-bottom: 15px;"></i>
        <h3 style="color: #333; margin-bottom: 10px;">Drag and drop your resume file here</h3>
        <p style="color: #666;">Supports PDF and DOCX formats</p>
    </div>
    <script>
        // This script is for visual effect only - actual upload is handled by Streamlit
        const uploadArea = document.getElementById('upload-area');
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.backgroundColor = '#e6f7ff';
            uploadArea.style.borderColor = '#0D8DD0';
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.style.backgroundColor = 'transparent';
            uploadArea.style.borderColor = '#1D9FF0';
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.style.backgroundColor = 'transparent';
            uploadArea.style.borderColor = '#1D9FF0';
        });
    </script>
    """
    components.html(upload_area_html, height=220)

def render_comparison_view(original_text, optimized_text):
    # Fix: Escape the curly braces in the HTML with double braces
    original_text_html = original_text.replace('\n', '<br>')
    optimized_text_html = optimized_text.replace('\n', '<br>')
    
    comparison_html = f"""
    <div style="display: flex; margin-top: 20px; gap: 20px; margin-bottom: 30px;">
        <div style="flex: 1; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h3 style="color: #333; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 1px solid #eee;">Original Resume</h3>
            <div style="white-space: pre-wrap; font-family: system-ui; color: #444; font-size: 14px; line-height: 1.6; max-height: 400px; overflow-y: auto;">
                {original_text_html}
            </div>
        </div>
        <div style="flex: 1; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h3 style="color: #1D9FF0; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 1px solid #eee;">Optimized Resume</h3>
            <div style="white-space: pre-wrap; font-family: system-ui; color: #444; font-size: 14px; line-height: 1.6; max-height: 400px; overflow-y: auto;">
                {optimized_text_html}
            </div>
        </div>
    </div>
    """
    components.html(comparison_html, height=500, scrolling=True)

def display_progress_animation():
    progress_html = """
    <div style="display: flex; justify-content: center; align-items: center; height: 100px;">
        <div class="loader"></div>
    </div>
    <style>
        .loader {
            border: 5px solid #f3f3f3;
            border-top: 5px solid #1D9FF0;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    """
    return components.html(progress_html, height=100)

# Add Font Awesome for icons
def add_font_awesome():
    font_awesome_html = """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    """
    components.html(font_awesome_html)

# Main App
def main():
    # Page config
    st.set_page_config(page_title="Resume Optimizer", layout="wide", initial_sidebar_state="collapsed")
    
    # Add fonts and icons
    add_font_awesome()
    
    # Apply custom CSS
    local_css("""
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            max-width: 1200px;
        }
        .stButton>button {
            background-color: #1D9FF0;
            color: white;
            font-size: 16px;
            padding: 10px 24px;
            border-radius: 8px;
            border: none;
            font-weight: 500;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #0F7EBD;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        body, [data-testid="stAppViewContainer"] {
            background-color: #f8f9fa !important;
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff;
        }
        /* Hide Streamlit branding */
        footer {
            visibility: hidden;
        }
    """)
    
    # App header
    render_header()
    
    # Create columns for layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Show custom upload area UI
        render_file_upload_area()
        
        # Actual file uploader (will be used under the hood)
        uploaded_file = st.file_uploader("", type=["pdf", "docx"], key="file_uploader", label_visibility="collapsed")
        
        # Process uploaded file
        resume_text = ""
        if uploaded_file is not None:
            file_extension = uploaded_file.name.split(".")[-1].lower()
            
            try:
                if file_extension == "pdf":
                    resume_text = extract_text_from_pdf(uploaded_file)
                    st.success(f"Successfully extracted text from {uploaded_file.name}")
                elif file_extension == "docx":
                    resume_text = extract_text_from_docx(uploaded_file)
                    st.success(f"Successfully extracted text from {uploaded_file.name}")
                else:
                    st.error("Unsupported file format!")
                
                # Clean the extracted text
                resume_text = clean_text(resume_text)
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    with col2:
        st.markdown("### Optimization Settings")
        
        job_role = st.text_input("Target Job Role", "Software Engineer")
        
        # Additional customization options
        with st.expander("Advanced Options", expanded=False):
            selected_skills = st.multiselect(
                "Key Skills to Highlight",
                ["Python", "JavaScript", "React", "Node.js", "Machine Learning", "Data Analysis", 
                 "Project Management", "Leadership", "Communication", "Problem Solving"],
                default=[]
            )
            
            optimization_focus = st.radio(
                "Optimization Focus",
                ["General Improvement", "Technical Skills", "Leadership & Management", "Academic Focus"],
                index=0
            )
            
            api_model = st.selectbox(
                "AI Model",
                ["mixtral-8x7b-32768", "llama3-70b-8192", "llama3-8b-8192"],
                index=0
            )
    
    # Create an optimize button
    if resume_text:
        if st.button("Optimize Resume", key="optimize_button", use_container_width=True):
            # Display progress indicator
            progress_placeholder = st.empty()
            with progress_placeholder.container():
                progress_indicator = display_progress_animation()
            
            # Perform optimization
            optimized_resume = optimize_resume_groq(
                resume_text, 
                job_role, 
                selected_skills if selected_skills else None, 
                optimization_focus if optimization_focus != "General Improvement" else None
            )
            
            # Remove progress indicator
            progress_placeholder.empty()
            
            # Display results in side-by-side view
            render_comparison_view(resume_text, optimized_resume)
            
            # Add download buttons
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download Optimized Resume as TXT",
                    data=optimized_resume,
                    file_name=f"optimized_{job_role.replace(' ', '_')}_resume.txt",
                    mime="text/plain",
                )
            with col2:
                st.info("💡 **Pro Tip:** Copy the optimized text and paste it back into your original resume document to maintain formatting.")

    # Show a message when no file is uploaded
    else:
        st.info("👆 Please upload your resume to get started.")
        
        # Sample features section
        st.markdown("### Features")
        features_html = """
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px;">
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
                <i class="fas fa-robot" style="font-size: 24px; color: #1D9FF0; margin-bottom: 10px;"></i>
                <h4 style="margin: 10px 0; color: #333;">AI-Powered Optimization</h4>
                <p style="color: #666; font-size: 14px;">Our AI analyzes your resume and optimizes it for your target role</p>
            </div>
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
                <i class="fas fa-search" style="font-size: 24px; color: #1D9FF0; margin-bottom: 10px;"></i>
                <h4 style="margin: 10px 0; color: #333;">ATS-Friendly</h4>
                <p style="color: #666; font-size: 14px;">Improve your chances of getting past Applicant Tracking Systems</p>
            </div>
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
                <i class="fas fa-bolt" style="font-size: 24px; color: #1D9FF0; margin-bottom: 10px;"></i>
                <h4 style="margin: 10px 0; color: #333;">Fast Results</h4>
                <p style="color: #666; font-size: 14px;">Get your optimized resume in seconds, not hours</p>
            </div>
        </div>
        """
        components.html(features_html, height=200)

if __name__ == "__main__":
    main()