# news_api.py
import requests
from bs4 import BeautifulSoup

def fetch_company_news(query: str, page_size: int = 20):
    max_results = page_size

    query = query.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={query}"

    response = requests.get(url, headers={"User-Agent": "PythonBackend/1.0"})
    
    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")

    articles = []

    for item in items[:max_results]:
        articles.append({
            "title": item.title.text,
            "description": item.description.text,
            "publishedAt": item.pubDate.text,
            "url": item.link.text,
            "source": item.source.text if item.source else "Unknown",
        })

    return articles
