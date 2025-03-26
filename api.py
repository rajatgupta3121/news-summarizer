from flask import Flask, request, jsonify
from utils import (
    fetch_articles_for_company,
    process_articles_parallel,
    comparative_analysis,
    generate_hindi_tts_bytes
)
import base64

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Company News Summarizer API is running."

@app.route('/analyze_company', methods=['GET'])
def analyze_company():
    company = request.args.get('company')
    if not company:
        return jsonify({"error": "Company parameter is required"}), 400

    # Fetch and process articles
    articles = fetch_articles_for_company(company)
    articles = process_articles_parallel(articles)
    comparison = comparative_analysis(articles)

    # Hindi audio summary generation
    final_sentiment = comparison['Overall Sentiment Conclusion']
    summary_text = f"{company} ke news coverage ke anusar overall sentiment {final_sentiment} hai."
    audio_bytes = generate_hindi_tts_bytes(summary_text)

    audio_b64 = None
    if audio_bytes:
        audio_b64 = base64.b64encode(audio_bytes.read()).decode()

    # Prepare response
    response_data = {
        "articles": articles,
        "comparison": comparison,
        "audio_base64": audio_b64   # Audio in base64 so Android can decode and play
    }

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
