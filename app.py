import streamlit as st
import plotly.express as px
from utils import (
    fetch_articles_for_company,
    generate_summary_bart,
    analyze_sentiment_vader,
    comparative_analysis,
    generate_hindi_tts
)
import base64

st.set_page_config(page_title="📈 Company News Summarizer & Sentiment Analysis", layout="wide", page_icon="📈")

st.title("📈 Company News Summarization & Sentiment Analysis (with Hindi TTS)")
st.markdown("Enter a company name to fetch and analyze recent news articles, see sentiment insights, and get a Hindi audio summary.")

company = st.text_input("Enter Company Name", placeholder="e.g., Tesla, Infosys, Amazon")

if st.button("Analyze"):
    if company.strip() == "":
        st.error("⚠️ Please enter a company name to proceed.")
    else:
        with st.spinner("Fetching articles, generating summaries, and analyzing sentiments..."):
            articles = fetch_articles_for_company(company)
            if not articles:
                st.error("❌ No articles found or there was a network issue. Please try another company or retry later.")
            else:
                for article in articles:
                    content = article.get('content', '')
                    article['summary'] = generate_summary_bart(content)
                    article['sentiment'] = analyze_sentiment_vader(content)

                comparison = comparative_analysis(articles)
                final_sentiment = comparison['Overall Sentiment Conclusion']

                audio_file = generate_hindi_tts(
                    f"{company} ke news coverage par vishleshan ke anusar overall sentiment {final_sentiment} hai."
                )

                st.header(f"📰 News Coverage Summary for **{company.capitalize()}**")

                sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
                for article in articles:
                    sentiment_counts[article['sentiment']] += 1

                fig = px.pie(
                    names=list(sentiment_counts.keys()),
                    values=list(sentiment_counts.values()),
                    color=list(sentiment_counts.keys()),
                    title="Sentiment Distribution Across Articles",
                    hole=0.3
                )
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("📃 Article Summaries")
                for article in articles:
                    with st.expander(f"{article['title']}"):
                        st.write(f"**Summary:** {article['summary']}")
                        st.write(f"**Sentiment:** {article['sentiment']}")
                        if article.get('url'):
                            st.markdown(f"[Read Full Article]({article['url']})")

                st.subheader("📊 Comparative Analysis Insights")
                st.write(f"**Overall Sentiment Conclusion:** {comparison['Overall Sentiment Conclusion']}")
                st.json(comparison['Topic Overlap'])
                for diff in comparison['Coverage Differences']:
                    st.write(f"➡️ {diff['Comparison']} — *Impact:* {diff['Impact']}")

                st.subheader("🔊 Hindi Audio Summary")
                if audio_file:
                    with open(audio_file, "rb") as audio:
                        audio_bytes = audio.read()
                        st.audio(audio_bytes, format="audio/mp3")
                        b64 = base64.b64encode(audio_bytes).decode()
                        href = f'<a href="data:audio/mp3;base64,{b64}" download="{company}_summary.mp3">📥 Download Hindi Audio Report</a>'
                        st.markdown(href, unsafe_allow_html=True)
                else:
                    st.write("Audio generation failed. Please try again.")

st.markdown("---")
st.caption("Built with ❤️ by Rajat Gupta | [Connect on LinkedIn](https://linkedin.com/in/rajatgupta3121)")
