# sentiment.py
from typing import Dict, Any, List
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()


def classify_label(compound: float) -> str:
    if compound >= 0.05:
        return "positive"
    elif compound <= -0.05:
        return "negative"
    else:
        return "neutral"


def analyze_text_sentiment(text: str) -> Dict[str, Any]:
    if not text:
        return {
            "neg": 0.0,
            "neu": 1.0,
            "pos": 0.0,
            "compound": 0.0,
            "label": "neutral",
        }

    scores = sia.polarity_scores(text)
    scores["label"] = classify_label(scores["compound"])
    return scores


def analyze_articles(articles: List[Dict]) -> List[Dict]:
    enriched = []

    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")
        combined_text = f"{title}. {description}"

        sentiment = analyze_text_sentiment(combined_text)

        enriched.append({
            **article,
            "sentiment_label": sentiment["label"],
            "sentiment_compound": sentiment["compound"],
            "sentiment_neg": sentiment["neg"],
            "sentiment_neu": sentiment["neu"],
            "sentiment_pos": sentiment["pos"],
        })

    return enriched
