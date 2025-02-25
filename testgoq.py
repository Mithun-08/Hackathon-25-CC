import streamlit as st
import groq

# Configure Groq API Key (Replace with your actual key)
GROQ_API_KEY = "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"

# Initialize Groq Client
client = groq.Groq(api_key=GROQ_API_KEY)

# Streamlit App Configuration
st.set_page_config(page_title="Interview Prep", layout="wide")

# Custom CSS for Styling
st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        .title {
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            color: #1D9FF0;
            margin-top: 20px;
        }
        .subtitle {
            font-size: 20px;
            text-align: center;
            color: #555555;
            margin-bottom: 30px;
        }
        .stTextInput label {
            color: #000000 !important;
            font-weight: bold;
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
        .question-box {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #1D9FF0;
            margin-bottom: 10px;
            font-size: 18px;
            color: #333333;
        }
        .feedback-box {
            background-color: #e9f5e9;
            color: #000000;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px groove #28a745;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Page Title
st.markdown('<div class="title">Interview Preparation</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Practice with AI-generated interview questions</div>', unsafe_allow_html=True)

# User input for job role
job_role = st.text_input("Enter the Job Role:")

# Function to validate job role
def is_valid_job_role(job_role):
    return bool(job_role.strip()) and len(job_role) > 2  # Ensures job role is non-empty and meaningful

# Function to generate exactly 5 open-ended questions using Groq AI
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

# Function to get **general** AI feedback based on all answers
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

        return response.choices[0].message.content.strip()  # Single general feedback
    except Exception as e:
        return f"Error generating feedback: {str(e)}"

# Generate and display questions only if a valid job role is provided
if st.button("Start Mock Interview"):
    if not is_valid_job_role(job_role):
        st.error("Please enter a valid job description before starting.")
    else:
        with st.spinner("Generating questions..."):
            questions = generate_questions(job_role)
            
            if not questions or "Error" in questions[0]:
                st.error("Failed to generate questions. Please try again.")
            else:
                st.session_state["questions"] = questions
                st.session_state["responses"] = {q: "" for q in questions}
                st.session_state["submitted"] = False

# Display questions and allow user input
if "questions" in st.session_state and not st.session_state.get("submitted", False):
    st.subheader(f"Mock Interview for {job_role}")
    
    for idx, question in enumerate(st.session_state["questions"], start=1):
        st.markdown(f'<div class="question-box">Q{idx}: {question}</div>', unsafe_allow_html=True)
        st.session_state["responses"][question] = st.text_area(f"Your Answer for Q{idx}:", key=f"q{idx}")

    # Submit button
    if st.button("Submit Answers"):
        st.session_state["submitted"] = True  # Mark as submitted

# Display **General** feedback after submission
if st.session_state.get("submitted", False):
    st.subheader("Overall AI Feedback")

    # Filter out unanswered questions
    answered_questions = {q: ans for q, ans in st.session_state["responses"].items() if ans.strip()}
    
    if answered_questions:
        with st.spinner("Generating feedback..."):
            general_feedback = get_general_feedback(answered_questions)

        st.markdown(f'<div class="feedback-box"><b>General Performance Feedback:</b><br>{general_feedback}</div>', unsafe_allow_html=True)
    else:
        st.warning("No answers submitted. Please provide responses before submitting.")
