from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # Import CORS for cross-origin requests
import json
import requests
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# === Configuration ===
API_KEY = "AIzaSyCHcavN8CMNDIy_DNWbtZ69_XmIN37BMgI"  

# === Load Scraped Data ===
def load_scraped_data():
    if os.path.exists("scraped_content.json"):
        with open("scraped_content.json", "r") as file:
            return json.load(file)
    return {}

scraped_data = load_scraped_data()

# === Gemini API Request Function ===
def ask_gemini(category, question):
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}

    content = scraped_data.get(category, "No information available for this category.")
    
    data = {
        "contents": [{"parts": [{"text": f"Category: {category}\n\nContext:\n{content}\n\nQuestion: {question}"}]}],
    }

    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code == 200:
        try:
            # Extract the actual content from the response
            return response.json()["candidates"][0]["content"]
        except (KeyError, IndexError):
            return "Unexpected response format from Gemini API."
    else:
        return f"Request failed with status code: {response.status_code}"

# === Flask Routes ===
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Invalid request"}), 400

    category = data.get("category", "General")
    question = data["question"]

    # Fetch real response from Gemini API
    answer = ask_gemini(category, question)

    return jsonify({"answer": answer})  # Return the actual response from Gemini

# === Run Flask App ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT dynamically
    app.run(host="0.0.0.0", port=port, debug=True)
