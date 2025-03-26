import streamlit as st
import plotly.express as px
from utils import (
    fetch_articles_for_company,
    generate_summary_bart,
    analyze_sentiment_vader,
    comparative_analysis,
    generate_hindi_tts_bytes,
    process_articles_parallel
)
import base64

# Page config with wide layout and custom icon
st.set_page_config(page_title="📈 Company News Summarizer & Insights", layout="wide", page_icon="📰")

# Custom CSS for better visuals
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton > button {
        color: white;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 8px;
        height: 3em;
        width: 12em;
        font-size: 16px;
    }
    .stMarkdown {
        font-size: 16px;
    }
    .badge-positive {
        background-color: #28a745;
        color: white;
        padding: 4px 8px;
        border-radius: 5px;
        font-size: 13px;
    }
    .badge-neutral {
        background-color: #ffc107;
        color: black;
        padding: 4px 8px;
        border-radius: 5px;
        font-size: 13px;
    }
    .badge-negative {
        background-color: #dc3545;
        color: white;
        padding: 4px 8px;
        border-radius: 5px;
        font-size: 13px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Company News Summarizer & Sentiment Insights")
st.markdown("✨ *Enter a company name to get recent articles, AI-powered summaries, sentiment analysis, and a Hindi audio brief!*")

company = st.text_input("🔎 **Enter Company Name**", placeholder="e.g., Tesla, Infosys, Amazon")

if st.button("🚀 Analyze Now"):
    if company.strip() == "":
        st.error("⚠️ Please enter a valid company name.")
    else:
        with st.spinner("🔄 Fetching, summarizing, and analyzing from live news..."):
            articles = fetch_articles_for_company(company)
            articles = process_articles_parallel(articles)

            if not articles:
                st.error("❌ No articles found. Try another company or check your connection.")
            else:
                comparison = comparative_analysis(articles)
                final_sentiment = comparison['Overall Sentiment Conclusion']

                # Hindi audio generation
                audio_bytes = generate_hindi_tts_bytes(
                    f"{company} ke news coverage par vishleshan ke anusar overall sentiment {final_sentiment} hai."
                )

                st.markdown("---")
                st.header(f"🗞️ Latest News for **{company.capitalize()}**")
                
                # Sentiment pie chart
                sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
                for article in articles:
                    sentiment_counts[article['sentiment']] += 1

                fig = px.pie(
                    names=list(sentiment_counts.keys()),
                    values=list(sentiment_counts.values()),
                    title="Sentiment Distribution Across Recent Articles",
                    hole=0.35,
                    color_discrete_map={
                        "Positive": "#28a745",
                        "Neutral": "#ffc107",
                        "Negative": "#dc3545"
                    }
                )
                fig.update_traces(textinfo='percent+label', pull=[0.05, 0, 0])
                st.plotly_chart(fig, use_container_width=True)

                # Display articles in beautiful cards
                st.subheader("📝 AI-Powered Article Summaries")
                for article in articles:
                    sentiment_badge = {
                        "Positive": '<span class="badge-positive">Positive</span>',
                        "Neutral": '<span class="badge-neutral">Neutral</span>',
                        "Negative": '<span class="badge-negative">Negative</span>'
                    }
                    with st.expander(f"🔸 {article['title']}"):
                        st.markdown(f"**Summary:** {article['summary']}")
                        st.markdown(f"**Sentiment:** {sentiment_badge[article['sentiment']]}", unsafe_allow_html=True)
                        if article.get('url'):
                            st.markdown(f"[🌐 Read Full Article]({article['url']})")

                # Comparative analysis section
                st.subheader("📊 Comparative Insights")
                with st.expander("🔎 See Detailed Comparative Analysis"):
                    st.markdown(f"**Overall Sentiment Conclusion:** *{comparison['Overall Sentiment Conclusion']}*")
                    st.write("**Common Topics Found:**")
                    st.json(comparison['Topic Overlap'])
                    st.write("**Coverage Differences Noted:**")
                    for diff in comparison['Coverage Differences']:
                        st.markdown(f"➡️ {diff['Comparison']} — *Impact:* {diff['Impact']}")

                # Audio playback
                st.subheader("🔊 Listen to AI-Generated Hindi Audio Summary")
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")

                    b64_audio = base64.b64encode(audio_bytes.read()).decode()
                    download_link = f'<a href="data:audio/mp3;base64,{b64_audio}" download="{company}_summary.mp3">📥 Download Hindi Audio Summary</a>'
                    st.markdown(download_link, unsafe_allow_html=True)
                else:
                    st.warning("Audio generation failed. Please try again.")

st.markdown("---")
st.markdown("✨ *Built with ❤️ by [Rajat Gupta](https://www.linkedin.com/in/rajatgupta3121/).*")

