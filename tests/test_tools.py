import json
from unittest.mock import Mock, patch, mock_open

from src.llm.tools.webscraping import fetch_product_data, fetch_product_reviews
from src.llm.tools.sentiment_analysis import get_product_sentiment_analysis
from src.llm.tools.market_trend_analysis import analyze_market_trends
from src.llm.tools.report_generator import generate_product_report
from src.llm.agent import ResearchContext


def test_fetch_product_data():
    ctx = Mock()
    ctx.deps = ResearchContext()

    result = fetch_product_data(ctx, "iPhone 15 Pro")

    assert result is not None
    result_data = json.loads(result)
    assert "product_info" in result_data
    assert "pricing_data" in result_data
    assert "availability_summary" in result_data
    assert "rating_summary" in result_data
    assert "retailers" in result_data
    assert "scraping_metadata" in result_data
    assert result_data["product_info"]["name"] == "iPhone 15 Pro"


def test_fetch_product_reviews():
    ctx = Mock()
    ctx.deps = ResearchContext()

    result = fetch_product_reviews(ctx, "iPhone 15 Pro")

    assert result is not None
    result_data = json.loads(result)
    assert isinstance(result_data, list)
    assert len(result_data) >= 0
    assert ctx.deps.reviews_data is not None


def test_get_product_sentiment_analysis():
    ctx = Mock()
    ctx.deps = ResearchContext(
        product_name="iPhone 15 Pro",
        reviews_data=[
            {"sentiment": "positive", "rating": 5},
            {"sentiment": "positive", "rating": 4},
            {"sentiment": "negative", "rating": 2},
        ],
    )

    result = get_product_sentiment_analysis(ctx)

    assert result is not None
    result_data = json.loads(result)
    assert "total_reviews" in result_data
    assert "sentiment_summary" in result_data
    assert "sentiment_percentages" in result_data
    assert "average_rating" in result_data
    assert "overall_sentiment" in result_data
    assert "confidence_score" in result_data
    assert result_data["total_reviews"] == 3
    assert result_data["sentiment_summary"]["positive"] == 2
    assert result_data["sentiment_summary"]["negative"] == 1
    assert ctx.deps.sentiment_analysis is not None


def test_analyze_market_trends():
    ctx = Mock()
    ctx.deps = ResearchContext(product_name="iPhone 15 Pro")

    result = analyze_market_trends(ctx)

    assert result is not None
    result_data = json.loads(result)

    assert isinstance(result_data, dict)
    assert ctx.deps.market_trends is not None


@patch("builtins.open", new_callable=mock_open)
@patch("pathlib.Path.mkdir")
def test_generate_product_report(mock_mkdir, mock_file):
    ctx = Mock()
    ctx.deps = ResearchContext(
        product_info={"product_info": {"name": "iPhone 15 Pro"}},
        sentiment_analysis={"overall_sentiment": "positive"},
        market_trends={"trend": "growing"},
    )

    result = generate_product_report(ctx)

    assert result is not None
    assert "iPhone_15_Pro_report_" in result
    mock_file.assert_called()
    mock_mkdir.assert_called()
    assert ctx.deps.report_path is not None
