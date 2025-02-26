import streamlit as st
import random
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json
import re
import requests
import os
import time

# Hide Streamlit default menu and footer
st.set_page_config(page_title="Soft Skills Evaluator", layout="wide")
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
    </style>
""", unsafe_allow_html=True)

# Groq API integration with hardcoded API key
def groq_analyze(text, question_type):
    """
    Uses Groq API to analyze interview responses based on different question types.
    Returns detailed feedback on the response quality.
    """
    # Directly use the integrated API key
    api_key = "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"
    
    # Construct prompt based on question type
    system_prompt = """You are an expert interview coach specializing in evaluating soft skills responses. 
    Analyze the following interview response and provide:
    1. A score from 1-10 based on response quality
    2. Brief feedback on strengths (max 2 points)
    3. Brief feedback on weaknesses (max 2 points)
    4. One specific improvement tip
    
    Format as JSON: {"score": 7.5, "feedback": "Your concise feedback here", "tip": "Your improvement tip here"}
    
    Focus on: specificity of examples, structure, reflection, results-orientation, and communication clarity."""
    
    # Add question-type specific instructions
    if "challenge" in question_type.lower() or "problem" in question_type.lower():
        system_prompt += " For this challenge/problem question, evaluate if they clearly identified the problem, explained their actions, and described results."
    elif "team" in question_type.lower() or "colleague" in question_type.lower() or "conflict" in question_type.lower():
        system_prompt += " For this teamwork/conflict question, evaluate their collaboration approach, role clarity, and resolution skills."
    
    user_prompt = f"Question: {question_type}\n\nResponse: {text}\n\nEvaluate this interview response."
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Try to parse the JSON response
            try:
                analysis = json.loads(content)
                # Ensure all required fields exist
                if "score" not in analysis:
                    analysis["score"] = 5.0
                if "feedback" not in analysis:
                    analysis["feedback"] = "Response analyzed."
                if "tip" not in analysis:
                    analysis["tip"] = "Focus on providing specific examples and clear structure."
                
                return analysis
            except json.JSONDecodeError:
                # If can't parse JSON, extract information manually using regex
                score_match = re.search(r'score"?\s*:\s*(\d+\.?\d*)', content)
                score = float(score_match.group(1)) if score_match else 5.0
                
                feedback_match = re.search(r'feedback"?\s*:\s*"([^"]+)"', content)
                feedback = feedback_match.group(1) if feedback_match else "Response analyzed."
                
                tip_match = re.search(r'tip"?\s*:\s*"([^"]+)"', content)
                tip = tip_match.group(1) if tip_match else "Focus on specific examples."
                
                return {
                    "feedback": feedback,
                    "score": score,
                    "tip": tip
                }
        else:
            st.error(f"Groq API Error: {response.status_code} - {response.text}")
            return fallback_analyze(text, question_type)
    except Exception as e:
        st.error(f"Error calling Groq API: {str(e)}")
        return fallback_analyze(text, question_type)

# Fallback analysis function (simplified version of the original grok_analyze)
def fallback_analyze(text, question_type):
    """
    Fallback analysis when Groq API is unavailable.
    """
    # Length-based metrics
    word_count = len(text.split())
    
    # Basic pattern matching for different response elements
    has_specific_example = bool(re.search(r'\b(for example|instance|specifically|when I|once I|during my)\b', text, re.IGNORECASE))
    has_reflection = bool(re.search(r'\b(learned|realized|understood|insight|growth|improved|discovered)\b', text, re.IGNORECASE))
    has_result = bool(re.search(r'\b(result|outcome|achieved|accomplishment|success|finally|ultimately)\b', text, re.IGNORECASE))
    
    # Calculate response quality score
    response_quality = 0.5  # Default middle score
    
    # Adjust based on response elements
    response_quality += 0.1 if has_specific_example else 0
    response_quality += 0.1 if has_reflection else 0
    response_quality += 0.1 if has_result else 0
    response_quality += 0.1 if word_count > 50 else 0
    
    # Convert to score out of 10
    score = 4.0 + (response_quality * 6.0)
    
    # Generate basic feedback
    strengths = []
    if has_specific_example: strengths.append("using concrete examples")
    if has_reflection: strengths.append("showing reflective thinking")
    if has_result: strengths.append("highlighting outcomes")
    
    weaknesses = []
    if not has_specific_example: weaknesses.append("specific examples")
    if not has_reflection: weaknesses.append("reflective insights")
    if not has_result: weaknesses.append("results focus")
    
    strengths_text = f"Strengths: {', '.join(strengths)}" if strengths else ""
    weaknesses_text = f"Areas to improve: {', '.join(weaknesses)}" if weaknesses else ""
    
    feedback = "Fallback analysis: " + strengths_text + " " + weaknesses_text
    
    tip = "Try to include specific examples, actions taken, and results achieved in your response."
    
    return {
        "feedback": feedback.strip(),
        "score": round(score, 1),
        "tip": tip
    }

def analyze_text(text, question):
    # First run basic sentiment analysis
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    compound_score = sentiment["compound"]
    
    sentiment_score = round((compound_score + 1) * 4.5 + 1, 1)
    
    # Then run Groq AI analysis
    groq_results = groq_analyze(text, question)
    
    # Combine the scores (70% Groq, 30% sentiment)
    combined_score = round((groq_results["score"] * 0.7) + (sentiment_score * 0.3), 1)
    combined_score = min(max(combined_score, 1), 10)  # Ensure score stays between 1-10
    
    # Determine sentiment-based feedback prefix
    if compound_score > 0.5:
        sentiment_feedback = "Positive and confident tone. "
    elif compound_score < -0.5:
        sentiment_feedback = "Your tone seems quite negative. Consider a more positive approach. "
    elif compound_score < -0.2:
        sentiment_feedback = "Your tone leans negative. Adding optimism could help. "
    else:
        sentiment_feedback = ""
    
    # Combine feedback
    feedback = sentiment_feedback + groq_results["feedback"]
    
    return feedback, combined_score, groq_results["tip"]

def get_random_questions():
    questions = [
        "Tell me about a time you faced a challenge at work and how you handled it.",
        "Describe a situation where you had to work as part of a team.",
        "How do you handle constructive criticism?",
        "Can you give an example of a time you had to solve a problem creatively?",
        "Describe a situation where you had to adapt to a significant change.",
        "What is your approach to managing tight deadlines?",
        "Tell me about a time you had to negotiate to achieve your goals.",
        "How do you prioritize tasks when you have multiple responsibilities?",
        "Describe how you would handle a conflict with a colleague.",
        "What strategies do you use to maintain work-life balance?",
    ]
    return random.sample(questions, 5)  # Select 5 unique random questions

# Custom header
def render_header():
    st.markdown("""
    <div style="background-color: #5436DA; padding: 20px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h1 style="color: white; text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0;">
            Groq-Powered Soft Skills Evaluator
        </h1>
        <p style="color: white; text-align: center; font-size: 18px; margin-top: 10px;">
            Enhance your interview responses with AI-powered feedback and scoring
        </p>
    </div>
    """, unsafe_allow_html=True)

# Render feedback cards
def render_feedback(question, feedback, score, tip, idx):
    score_color = "#28a745" if score >= 7 else "#ffc107" if score >= 4 else "#dc3545"
    st.markdown(f"""
    <div style="background-color: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; border-left: 5px solid {score_color}; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
        <h4 style="color: #333; margin-bottom: 10px;">Question {idx}: {question}</h4>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <p style="font-weight: bold; color: {score_color}; margin: 0;">{feedback}</p>
            <div style="background-color: {score_color}; color: white; border-radius: 50px; padding: 5px 15px; font-weight: bold;">
                {score}/10
            </div>
        </div>
        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 8px; display: flex; align-items: center;">
            <span style="color: #5436DA; margin-right: 10px;">💡</span>
            <p style="margin: 0; color: #666;">{tip}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Render the final score card
