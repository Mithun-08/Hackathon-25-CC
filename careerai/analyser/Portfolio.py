import streamlit as st
import os

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
        .success-message {
            color: black !important;
            font-weight: bold;
            background-color: rgba(0, 255, 0, 0.2);  /* Translucent green */
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# App title
st.markdown('<div class="main-title">Personal Portfolio Builder</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Fill in your details to generate a modern HTML portfolio page.</div>', unsafe_allow_html=True)

# Sidebar Inputs
st.sidebar.header("Enter Your Details")
name = st.sidebar.text_input("Full Name", "John Doe")
bio = st.sidebar.text_area("Short Bio", "A passionate software developer with expertise in Python and AI.")
email = st.sidebar.text_input("Email", "johndoe@example.com")
linkedin = st.sidebar.text_input("LinkedIn Profile", "https://www.linkedin.com/in/johndoe/")
github = st.sidebar.text_input("GitHub Profile", "https://github.com/johndoe")

# Skills Section
st.sidebar.subheader("Skills")
skills = st.sidebar.text_area("Enter your skills (comma-separated)", "Python, JavaScript, React, AI")

# Projects Section
st.sidebar.subheader("Projects")
project1 = st.sidebar.text_input("Project 1 Title", "AI Chatbot")
project1_desc = st.sidebar.text_area("Project 1 Description", "Developed an AI-based chatbot using Python and NLP.")
project2 = st.sidebar.text_input("Project 2 Title", "E-commerce Website")
project2_desc = st.sidebar.text_area("Project 2 Description", "Built an e-commerce website using Django and React.")

# Profile Picture Upload
profile_pic = st.sidebar.file_uploader("Upload a Profile Picture", type=["jpg", "png", "jpeg"])

# Save uploaded image
image_path = None
if profile_pic:
    image_path = os.path.join("profile_pic.png")
    with open(image_path, "wb") as f:
        f.write(profile_pic.getbuffer())

# Generate HTML with Modern CSS
def generate_html():
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
                width: 80%;
                margin: auto;
                background: white;
                box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
                border-radius: 12px;
                padding: 30px;
                margin-top: 30px;
            }}
            img {{
                width: 150px;
                height: 150px;
                border-radius: 50%;
                border: 4px solid #007BFF;
                margin-top: 20px;
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
            {"<img src='profile_pic.png'>" if profile_pic else ""}
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
    
    # Save HTML file
    html_file = "portfolio.html"
    with open(html_file, "w", encoding="utf-8") as file:
        file.write(html_template)
    return html_file

# Generate & Download Portfolio
if st.button("Generate Portfolio HTML"):
    html_file = generate_html()
    with open(html_file, "rb") as file:
        st.download_button("Download Portfolio HTML", file, file_name="portfolio.html", mime="text/html")

# Success message with green tick and translucent green background
st.markdown('<p class="success-message">✅ Portfolio HTML file is ready for download!</p>', unsafe_allow_html=True)
