from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import json
import os

app = Flask(__name__)
CORS(app)

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash-lite")


@app.route("/")
def home():
    return send_from_directory(app.root_path, "index.html")


@app.route("/style.css")
def serve_css():
    return send_from_directory(app.root_path, "style.css")


@app.route("/script.js")
def serve_js():
    return send_from_directory(app.root_path, "script.js")

@app.route("/api/analyze", methods=["POST"])
def analyze_claim():

    data = request.get_json(silent=True) or {}
    user_input = data.get("claim", "")

    if not isinstance(user_input, str) or not user_input.strip():
        return jsonify({
            "error": "Please enter a valid claim."
        }), 400

    prompt = f"""
    You are a strict AI fact-checking system.
    Return ONLY valid JSON.
    Do NOT include any extra text or markdown formatting like ```json.

    Format:
    {{
        "verdict": "Likely True" or "Uncertain" or "Fake News",
        "confidence": integer between 0 and 100,
        "reason": "clear and short explanation",
        "category": "Health", "Politics", "Tech", etc.
    }}

    Claim: {user_input}
    """

    try:
        response = model.generate_content(prompt)

        result_text = response.text.strip()

        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "").replace("```", "").strip()
        elif result_text.startswith("```"):
            result_text = result_text.replace("```", "").strip()

        result = json.loads(result_text)

        return jsonify(result)

    except Exception:
        app.logger.exception("News analysis failed")
        return jsonify({
            "error": "Unable to analyze the claim right now."
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
