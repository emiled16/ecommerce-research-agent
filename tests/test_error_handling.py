import json
from unittest.mock import Mock

from src.llm.tools.market_trend_analysis import analyze_market_trends
from src.llm.tools.sentiment_analysis import get_product_sentiment_analysis
from src.llm.tools.webscraping import fetch_product_data
from src.llm.agent import ResearchContext


def test_market_trends_product_not_found():
    ctx = Mock()
    ctx.deps = ResearchContext(product_name="NonExistentProduct")

    result = analyze_market_trends(ctx)

    result_data = json.loads(result)
    assert "error" in result_data
    assert "Market data not found" in result_data["error"]


def test_sentiment_analysis_missing_data():
    ctx = Mock()
    ctx.deps = ResearchContext(product_name=None, reviews_data=None)

    result = get_product_sentiment_analysis(ctx)

    result_data = json.loads(result)
    assert "error" in result_data
    assert "Product name or reviews data not found" in result_data["error"]


def test_webscraping_product_not_found():
    ctx = Mock()
    ctx.deps = ResearchContext()

    result = fetch_product_data(ctx, "NonExistentProduct")

    result_data = json.loads(result)
    assert "error" in result_data or result_data is None
