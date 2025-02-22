from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Configure your OpenAI API key
openai.api_key = os.getenv("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") 
@app.route('/api/optimize_resume', methods=['POST'])
def optimize_resume():
    data = request.json
    resume_text = data.get("resume")
    
    if not resume_text:
        return jsonify({"error": "No resume provided"}), 400

    prompt = f"Optimize this resume for ATS compliance and clarity:\n\n{resume_text}\n\nOptimized version:"
    
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=200,
            temperature=0.7
        )
        optimized_resume = response.choices[0].text.strip()
        return jsonify({"optimized_resume": optimized_resume})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
