import requests
from bs4 import BeautifulSoup
from newspaper import Article
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from gtts import gTTS
import uuid
import os

# Initialize summarizer with a lightweight model for speed
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
vader_analyzer = SentimentIntensityAnalyzer()

# 1. Fetch articles
def fetch_articles_for_company(company):
    search_url = f"https://www.bing.com/news/search?q={company}&FORM=HDRSC6"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, "html.parser")
    articles = []

    for item in soup.find_all("a", class_="title")[:5]:  # Limit to top 5
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
        except Exception:
            continue
    return articles

# 2. Summarization (fast, with length constraints)
def generate_summary_bart(text):
    if not text or len(text.strip().split()) < 40:
        return text.strip()[:200] + "..." if text else "Not enough content to summarize."
    text = text[:800]  # Limit for speed
    try:
        summary = summarizer(text, max_length=80, min_length=20, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Summarization failed: {str(e)}"

# 3. Sentiment analysis
def analyze_sentiment_vader(text):
    scores = vader_analyzer.polarity_scores(text)
    comp = scores['compound']
    if comp >= 0.05:
        return "Positive"
    elif comp <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# 4. Comparative analysis
def comparative_analysis(articles):
    sentiment_dist = {"Positive": 0, "Negative": 0, "Neutral": 0}
    keywords = []

    for article in articles:
        sentiment_dist[article['sentiment']] += 1
        words = article['title'].split(" ")[:2]
        keywords.extend(words)

    overall_sentiment = (
        "mostly positive" if sentiment_dist["Positive"] > sentiment_dist["Negative"] else "mixed or negative"
    )

    return {
        "Sentiment Distribution": sentiment_dist,
        "Coverage Differences": [
            {"Comparison": "Articles differ between optimism and caution.", "Impact": "Creates mixed sentiment for readers."}
        ],
        "Topic Overlap": {
            "Common Keywords": list(set(keywords))
        },
        "Overall Sentiment Conclusion": overall_sentiment
    }

# 5. Generate Hindi audio summary
def generate_hindi_tts(text):
    try:
        audio = gTTS(text=text, lang='hi', slow=False)
        file_name = f"audio_{uuid.uuid4().hex}.mp3"
        audio.save(file_name)
        return file_name
    except Exception:
        return None
