# app.py
import streamlit as st
import pandas as pd

from news_api import fetch_company_news
from sentiment import analyze_articles
from zauba_scraper import scrape_zauba_details
from director_sentiment import analyze_directors

st.set_page_config(page_title="Company News Sentiment OSINT", layout="wide")

st.title("🕵️‍♂️ Company News Sentiment OSINT Dashboard")

st.markdown(
    """
Enter a **company name** below.  
The app will:
1. Fetch recent news articles using Google News RSS  
2. Run **NLTK VADER** sentiment analysis  
3. Show which articles are **positive / neutral / negative**  
4. Scrape ZaubaCorp for company info  
5. Run sentiment analysis on **directors**  
"""
)

company_name = st.text_input("🔎 Company name", placeholder="e.g. Reliance Industries, TCS, Infosys")

page_size = st.slider("Number of articles to fetch", min_value=5, max_value=50, value=20, step=5)

if st.button("Fetch & Analyze"):

    if not company_name.strip():
        st.warning("Please enter a company name.")
        st.stop()

    
    with st.spinner("Fetching news articles & analyzing sentiment..."):
        try:
            articles = fetch_company_news(company_name, page_size=page_size)
        except Exception as e:
            st.error(f"Error while fetching news: {e}")
            st.stop()

        if not articles:
            st.info("No articles found for this company.")
            st.stop()

        analyzed_articles = analyze_articles(articles)

        # Convert to DataFrame
        df = pd.DataFrame(
            [
                {
                    "Source": art.get("source", "Unknown"),
                    "Title": art.get("title"),
                    "Description": art.get("description"),
                    "Published At": art.get("publishedAt"),
                    "URL": art.get("url"),
                    "Sentiment": art.get("sentiment_label"),
                    "Compound Score": art.get("sentiment_compound"),
                    "Neg": art.get("sentiment_neg"),
                    "Neu": art.get("sentiment_neu"),
                    "Pos": art.get("sentiment_pos"),
                }
                for art in analyzed_articles
            ]
        )

    st.subheader("Sentiment Summary")

    sentiment_counts = df["Sentiment"].value_counts()
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Count by sentiment:**")
        st.write(sentiment_counts)

    with col2:
        st.write("**Negative article percentage:**")
        total = len(df)
        neg = (df["Sentiment"] == "negative").sum()
        perc = (neg / total) * 100 if total > 0 else 0
        st.write(f"{neg} / {total} articles are negative (**{perc:.2f}%**)")


    st.subheader("All Articles with Sentiment")
    st.dataframe(df, use_container_width=True)

    negative_df = df[df["Sentiment"] == "negative"]

    if not negative_df.empty:
        st.subheader("Flagged Negative Articles")
        st.dataframe(negative_df, use_container_width=True)
    else:
        st.success("No negative articles detected ")


    st.subheader("ZaubaCorp Company Details")

    zauba = scrape_zauba_details(company_name)

    if not zauba["company_name"]:
        st.warning("No ZaubaCorp data found for this company.")
    else:
        st.json({
            "Company Name": zauba["company_name"],
            "CIN": zauba["cin"],
            "Status": zauba["status"],
            "ROC": zauba["roc"],
            "Registration Date": zauba["registration_date"],
            "Authorized Capital": zauba["authorized_capital"],
            "Paid-up Capital": zauba["paidup_capital"],
            "Directors": zauba["directors"]
        })


        st.subheader(" Director-wise Sentiment Analysis")

        director_results = analyze_directors(zauba["directors"])

        for d in director_results:
            st.write(f"### Director: **{d['director']}**")

            if "error" in d:
                st.error(f"Error: {d['error']}")
                continue

            st.write(f"- Total Articles: {d['total_articles']}")
            st.write(f"- Negative Articles: {d['negative_count']}")

            if d['articles']:
                st.dataframe(
                    pd.DataFrame(d["articles"])[
                        ["title", "description", "publishedAt", "url", "sentiment_label", "sentiment_compound"]
                    ],
                    use_container_width=True
                )

    st.success("ZaubaCorp + Director Sentiment analysis completed!")
