from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Load scraped content
with open("scraped_content.json", "r") as file:
    scraped_data = json.load(file)

API_KEY = "AIzaSyCHcavN8CMNDIy_DNWbtZ69_XmIN37BMgI"

def ask_gemini(category, question):
    """Sends question to Google Gemini API"""
    content = scraped_data.get(category, "")
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": f"Context:\n{content}\n\nQuestion: {question}"}]}]}

    response = requests.post(api_url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json().get("candidates", [{}])[0].get("content", "No response.")
    return "Error connecting to Gemini API"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    category = data.get("category", "")
    question = data.get("question", "")
    answer = ask_gemini(category, question)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