def render_final_score(total_score):
    percentage = (total_score / 50) * 100
    score_range = "Excellent" if percentage >= 80 else "Good" if percentage >= 60 else "Needs Improvement"
    score_color = "#28a745" if percentage >= 80 else "#ffc107" if percentage >= 60 else "#dc3545"
    
    st.markdown(f"""
    <div style="background-color: white; border-radius: 10px; padding: 30px; margin: 20px 0; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
        <h2 style="color: #333; margin-bottom: 20px;">Your Final Assessment</h2>
        <div style="font-size: 48px; font-weight: bold; color: {score_color}; margin-bottom: 20px;">
            {total_score}/50
        </div>
        <div style="font-size: 24px; color: {score_color}; margin-bottom: 20px;">
            {score_range}
        </div>
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: left; max-width: 600px; margin: 0 auto;">
            <p style="margin: 0; color: #666; line-height: 1.6;">
                <span style="color: #5436DA; font-weight: bold;">Groq AI Analysis:</span> 
                The assessment used advanced language models to evaluate your responses based on structure, 
                specific examples, reflective thinking, and communication clarity. Continue practicing with a focus on 
                providing concrete examples and demonstrating your problem-solving approach.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_groq_info():
    st.sidebar.markdown("""
    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 10px;">
        <h3 style="color: #5436DA; margin-top: 0;">About Groq AI Analysis</h3>
        <p style="font-size: 14px; color: #333;">
            This evaluator uses the powerful Groq API (with Llama 3 70B model) to analyze interview responses.
            The AI evaluates:
        </p>
        <ul style="font-size: 14px; color: #333; padding-left: 20px;">
            <li>Use of specific examples</li>
            <li>Problem-solution structure</li>
            <li>Communication clarity</li>
            <li>Reflective thinking</li>
            <li>Results orientation</li>
            <li>Emotional intelligence</li>
        </ul>
        <p style="font-size: 14px; color: #333; margin-top: 15px;">
            Each question type has specific evaluation criteria tailored to best practices for that type of interview question.
        </p>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Initialize session state
    if "questions" not in st.session_state:
        st.session_state.questions = get_random_questions()
    
    if "analyzed" not in st.session_state:
        st.session_state.analyzed = False
    
    # Render Groq info in sidebar
    render_groq_info()
    
    # Render custom header
    render_header()
    
    # Instructions
    st.markdown("""
    <div style="background-color: #f0f7fb; padding: 15px; border-radius: 8px; border-left: 5px solid #5436DA; margin-bottom: 25px;">
        <p style="margin: 0; color: #333; font-size: 16px;">
            <strong>Instructions:</strong> Answer each question as if you were in a job interview. 
            Our Groq-powered AI will analyze your responses for structure, specific examples, and communication effectiveness.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Collect responses using standard Streamlit components
    responses = []
    for idx, question in enumerate(st.session_state.questions, start=1):
        question_key = f"q{idx}"
        
        st.markdown(f"""
        <h3 style="color: #5436DA; margin-bottom: 10px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            Question {idx}: {question}
        </h3>
        """, unsafe_allow_html=True)
        
        # Standard Streamlit text area instead of custom HTML
        user_input = st.text_area(
            label=f"Your response to Question {idx}",
            key=question_key,
            placeholder="Type your response here...",
            height=120,
            label_visibility="collapsed"
        )
        
        # Character count display
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; margin-top: -15px; margin-bottom: 20px;">
            <small style="color: #666;">{len(user_input)} characters</small>
            <small style="color: #666;">Aim for 100-300 characters for best results</small>
        </div>
        """, unsafe_allow_html=True)
        
        responses.append((question, user_input))
    
    # Analyze button with Groq branding
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "Analyze with Groq AI", 
            type="primary",
            use_container_width=True,
            key="analyze_button"
        )
    
    # Center the button and style
    st.markdown("""
    <style>
        div[data-testid="stButton"] button {
            background-color: #5436DA !important;
            color: white !important;
            padding: 12px 30px !important;
            font-size: 18px !important;
            font-weight: bold !important;
        }
        div[data-testid="stButton"] button:hover {
            background-color: #4526ba !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    if analyze_button:
        # Add a spinner for "Groq is thinking" effect
        with st.spinner("Groq AI is analyzing your responses..."):
            # Simulate thinking time for better UX (but shorter than original)
            time.sleep(0.8)
            st.session_state.analyzed = True
    
    # Display results if analyzed
    if st.session_state.analyzed:
        st.markdown("""
        <h2 style="color: #333; text-align: center; margin: 30px 0 20px 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            Groq's Assessment of Your Responses
        </h2>
        """, unsafe_allow_html=True)
        
        total_score = 0
        
        for idx, (question, user_input) in enumerate(responses, start=1):
            if user_input.strip():
                feedback, score, tip = analyze_text(user_input, question)
                total_score += score
                render_feedback(question, feedback, score, tip, idx)
            else:
                empty_feedback = "No response provided."
                empty_tip = "Always provide a thoughtful answer to showcase your communication skills."
                render_feedback(question, empty_feedback, 0, empty_tip, idx)
        
        render_final_score(total_score)
        
        # Reset button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Try with New Questions", key="reset_button"):
                # Generate new questions
                st.session_state.questions = get_random_questions()
                # Reset the analyzed state
                st.session_state.analyzed = False
                # Clear all text inputs by removing them from session state
                for i in range(1, 6):
                    if f"q{i}" in st.session_state:
                        del st.session_state[f"q{i}"]
                # Rerun the app to reflect changes
                st.rerun()

if __name__ == "__main__":
    main()