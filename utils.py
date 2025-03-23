import requests
from bs4 import BeautifulSoup
from newspaper import Article
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from gtts import gTTS
import os
import uuid

# 1. Fetch articles from Bing News
def fetch_articles_for_company(company):
    search_url = f"https://www.bing.com/news/search?q={company}&FORM=HDRSC6"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, "html.parser")
    articles = []

    for item in soup.find_all("a", class_="title")[:10]:
        title = item.text.strip()
        url = item["href"]
        try:
            article = Article(url)
            article.download()
            article.parse()
            content = article.text
            articles.append({
                "title": title,
                "url": url,
                "content": content
            })
        except:
            continue
    return articles

# 2. Summarization using Hugging Face BART
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_summary_bart(text):
    # Skip summarization for very short text
    if not text or len(text.strip().split()) < 50:
        return text.strip()[:200] + "..." if text else "Content not sufficient for summarization."
    try:
        summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Summarization failed: {str(e)}"


# 3. Sentiment analysis using VADER
vader_analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment_vader(text):
    scores = vader_analyzer.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# 4. Comparative analysis
def comparative_analysis(articles):
    sentiment_dist = {"Positive": 0, "Negative": 0, "Neutral": 0}
    common_topics = []
    for article in articles:
        sentiment_dist[article['sentiment']] += 1
        common_topics.append(article['title'].split(" ")[0])  # Rough topic extraction

    overall_sentiment = "mostly positive" if sentiment_dist["Positive"] > sentiment_dist["Negative"] else "mixed or negative"
    return {
        "Sentiment Distribution": sentiment_dist,
        "Coverage Differences": [
            {"Comparison": "Some articles show growth while others raise concerns.", "Impact": "Mixed investor sentiment."}
        ],
        "Topic Overlap": {
            "Common Topics": list(set(common_topics))
        },
        "Overall Sentiment Conclusion": overall_sentiment
    }

# 5. Generate Hindi TTS audio
def generate_hindi_tts(text):
    audio = gTTS(text=text, lang='hi', slow=False)
    file_name = f"static/audio_{uuid.uuid4().hex}.mp3"
    audio.save(file_name)
    return file_name
