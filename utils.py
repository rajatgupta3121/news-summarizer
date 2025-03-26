import requests
from bs4 import BeautifulSoup
from newspaper import Article
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from gtts import gTTS
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

# 1. Initialize lightweight summarizer model (faster than large BART)
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")
vader_analyzer = SentimentIntensityAnalyzer()

# 2. Fetch articles from Bing News and fallback scrape content if needed
def fetch_articles_for_company(company):
    search_url = f"https://www.bing.com/news/search?q={company}&FORM=HDRSC6"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, "html.parser")
    articles = []

    for item in soup.find_all("a", class_="title")[:3]:  # Limit to top 3 for speed
        title = item.text.strip()
        url = item["href"]
        content = ""

        try:
            article = Article(url)
            article.download()
            article.parse()
            content = article.text.strip()
        except Exception:
            content = ""

        # If article content is too short, fallback scraping from <p> tags
        if len(content.split()) < 20:
            try:
                fallback_res = requests.get(url)
                fallback_soup = BeautifulSoup(fallback_res.content, "html.parser")
                paragraphs = fallback_soup.find_all('p')
                content = " ".join([p.get_text() for p in paragraphs]).strip()
            except Exception:
                content = ""

        if len(content.strip()) == 0:
            content = f"Unable to retrieve full content for this article: {title}"

        articles.append({
            "title": title,
            "url": url,
            "content": content
        })

    return articles

# 3. Generate summaries using lightweight summarizer
def generate_summary_bart(text):
    if not text or len(text.strip().split()) < 20:
        return text.strip()[:300] + "..." if text else "Summary not available."
    text = text[:500]
    try:
        summary = summarizer(text, max_length=60, min_length=15, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Summarization failed."

# 4. Sentiment analysis using VADER
def analyze_sentiment_vader(text):
    scores = vader_analyzer.polarity_scores(text)
    comp = scores['compound']
    if comp >= 0.05:
        return "Positive"
    elif comp <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# 5. Comparative analysis for sentiment distribution & topic overlap
def comparative_analysis(articles):
    sentiment_dist = {"Positive": 0, "Negative": 0, "Neutral": 0}
    keywords = []

    for article in articles:
        sentiment_dist[article['sentiment']] += 1
        headline_words = article['title'].split(" ")[:2]
        keywords.extend(headline_words)

    overall_sentiment = (
        "mostly positive" if sentiment_dist["Positive"] > sentiment_dist["Negative"] else "mixed or negative"
    )

    return {
        "Sentiment Distribution": sentiment_dist,
        "Coverage Differences": [
            {"Comparison": "Some articles show optimism, others raise caution.", "Impact": "Readers receive mixed signals."}
        ],
        "Topic Overlap": {
            "Common Keywords": list(set(keywords))
        },
        "Overall Sentiment Conclusion": overall_sentiment
    }

# 6. Generate Hindi TTS in memory (no disk write)
def generate_hindi_tts_bytes(text):
    try:
        tts = gTTS(text=text, lang='hi')
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception:
        return None

# 7. Process articles in parallel to speed up summaries and sentiment analysis
def process_article(article):
    content = article.get('content', '')
    article['summary'] = generate_summary_bart(content)
    article['sentiment'] = analyze_sentiment_vader(content)
    return article

def process_articles_parallel(articles):
    with ThreadPoolExecutor(max_workers=3) as executor:
        return list(executor.map(process_article, articles))
