import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import plotly.express as px
import pandas as pd

# Set page config
st.set_page_config(page_title="careerDrive", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .nav-container {
        background-color: #111;
        padding: 15px 40px;
        border-radius: 10px;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .nav-container h3 {
        color: lightblue;
        margin: 0;
    }
    
    .nav-links {
        display: flex;
        gap: 15px;
    }
    
    .nav-links a {
        color: white;
        text-decoration: none;
        font-weight: bold;
        padding: 10px 15px;
        border-radius: 8px;
        background: linear-gradient(45deg, #6a11cb, #2575fc);
        transition: all 0.3s ease-in-out;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    .nav-links a:hover {
        background: linear-gradient(45deg, #2575fc, #6a11cb);
        transform: scale(1.05);
        box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.4);
    }

    .main-container {
        padding-top: 80px; /* Adjust padding for fixed navbar */
    }

    /* Unique styling for CareerDrive */
    .career-drive-title {
        font-size: 2.5em;
        font-weight: 600;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 8px rgba(0, 123, 255, 0.5);
        animation: pulse 2s infinite;
    }

    /* Animation keyframes */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Navigation Bar using Streamlit Columns
with st.container():
    col1, col2 = st.columns([1, 3])  # Adjust column width
    with col1:
        st.markdown("<h3 class='career-drive-title'>CareerDrive</h3>", unsafe_allow_html=True)
    with col2:
        st.markdown(
            """
            <div class='nav-links'>
                <a href='https://portfolio-ca.streamlit.app/' target='_blank'>Portfolio Builder</a>
                <a href='https://analyser-ca.streamlit.app' target='_blank'>Skill Analysis</a>
                <a href='https://optimizer-careerai.streamlit.app/' target='_blank'>Resume Optimiser</a>
                <a href='https://softskill-careerai.streamlit.app/' target='_blank'>Soft-Skills Test</a>
                <a href='https://test-careerai.streamlit.app/' target='_blank'>Mock Interview</a>
                <a href='#contact'>Contact Us</a>
            </div>
            """,
            unsafe_allow_html=True
        )
st.write("Navbar rendered")  # Debug

# Main Content
st.markdown("<div class='main-container'>", unsafe_allow_html=True)

st.title("AI-Powered Personalized Job Assistant")
st.write("Navigating your career journey has never been easier. Our intelligent platform helps you stand out in the competitive job market with a suite of powerful tools:")

# Features
st.subheader("Our Features")
st.markdown("""
- **Resume Optimizer** – Enhance your resume with AI-driven suggestions to match job requirements.
- **Interview Preparation** – Get tailored practice questions and expert tips to ace your interviews.
- **Resume Analysis** – Receive in-depth feedback on your resume to improve its impact.
- **Soft Skills Test** – Assess and improve your communication, teamwork, and leadership skills.
- **Portfolio Builder** – Showcase your projects and achievements in a professional online portfolio.
""")

# Image
image_url = "https://resume.io/assets/landing/home/hero/hero-c5cd61805c7bfbfb6b968731e97cdebbad21e22c266ddfdb9af831bbfe5b8f1d.png"

# Download image with error handling
response = requests.get(image_url)
if response.status_code == 200:
    try:
        image = Image.open(BytesIO(response.content))
        st.markdown(
            """
            <style>
            .centered-image {
                display: block;
                margin-left: auto;
                margin-right: auto;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown('<div class="centered-image">', unsafe_allow_html=True)
        st.image(image, caption="AI Resume Assistant", use_container_width=False, output_format="PNG")
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.write(f"Error loading image: {e}")
else:
    st.write("Failed to load image")
st.write("Image rendered")  # Debug

# Interactive Graph: Time vs. Number of Employees (Line Graph)  
st.subheader("Employee Growth Over Time")
# Sample data
data = pd.DataFrame({
    "Time": ["FEB 22", "FEB 23", "FEB 24", "FEB 25", "FEB 26"],
    "Employees": [0, 12, 42, 43, 69]
})
st.write("Graph data:", data)  # Debug

# Create an interactive line chart with Plotly
fig = px.line(
    data,
    x="Time",
    y="Employees",
    title="Employee Growth Over Time",
    labels={"Employees": "Number of Employees", "Time": "Year"},
    line_shape="linear"
)

# Customize layout
fig.update_layout(
    height=400,
    width=800
)

# Display the interactive graph
st.plotly_chart(fig, use_container_width=True)
st.write("Graph rendered")  # Debug

# Contact Section
st.markdown("<div id='contact'>", unsafe_allow_html=True)
st.subheader("Contact Us")
st.write("📧 Email: sahishnu24110007@snuchennai.edu.in")
st.write("📞 Phone: +91 99489351201")
st.write("📍 Address: SHIV NADAR UNIVERSITY ,Chennai ")
st.markdown("</div>", unsafe_allow_html=True)
st.write("Contact rendered")  # Debug