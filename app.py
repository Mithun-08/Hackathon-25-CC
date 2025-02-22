from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Set OpenAI API ;Key
openai.api_key = "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"
if not openai.api_key:
    raise ValueError("Missing OpenAI API Key! Set OPENAI_API_KEY as an environment variable.")

# Root Route (to prevent 404)
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Flask API is running!"})

# Chat Endpoint
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' in request"}), 400
        
        user_message = data["message"]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_message}]
        )

        return jsonify({"response": response["choices"][0]["message"]["content"]})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
