import streamlit as st
import groq
import streamlit.components.v1 as components

# Configure Groq API Key
GROQ_API_KEY = "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"

# Initialize Groq Client
client = groq.Groq(api_key=GROQ_API_KEY)

# Streamlit App Configuration
st.set_page_config(page_title="Interview Prep", layout="wide")

# Custom Component for better styling
def custom_html_component():
    custom_css = """
    <style>
        body {
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }
        .interview-container {
            max-width: 100%;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background-color: #ffffff;
            margin-bottom: 20px;
        }
        .logo-animation {
            text-align: center;
            margin-bottom: 20px;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .pulse {
            animation: pulse 2s infinite ease-in-out;
        }
    </style>
    
    <div class="interview-container">
        <div class="logo-animation">
            <svg width="120" height="120" class="pulse">
                <circle cx="60" cy="60" r="50" fill="#1D9FF0" />
                <text x="60" y="65" text-anchor="middle" fill="white" font-size="16px" font-weight="bold">PREP</text>
            </svg>
        </div>
        <h1 style="color: #1D9FF0; text-align: center; font-size: 36px; font-weight: bold;">Interview Preparation</h1>
        <p style="color: #555555; text-align: center; font-size: 20px; margin-bottom: 30px;">Practice with AI-generated interview questions</p>
    </div>
    
    <script>
        // Add some interactivity
        document.addEventListener('DOMContentLoaded', function() {
            // This script would handle any client-side interactivity
            console.log('Interview preparation app loaded');
        });
    </script>
    """
    components.html(custom_css, height=280)

