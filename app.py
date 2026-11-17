"""
Flask Web Application for Fake News Detection & Sentiment Analysis System
Project 4 - NLP Major Project
"""

import os
from flask import Flask, render_template, request, jsonify
from nlp_model import FakeNewsNLPEngine
from dataset import SAMPLE_NEWS_ARTICLES

app = Flask(__name__)
nlp_engine = FakeNewsNLPEngine()

@app.route('/')
def home():
    return render_template('index.html', samples=SAMPLE_NEWS_ARTICLES)

@app.route('/api/sample/<sample_id>', methods=['GET'])
def get_sample(sample_id):
    if sample_id in SAMPLE_NEWS_ARTICLES:
        return jsonify({"success": True, "data": SAMPLE_NEWS_ARTICLES[sample_id]})
    return jsonify({"success": False, "error": "Sample article not found"}), 404

@app.route('/api/analyze', methods=['POST'])
def analyze_news():
    news_text = request.form.get('news_text', '').strip()
    model_type = request.form.get('model_type', 'lr')

    if not news_text or len(news_text) < 15:
        return jsonify({
            "success": False,
            "error": "Please provide a valid news article or headline (at least 15 characters)."
        }), 400

    try:
        results = nlp_engine.predict(news_text, model_type=model_type)
        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": f"Analysis failed: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Fake News Detector on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)

