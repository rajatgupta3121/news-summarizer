import streamlit as st
import plotly.express as px
from utils import (
    fetch_articles_for_company,
    generate_summary_bart,
    analyze_sentiment_vader,
    comparative_analysis,
    generate_hindi_tts
)

st.set_page_config(page_title="Company News Summarizer", layout="wide")

st.title("📈 Company News Summarization & Sentiment Analysis (with Hindi TTS)")
st.markdown("Enter a company name to fetch and analyze recent news articles.")

company = st.text_input("Enter Company Name")

if st.button("Analyze"):
    if company.strip() == "":
        st.error("Please enter a company name.")
    else:
        with st.spinner("Fetching, summarizing, and analyzing articles..."):
            # Fetch articles
            articles = fetch_articles_for_company(company)
            # Summarize & analyze sentiment
            for article in articles:
                content = article.get('content', '')
                article['summary'] = generate_summary_bart(content)
                article['sentiment'] = analyze_sentiment_vader(content)
            
            # Comparative analysis
            comparison = comparative_analysis(articles)
            final_sentiment = comparison['Overall Sentiment Conclusion']
            
            # Generate Hindi audio
            tts_audio = generate_hindi_tts(f"{company} ke news coverage par vishleshan ke anusar {final_sentiment} hai.")

            # Display results
            st.header(f"📰 News Coverage for {company.capitalize()}")

            # Sentiment pie chart
            sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
            for article in articles:
                sentiment_counts[article['sentiment']] += 1

            fig = px.pie(
                names=list(sentiment_counts.keys()),
                values=list(sentiment_counts.values()),
                title="Sentiment Distribution Across Articles"
            )
            st.plotly_chart(fig)

            # Display articles
            st.subheader("Article Details")
            for article in articles:
                with st.expander(article['title']):
                    st.write(f"**Published On:** {article.get('date', 'N/A')}")
                    st.write(f"**Summary:** {article['summary']}")
                    st.write(f"**Sentiment:** {article['sentiment']}")
                    if 'url' in article:
                        st.markdown(f"[Read Full Article]({article['url']})")

            # Comparative analysis display
            st.subheader("📊 Comparative Analysis")
            st.write(f"**Overall Conclusion:** {comparison['Overall Sentiment Conclusion']}")
            st.write("**Topic Overlap:**")
            st.json(comparison['Topic Overlap'])

            st.write("**Coverage Differences:**")
            for diff in comparison['Coverage Differences']:
                st.write(f"- {diff['Comparison']} | Impact: {diff['Impact']}")

            # Play Hindi audio summary
            st.subheader("🔊 Listen to Hindi Audio Summary")
            st.audio(tts_audio, format="audio/mp3")

st.markdown("---")
st.caption("Built with ❤️ by Rajat Gupta.")