# Custom CSS for the rest of the components
st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #f9f9f9 !important;
        }
        .stTextInput label, .stTextArea label {
            color: #000000 !important;
            font-weight: bold;
            font-size: 16px !important;
        }
        .stButton>button {
            background-color: #1D9FF0;
            color: white;
            font-size: 16px;
            padding: 10px 24px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stButton>button:hover {
            background-color: #1578C2;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .question-box {
            background-color: #f0f7ff;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #1D9FF0;
            margin-bottom: 15px;
            font-size: 18px;
            color: #333333;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        .question-box:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transform: translateX(3px);
        }
        .feedback-box {
            background-color: #e9f5e9;
            color: #000000;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px groove #28a745;
            margin: 20px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .text-area-container {
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .stTextArea>div>div>textarea {
            border: 1px solid #ddd !important;
            border-radius: 6px !important;
            padding: 12px !important;
            font-size: 16px !important;
        }
        /* Progress bar styling */
        .stProgress > div > div > div {
            background-color: #1D9FF0 !important;
        }
        /* Spinner styling */
        .stSpinner > div {
            border-top-color: #1D9FF0 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Use custom component for header
custom_html_component()

# Create columns for better layout
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # User input for job role
    job_role = st.text_input("Enter the Job Role:")

# Function to validate job role
def is_valid_job_role(job_role):
    return bool(job_role.strip()) and len(job_role) > 2

# Function to generate exactly 5 open-ended questions using Groq AI
@st.cache_data(ttl=3600)  # Cache results for 1 hour to reduce API calls
def generate_questions(job_role):
    prompt = f"""
    Generate exactly 5 open-ended interview questions for a {job_role} interview.
    Each question should assess technical knowledge, problem-solving skills, or behavioral competencies.
    Format the output strictly as follows:

    1. Question 1 text
    2. Question 2 text
    3. Question 3 text
    4. Question 4 text
    5. Question 5 text
    """

    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an expert interviewer helping candidates prepare for job interviews."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        questions = response.choices[0].message.content.strip().split("\n")
        return questions[:5] if len(questions) >= 5 else questions  # Ensure exactly 5 questions
    except Exception as e:
        return [f"Error generating questions: {str(e)}"]

# Function to get general AI feedback based on all answers
def get_general_feedback(questions_responses):
    prompt = "Analyze the following interview answers and provide general feedback. Identify overall strengths and areas for improvement.\n\n"
    for i, (question, answer) in enumerate(questions_responses.items(), start=1):
        if answer.strip():
            prompt += f"Question {i}: {question}\nAnswer: {answer}\n\n"

    prompt += """
    Based on the answers, analyze the candidate's overall performance. Provide:
    - Key strengths in their responses
    - Areas where improvement is needed
    - Any specific advice for better performance
    """

    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an expert hiring manager providing insightful feedback on interview answers."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating feedback: {str(e)}"

# Custom JavaScript for more interactive experience
def add_interactivity():
    js = """
    <script>
    // Function to add subtle animation when questions appear
    function animateQuestions() {
        const questions = document.querySelectorAll('.question-box');
        questions.forEach((q, i) => {
            setTimeout(() => {
                q.style.opacity = '1';
                q.style.transform = 'translateX(0)';
            }, i * 200);
        });
    }
    
    // Execute when loaded
    document.addEventListener('DOMContentLoaded', function() {
        animateQuestions();
        
        // Add click event to highlight current question
        document.querySelectorAll('.question-box').forEach(q => {
            q.addEventListener('click', function() {
                document.querySelectorAll('.question-box').forEach(box => {
                    box.style.borderLeftColor = '#1D9FF0';
                });
                this.style.borderLeftColor = '#FFA500';
            });
        });
    });
    </script>
    
    <style>
    .question-box {
        opacity: 0;
        transform: translateX(-10px);
        transition: opacity 0.5s ease, transform 0.5s ease;
    }
    </style>
    """
    components.html(js, height=0)

# Generate and display questions only if a valid job role is provided
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Start Mock Interview"):
        if not is_valid_job_role(job_role):
            st.error("Please enter a valid job description before starting.")
        else:
            with st.spinner("Generating personalized interview questions..."):
                # Add a progress bar for better UX
                progress_bar = st.progress(0)
                for i in range(100):
                    # Update progress bar
                    progress_bar.progress(i + 1)
                    
                questions = generate_questions(job_role)
                
                if not questions or "Error" in questions[0]:
                    st.error("Failed to generate questions. Please try again.")
                else:
                    st.session_state["questions"] = questions
                    st.session_state["responses"] = {q: "" for q in questions}
                    st.session_state["submitted"] = False
                    
                    # Add success message with animation
                    st.success("Questions generated successfully!")

# Display questions and allow user input
if "questions" in st.session_state and not st.session_state.get("submitted", False):
    st.subheader(f"📝 Mock Interview for: {job_role}")
    
    add_interactivity()  # Add the interactive JavaScript elements
    
    for idx, question in enumerate(st.session_state["questions"], start=1):
        st.markdown(f'<div class="question-box" id="question-{idx}">Q{idx}: {question}</div>', unsafe_allow_html=True)
        
        # Create a visual container for text areas
        st.markdown('<div class="text-area-container">', unsafe_allow_html=True)
        st.session_state["responses"][question] = st.text_area(f"Your Answer for Q{idx}:", key=f"q{idx}", height=150)
        st.markdown('</div>', unsafe_allow_html=True)

    # Submit button with better positioning
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Submit Answers for Feedback"):
            # Validate if at least one answer is provided
            if any(ans.strip() for ans in st.session_state["responses"].values()):
                st.session_state["submitted"] = True
            else:
                st.warning("Please provide at least one answer before submitting.")

# Display feedback after submission
if st.session_state.get("submitted", False):
    st.subheader("🔍 AI Performance Analysis")

    # Filter out unanswered questions
    answered_questions = {q: ans for q, ans in st.session_state["responses"].items() if ans.strip()}
    
    if answered_questions:
        with st.spinner("Analyzing your answers..."):
            general_feedback = get_general_feedback(answered_questions)

        # Display feedback with better formatting
        st.markdown(f'<div class="feedback-box"><h3>General Performance Feedback:</h3>{general_feedback}</div>', unsafe_allow_html=True)
        
        # Add restart option
        if st.button("Start a New Interview"):
            # Clear session state
            for key in ["questions", "responses", "submitted"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.experimental_rerun()
    else:
        st.warning("No answers submitted. Please provide responses before submitting.")

# Add footer with components.v1
footer_html = """
<div style="margin-top: 50px; text-align: center; color: #888; padding: 20px;">
    <p>Powered by AI | Interview Preparation Tool</p>
    <p style="font-size: 12px;">© 2025 - Using Groq API and Streamlit</p>
</div>
"""
components.html(footer_html, height=100)