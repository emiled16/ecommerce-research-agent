import json
from typing import Any
from loguru import logger
from pydantic_ai import RunContext


def _analyze_product_sentiment(reviews: list[dict[str, Any]]) -> dict[str, Any]:
    if not reviews:
        return {
            "total_reviews": 0,
            "sentiment_summary": {"positive": 0, "negative": 0, "neutral": 0},
            "sentiment_percentages": {"positive": 0.0, "negative": 0.0, "neutral": 0.0},
            "average_rating": 0.0,
            "overall_sentiment": "neutral",
        }

    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    total_rating = 0

    for review in reviews:
        sentiment = review.get("sentiment", "neutral").lower()
        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1

        rating = review.get("rating", 0)
        total_rating += rating

    total_reviews = len(reviews)
    average_rating = total_rating / total_reviews if total_reviews > 0 else 0

    sentiment_percentages = {sentiment: (count / total_reviews) * 100 for sentiment, count in sentiment_counts.items()}

    max_sentiment = max(sentiment_counts, key=sentiment_counts.get)
    overall_sentiment = max_sentiment

    if sentiment_counts["positive"] == sentiment_counts["negative"]:
        overall_sentiment = "positive" if average_rating >= 4 else "negative" if average_rating <= 2 else "neutral"

    return {
        "total_reviews": total_reviews,
        "sentiment_summary": sentiment_counts,
        "sentiment_percentages": {sentiment: round(percentage, 1) for sentiment, percentage in sentiment_percentages.items()},
        "average_rating": round(average_rating, 1),
        "overall_sentiment": overall_sentiment,
        "confidence_score": round(max(sentiment_percentages.values()), 1),
    }


def get_product_sentiment_analysis(ctx: RunContext) -> str:
    logger.info("Getting product sentiment analysis")
    product_name = ctx.deps.product_name
    reviews_data = ctx.deps.reviews_data
    if product_name is None or reviews_data is None:
        logger.error("Product name or reviews data not found")
        return json.dumps({"error": "Product name or reviews data not found"})

    logger.info(f"Analyzing sentiment for product: {product_name}")

    analysis = _analyze_product_sentiment(reviews_data)

    ctx.deps.sentiment_analysis = analysis
    logger.info(f"Sentiment analysis for product: {product_name} completed")
    return json.dumps(analysis, indent=2)
