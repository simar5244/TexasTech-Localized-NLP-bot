import os
from flask import Flask, request, jsonify
from gemini_api import ask_question
from data_loader import load_scraped_data

app = Flask(__name__)

scraped_data = load_scraped_data()

@app.route("/ask", methods=["POST"])
def handle_question():
    data = request.json
    category = data.get("category", "").strip()
    question = data.get("question", "").strip()

    if not category or not question:
        return jsonify({"error": "Missing category or question"}), 400

    answer = ask_question(category, question, scraped_data)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's default port
    app.run(host="0.0.0.0", port=port)
