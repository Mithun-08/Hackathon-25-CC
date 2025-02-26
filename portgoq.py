import streamlit as st
import streamlit.components.v1 as components
import base64
import re
import io
import PyPDF2
import docx

# Streamlit Page Config
st.set_page_config(page_title="Portfolio Builder", layout="wide")

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
        }
        .success-message {
            color: black !important;
            font-weight: bold;
            background-color: rgba(0, 255, 0, 0.2);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            margin-top: 10px;
        }
        .preview-container {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .upload-section {
            border: 2px dashed #1D9FF0;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }
        .resume-info {
            background-color: #e8f4ff;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for form values
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {
        'name': '',
        'email': '',
        'skills': '',
        'linkedin': '',
        'github': '',
        'bio': '',
        'projects': []
    }

# Resume parser functions - simplified versions
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {e}")
        return ""

def extract_email(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else ''

def extract_linkedin(text):
    linkedin_patterns = [
        r'linkedin\.com/in/[\w-]+',
        r'linkedin\.com/profile/[\w-]+'
    ]
    for pattern in linkedin_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return f"https://www.{matches[0]}"
    return ''

def extract_github(text):
    github_patterns = [
        r'github\.com/[\w-]+',
    ]
    for pattern in github_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return f"https://www.{matches[0]}"
    return ''

def extract_skills(text):
    # Simplified skills extraction with common tech skills
    common_skills = [
        "python", "javascript", "java", "c++", "c#", "ruby", "php", "swift",
        "kotlin", "go", "rust", "typescript", "html", "css", "sql", "nosql",
        "react", "angular", "vue", "node", "django", "flask", "spring", "asp.net",
        "docker", "kubernetes", "aws", "azure", "gcp", "devops", "ci/cd",
        "git", "machine learning", "ai", "data science", "data analysis"
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in common_skills:
        if skill in text_lower:
            found_skills.append(skill)
    
    return ", ".join(found_skills)

def extract_name(text):
    # Simplified name extraction - first non-empty line that's not too long
    lines = text.split("\n")
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if line and 2 <= len(line.split()) <= 4 and len(line) < 40:
            return line
    return ""

def extract_projects(text):
    # Simplistic project identification
    # Look for sections with "project" in the heading
    project_keywords = ["project", "project experience", "projects"]
    lines = text.split("\n")
    
    projects = []
    in_project_section = False
    current_project = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a project section header
        is_project_header = any(keyword.lower() in line.lower() for keyword in project_keywords)
        
        if is_project_header:
            in_project_section = True
            continue
            
        # If we're in a project section and this looks like a project title
        if in_project_section and len(line) < 100 and line.strip():
            # If we already have a project in progress, save it
            if current_project:
                projects.append(current_project)
                
            # Start a new project
            current_project = {
                "title": line,
                "description": ""
            }
        # If we have a current project, add to its description
        elif current_project and line:
            if len(current_project["description"]) < 200:  # Limit description length
                current_project["description"] += line + " "
                
    # Add the last project if there is one
    if current_project:
        projects.append(current_project)
        
    # If we couldn't find explicit projects, look for keywords
    if not projects:
        project_indicators = ["developed", "created", "built", "implemented", "designed"]
        potential_projects = []
        
        for i, line in enumerate(lines):
            if any(indicator in line.lower() for indicator in project_indicators) and len(line) < 100:
                description = ""
                # Get the next few lines as description
                for j in range(1, 4):
                    if i+j < len(lines) and lines[i+j].strip():
                        description += lines[i+j].strip() + " "
                
                if description:
                    potential_projects.append({
                        "title": line.strip(),
                        "description": description
                    })
        
        # Take the first 2 potential projects
        projects = potential_projects[:2]
    
    # If still no projects, create some placeholders
    if not projects:
        return []
    
    # Return up to 2 projects
    return projects[:2]

def generate_bio(text, name):
    # Simplified bio generation
    if not name:
        name = "Professional"
        
    # Look for role/title
    role_patterns = [
        r'(software developer|web developer|fullstack developer|frontend developer|backend developer)',
        r'(software engineer|systems engineer|devops engineer)',
        r'(data scientist|data analyst|machine learning engineer)',
        r'(product manager|project manager)'
    ]
    
    role = ""
    for pattern in role_patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            role = matches[0]
            if isinstance(role, tuple):  # Some regex engines return tuples
                role = role[0]
            break
            
    if not role:
        role = "software professional"
        
    # Check for years of experience
    year_pattern = r'(\d+)\+?\s*years?'
    year_matches = re.findall(year_pattern, text.lower())
    experience = ""
    if year_matches:
        experience = f" with {year_matches[0]}+ years of experience"
        
    return f"{name} is a passionate {role}{experience} specializing in technology and software solutions."

def parse_resume(file):
    file_extension = file.name.split('.')[-1].lower()
    
    try:
        if file_extension == 'pdf':
            text = extract_text_from_pdf(file)
        elif file_extension in ['docx', 'doc']:
            text = extract_text_from_docx(file)
        else:
            st.error("Unsupported file format. Please upload a PDF or DOCX file.")
            return None
            
        if not text:
            st.error("Could not extract text from your resume. The file might be corrupt or password-protected.")
            return None
        
        # Extract information
        name = extract_name(text)
        email = extract_email(text)
        linkedin = extract_linkedin(text)
        github = extract_github(text)
        skills = extract_skills(text)
        projects = extract_projects(text)
        bio = generate_bio(text, name)
        
        return {
            'name': name,
            'email': email,
            'linkedin': linkedin,
            'github': github,
            'skills': skills,
            'bio': bio,
            'projects': projects
        }
    except Exception as e:
        st.error(f"Error parsing resume: {e}")
        return None

# App title
st.markdown('<div class="main-title">Personal Portfolio Builder</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Upload your resume or fill in your details to generate a modern HTML portfolio page.</div>', unsafe_allow_html=True)

# Create two columns layout
col1, col2 = st.columns([1, 1.5])

with col1:
    # Resume upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.subheader("Upload Resume")
    st.write("Upload your resume to automatically fill in your details")
    
    resume_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "doc"])
    
    if resume_file is not None:
        with st.spinner("Extracting information from your resume..."):
            try:
                extracted_data = parse_resume(resume_file)
                if extracted_data:
                    st.session_state.extracted_data = extracted_data
                    st.success("Resume parsed successfully!")
            except Exception as e:
                st.error(f"Error during resume parsing: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display extracted information if available
    if st.session_state.extracted_data['name']:
        st.markdown('<div class="resume-info">', unsafe_allow_html=True)
        st.subheader("Extracted Information")
        st.write(f"**Name:** {st.session_state.extracted_data['name']}")
        st.write(f"**Email:** {st.session_state.extracted_data['email']}")
        if st.session_state.extracted_data['linkedin']:
            st.write(f"**LinkedIn:** Found ✓")
        if st.session_state.extracted_data['github']:
            st.write(f"**GitHub:** Found ✓")
        st.write(f"**Skills:** {st.session_state.extracted_data['skills']}")
        st.write(f"**Projects Found:** {len(st.session_state.extracted_data['projects'])}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # User form with pre-filled data from resume
    st.header("Edit Your Details")
    with st.form("portfolio_form"):
        # Pre-fill with extracted data if available
        name = st.text_input("Full Name", 
                           st.session_state.extracted_data['name'] if st.session_state.extracted_data['name'] else "",
                           placeholder="Enter here")
        
        bio = st.text_area("Short Bio", 
                          st.session_state.extracted_data['bio'] if st.session_state.extracted_data['bio'] else "",
                          placeholder="Enter here")
        
        # Contact info
        st.subheader("Contact Information")
        email = st.text_input("Email", 
                            st.session_state.extracted_data['email'] if st.session_state.extracted_data['email'] else "",
                            placeholder="Enter here")
        
        linkedin = st.text_input("LinkedIn Profile", 
                               st.session_state.extracted_data['linkedin'] if st.session_state.extracted_data['linkedin'] else "",
                               placeholder="Enter here")
        
        github = st.text_input("GitHub Profile", 
                             st.session_state.extracted_data['github'] if st.session_state.extracted_data['github'] else "",
                             placeholder="Enter here")
        
        # Skills Section
        st.subheader("Skills")
        skills = st.text_area("Enter your skills (comma-separated)", 
                            st.session_state.extracted_data['skills'] if st.session_state.extracted_data['skills'] else "",
                            placeholder="Enter here")
        
        # Projects Section
        st.subheader("Projects")
        
        # Project 1
        project1 = st.text_input("Project 1 Title", 
                               st.session_state.extracted_data['projects'][0]['title'] if st.session_state.extracted_data['projects'] and len(st.session_state.extracted_data['projects']) > 0 else "",
                               placeholder="Enter here")
        
        project1_desc = st.text_area("Project 1 Description", 
                                    st.session_state.extracted_data['projects'][0]['description'] if st.session_state.extracted_data['projects'] and len(st.session_state.extracted_data['projects']) > 0 else "",
                                    placeholder="Enter here")
        
        # Project 2
        project2 = st.text_input("Project 2 Title", 
                               st.session_state.extracted_data['projects'][1]['title'] if st.session_state.extracted_data['projects'] and len(st.session_state.extracted_data['projects']) > 1 else "",
                               placeholder="Enter here")
        
        project2_desc = st.text_area("Project 2 Description", 
                                    st.session_state.extracted_data['projects'][1]['description'] if st.session_state.extracted_data['projects'] and len(st.session_state.extracted_data['projects']) > 1 else "",
                                    placeholder="Enter here")
        
        # Profile Picture Upload
        profile_pic = st.file_uploader("Upload a Profile Picture", type=["jpg", "png", "jpeg"])
        
        # Submit button
        submitted = st.form_submit_button("Update Preview")
        if submitted:
            st.session_state.form_submitted = True

# Function to get base64 encoding of the profile picture
def get_image_base64():
    if profile_pic:
        return base64.b64encode(profile_pic.getvalue()).decode()
    return None

# Generate HTML with Modern CSS
def generate_html(for_preview=False):
    img_base64 = get_image_base64()
    img_tag = ""
    if img_base64:
        img_tag = f'<img src="data:image/png;base64,{img_base64}" alt="{name}" />'
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{name} - Portfolio</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
                color: #333;
                text-align: center;
            }}
            .container {{
                width: {("100%" if for_preview else "80%")};
                margin: auto;
                background: white;
                box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
                border-radius: 12px;
                padding: 30px;
                {"margin-top: 30px;" if not for_preview else ""}
            }}
            img {{
                width: 150px;
                height: 150px;
                border-radius: 50%;
                border: 4px solid #007BFF;
                margin-top: 20px;
                object-fit: cover;
            }}
            h1 {{
                color: #007BFF;
                font-size: 28px;
                margin-top: 10px;
            }}
            .bio {{
                font-size: 18px;
                margin: 10px 0;
                color: #555;
            }}
            .skills, .projects {{
                margin-top: 30px;
                text-align: left;
                padding: 20px;
                background: #f9f9f9;
                border-radius: 10px;
            }}
            .skills h2, .projects h2 {{
                color: #007BFF;
            }}
            .links a {{
                display: inline-block;
                margin: 10px;
                padding: 10px 20px;
                background: #007BFF;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: 0.3s;
            }}
            .links a:hover {{
                background: #0056b3;
            }}
            .project-item {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {img_tag}
            <h1>{name}</h1>
            <p class="bio">{bio}</p>
            <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
            
            <div class="links">
                <a href="{linkedin}" target="_blank">LinkedIn</a>
                <a href="{github}" target="_blank">GitHub</a>
            </div>

            <div class="skills">
                <h2>Skills</h2>
                <p>{skills}</p>
            </div>

            <div class="projects">
                <h2>Projects</h2>
                <div class="project-item">
                    <h3>{project1}</h3>
                    <p>{project1_desc}</p>
                </div>
                <div class="project-item">
                    <h3>{project2}</h3>
                    <p>{project2_desc}</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template

# Display preview and download in the second column
with col2:
    st.header("Portfolio Preview")
    
    # Always show a preview, which updates when the form is submitted
    html_content = generate_html(for_preview=True)
    
    with st.container():
        st.markdown('<div class="preview-container">', unsafe_allow_html=True)
        components.html(html_content, height=600, scrolling=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Download button (always available)
    download_html = generate_html(for_preview=False)
    
    # Create a download button
    st.download_button(
        label="Download Portfolio HTML",
        data=download_html,
        file_name="portfolio.html",
        mime="text/html",
    )
    
    # Success message
    if st.session_state.form_submitted:
        st.markdown('<p class="success-message">✅ Portfolio preview updated! You can download the HTML file.</p>', unsafe_allow_html=True)
    elif resume_file and st.session_state.extracted_data['name']:
        st.markdown('<p class="success-message">✅ Resume data loaded! Review and update details if needed.</p>', unsafe_allow_html=True)