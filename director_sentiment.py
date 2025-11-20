# director_sentiment.py
from news_api import fetch_company_news
from sentiment import analyze_articles

def analyze_directors(directors: list) -> list:
    results = []

    for d in directors:
        try:
            name = d["name"]

            articles = fetch_company_news(name, page_size=20)

            analyzed = analyze_articles(articles)

            results.append({
                "director": name,
                "details": d,
                "total_articles": len(analyzed),
                "negative_count": sum(1 for x in analyzed if x["sentiment_label"] == "negative"),
                "articles": analyzed
            })

        except Exception as e:
            results.append({
                "director": d.get("name", "Unknown"),
                "details": d,
                "error": str(e),
                "articles": []
            })

    return results
