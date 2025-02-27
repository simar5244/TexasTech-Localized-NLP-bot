from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import requests
import os

app = Flask(__name__)
CORS(app, origins=["https://simar5244.github.io"])  # Allow requests from GitHub Pages

# === Configuration ===
API_KEY = "AIzaSyCHcavN8CMNDIy_DNWbtZ69_XmIN37BMgI"  # Replace with your actual API key

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
            return response.json()["candidates"][0]["content"]
        except (KeyError, IndexError):
            return "Unexpected response format from Gemini API."
    else:
        return f"Request failed with status code: {response.status_code}"

# === Flask Routes ===
@app.route("/")
def index():
    categories = list(scraped_data.keys())  # Load categories from scraped data
    return render_template("index.html", categories=categories)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    category = data.get("category")
    question = data.get("question")

    if not category or not question:
        return jsonify({"error": "Both category and question are required."}), 400

    answer = ask_gemini(category, question)
    return jsonify({"answer": answer})

# === Run Flask App ===
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
