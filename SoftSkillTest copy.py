import streamlit as st
import random
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Custom CSS Styling for Blue Heading and Black Text
st.markdown("""
    <style>
        body, [data-testid="stAppViewContainer"] {
            background-color: #ffffff !important;
        }
        h1 {
            color: #1D9FF0 !important; /* Blue color for main heading */
            text-align: center;
        }
        h2, h3, h4, h5, h6, p, label {
            color: black !important; /* Black color for all subheadings and text */
        }
        .stTextInput>div>div>input, .stTextArea>div>textarea {
            background-color: #ffffff !important;
            color: #333333 !important;
            font-size: 16px !important;
            border: 1px solid #cccccc !important;
            border-radius: 8px !important;
            padding: 10px !important;
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
    </style>
""", unsafe_allow_html=True)

def analyze_text(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    compound_score = sentiment["compound"]
    
    score = round((compound_score + 1) * 4.5 + 1, 1)  # Adjusted scoring to avoid always neutral responses
    
    if compound_score > 0.5:
        return "Positive and confident response!", min(score, 9.5), "Keep up the confidence and ensure clarity in your answers."
    elif compound_score < -0.5:
        return "Your response seems quite negative. Try to be more optimistic and constructive.", max(score, 1.0), "Consider focusing on strengths and lessons learned."
    elif compound_score < -0.2:
        return "Your response leans negative. Consider adding a positive outlook.", max(min(score, 4.0), 1.5), "Try to highlight your resilience and problem-solving ability."
    else:
        return "Neutral response. Try adding more enthusiasm and details!", max(min(score, 7.0), 2.0), "Use examples and confident wording to make your response more engaging."

def get_random_questions():
    questions = [
        "Tell me about a time you faced a challenge at work and how you handled it.",
        "Describe a situation where you had to work as part of a team.",
        "How do you handle constructive criticism?",
        "Can you give an example of a time you had to solve a problem creatively?",
        "Describe a situation where you had to adapt to a significant change.",
    ]
    return random.sample(questions, 5)  # Select 5 unique random questions

def main():
    st.title("AI-Powered Soft Skills Evaluator")  # Blue heading
    st.subheader("Test your communication and confidence skills!")  # Black subheading
    
    if "questions" not in st.session_state:
        st.session_state.questions = get_random_questions()
    
    total_score = 0
    responses = []
    
    for idx, question in enumerate(st.session_state.questions, start=1):
        st.write(f"**Question {idx}:** {question}")
        user_input = st.text_area(f"Your response for Question {idx}:", key=f"q{idx}")
        responses.append((question, user_input))
    
    if st.button("Analyze Responses"):
        st.subheader("Feedback & Scores")  # Black subheading
        for idx, (question, user_input) in enumerate(responses, start=1):
            if user_input.strip():
                feedback, score, tip = analyze_text(user_input)
                total_score += score
                st.write(f"**Question {idx}:** {question}")
                st.success(f"{feedback} Score: {score}/10")
                st.info(f"Tip: {tip}")
            else:
                st.warning(f"Question {idx}: No response provided.")
        
        st.subheader("Final Score")  # Black subheading
        st.write(f"Your total score: {total_score}/50")

if __name__ == "__main__":
    main()
