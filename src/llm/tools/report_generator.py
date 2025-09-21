from datetime import datetime
from pathlib import Path
from typing import Any
from loguru import logger
from pydantic_ai import RunContext


def generate_product_report(
    ctx: RunContext,
) -> str:
    product_info = ctx.deps.product_info
    if isinstance(product_info, dict):
        product_info = product_info.get("product_info")
    sentiment_analysis = ctx.deps.sentiment_analysis
    market_trends = ctx.deps.market_trends

    if product_info is None:
        logger.warning("Product info not found - generating empty report")
        product_info = {"name": "Unknown Product"}
    if sentiment_analysis is None:
        logger.warning("Sentiment analysis not found - generating empty report")
        sentiment_analysis = {"error": "Data not accessible"}
    if market_trends is None:
        logger.warning("Market trends not found - generating empty report")
        market_trends = {"error": "Data not accessible"}

    reports_dir = Path(__file__).parent.parent.parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    product_name = product_info.get("name", "unknown_product").replace(" ", "_")
    filename = f"{product_name}_report_{timestamp}"
    report_path = reports_dir / filename

    markdown_content = _generate_markdown_content(product_info, sentiment_analysis, market_trends)
    html_content = _generate_html_content(product_info, sentiment_analysis, market_trends)

    with open(report_path.with_suffix(".md"), "w", encoding="utf-8") as f:
        f.write(markdown_content)
    with open(report_path.with_suffix(".html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    ctx.deps.report_path = str(report_path.with_suffix(".html"))
    return str(report_path)


def _generate_markdown_content(
    product_info: dict[str, Any], sentiment_analysis: dict[str, Any], market_trends: dict[str, Any]
) -> str:
    product_name = product_info.get("name", "Unknown Product")
    report_date = datetime.now().strftime("%B %d, %Y")

    content = f"""# Product Analysis Report: {product_name}

**Generated on:** {report_date}

---

## Executive Summary

This report provides a comprehensive analysis of **{product_name}** including product information, customer sentiment analysis, and market trend insights.

---

## 📱 Product Information

"""

    # Check if we have minimal product information
    has_product_data = any(key in product_info for key in ["category", "price", "description", "features"])

    if has_product_data:
        if "category" in product_info:
            content += f"**Category:** {product_info['category']}\n\n"

        if "price" in product_info:
            content += f"**Price:** ${product_info['price']}\n\n"

        if "description" in product_info:
            content += f"**Description:** {product_info['description']}\n\n"

        if "features" in product_info and product_info["features"]:
            content += "**Key Features:**\n"
            for feature in product_info["features"]:
                content += f"- {feature}\n"
            content += "\n"
    else:
        content += "⚠️ **Product Information Not Available**\n\n"
        content += "Detailed product information could not be accessed at this time. Please verify product name and try again.\n\n"

    content += """---

## 😊 Customer Sentiment Analysis

"""

    if "error" not in sentiment_analysis:
        total_reviews = sentiment_analysis.get("total_reviews", 0)
        overall_sentiment = sentiment_analysis.get("overall_sentiment", "unknown")
        avg_rating = sentiment_analysis.get("average_rating", 0)

        content += f"**Total Reviews Analyzed:** {total_reviews}\n\n"
        content += f"**Overall Sentiment:** {overall_sentiment.title()}\n\n"
        content += f"**Average Rating:** {avg_rating}/5.0\n\n"

        if "sentiment_summary" in sentiment_analysis:
            sentiment_summary = sentiment_analysis["sentiment_summary"]
            content += "**Sentiment Breakdown:**\n"
            content += f"- 👍 Positive: {sentiment_summary.get('positive', 0)} reviews\n"
            content += f"- 👎 Negative: {sentiment_summary.get('negative', 0)} reviews\n"
            content += f"- 😐 Neutral: {sentiment_summary.get('neutral', 0)} reviews\n\n"

        if "sentiment_percentages" in sentiment_analysis:
            percentages = sentiment_analysis["sentiment_percentages"]
            content += "**Sentiment Percentages:**\n"
            content += f"- Positive: {percentages.get('positive', 0)}%\n"
            content += f"- Negative: {percentages.get('negative', 0)}%\n"
            content += f"- Neutral: {percentages.get('neutral', 0)}%\n\n"
    else:
        content += "⚠️ **Data Not Available**\n\n"
        content += "Customer sentiment analysis data could not be accessed at this time. Please try again later or check data connectivity.\n\n"

    content += """---

## 📈 Market Trend Analysis

"""

    if "error" not in market_trends:
        category = market_trends.get("category", "Unknown")
        market_sentiment = market_trends.get("market_sentiment", "unknown")

        content += f"**Product Category:** {category.title()}\n\n"
        content += f"**Market Sentiment:** {market_sentiment.title()}\n\n"

        if "current_metrics" in market_trends:
            metrics = market_trends["current_metrics"]
            content += "**Current Market Metrics:**\n"
            content += f"- Search Volume Index: {metrics.get('search_volume', 'N/A')}\n"
            content += f"- Price Index: {metrics.get('price_index', 'N/A')}\n"
            content += f"- Competition Index: {metrics.get('competition_index', 'N/A')}\n\n"

        if "trend_changes" in market_trends:
            changes = market_trends["trend_changes"]
            content += "**Trend Changes:**\n"
            content += f"- Monthly Search Change: {changes.get('monthly_search_change_percent', 'N/A')}%\n"
            content += f"- Monthly Price Change: {changes.get('monthly_price_change_percent', 'N/A')}%\n"
            content += f"- 6-Month Growth: {changes.get('six_month_growth_percent', 'N/A')}%\n\n"

        if "insights" in market_trends and market_trends["insights"]:
            content += "**Key Market Insights:**\n"
            for insight in market_trends["insights"]:
                content += f"- {insight}\n"
            content += "\n"
    else:
        content += "⚠️ **Data Not Available**\n\n"
        content += (
            "Market trend analysis data could not be accessed at this time. Please try again later or check data connectivity.\n\n"
        )

    content += """---

## 💡 Recommendations

Based on the analysis above, here are key recommendations:

"""

    recommendations = _generate_recommendations(sentiment_analysis, market_trends)
    for rec in recommendations:
        content += f"- {rec}\n"

    content += f"""

---

## 📊 Data Sources

- **Product Information:** Internal product database
- **Customer Reviews:** Aggregated from multiple retail platforms
- **Market Trends:** Market analysis database

---

*Report generated automatically on {report_date}*
"""

    return content


def _generate_html_content(product_info: dict[str, Any], sentiment_analysis: dict[str, Any], market_trends: dict[str, Any]) -> str:
    """Generate HTML content with the same information as the markdown report."""

    product_name = product_info.get("name", "Unknown Product")
    report_date = datetime.now().strftime("%B %d, %Y")

    # Start with HTML structure and CSS styling
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Analysis Report: {product_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            padding: 10px 0;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .meta-info {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
            font-weight: bold;
        }}
        .section {{
            margin-bottom: 40px;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }}
        .warning {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .metric {{
            display: inline-block;
            background: #f8f9fa;
            padding: 8px 12px;
            margin: 5px;
            border-radius: 5px;
            border-left: 3px solid #3498db;
        }}
        .positive {{ border-left-color: #27ae60; }}
        .negative {{ border-left-color: #e74c3c; }}
        .neutral {{ border-left-color: #f39c12; }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        .recommendations {{
            background: #e8f5e8;
            border: 1px solid #27ae60;
            border-radius: 8px;
            padding: 20px;
        }}
        .data-sources {{
            background: #f0f0f0;
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #666;
            font-style: italic;
        }}
        .emoji {{
            font-size: 1.2em;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Product Analysis Report: {product_name}</h1>
        
        <div class="meta-info">
            <strong>Generated on:</strong> {report_date}
        </div>

        <div class="section">
            <h2>📋 Executive Summary</h2>
            <p>This report provides a comprehensive analysis of <strong>{product_name}</strong> including product information, customer sentiment analysis, and market trend insights.</p>
        </div>

        <div class="section">
            <h2><span class="emoji">📱</span>Product Information</h2>
"""

    # Check if we have minimal product information
    has_product_data = any(key in product_info for key in ["category", "price", "description", "features"])

    if has_product_data:
        if "category" in product_info:
            html_content += f'            <div class="metric"><strong>Category:</strong> {product_info["category"]}</div>\n'

        if "price" in product_info:
            html_content += f'            <div class="metric"><strong>Price:</strong> ${product_info["price"]}</div>\n'

        if "description" in product_info:
            html_content += f"            <p><strong>Description:</strong> {product_info['description']}</p>\n"

        if "features" in product_info and product_info["features"]:
            html_content += "            <p><strong>Key Features:</strong></p>\n            <ul>\n"
            for feature in product_info["features"]:
                html_content += f"                <li>{feature}</li>\n"
            html_content += "            </ul>\n"
    else:
        html_content += """            <div class="warning">
                <strong>⚠️ Product Information Not Available</strong><br>
                Detailed product information could not be accessed at this time. Please verify product name and try again.
            </div>
"""

    html_content += """        </div>

        <div class="section">
            <h2><span class="emoji">😊</span>Customer Sentiment Analysis</h2>
"""

    if "error" not in sentiment_analysis:
        total_reviews = sentiment_analysis.get("total_reviews", 0)
        overall_sentiment = sentiment_analysis.get("overall_sentiment", "unknown")
        avg_rating = sentiment_analysis.get("average_rating", 0)

        html_content += f'            <div class="metric"><strong>Total Reviews Analyzed:</strong> {total_reviews}</div>\n'
        html_content += f'            <div class="metric {overall_sentiment}"><strong>Overall Sentiment:</strong> {overall_sentiment.title()}</div>\n'
        html_content += f'            <div class="metric"><strong>Average Rating:</strong> {avg_rating}/5.0</div>\n'

        if "sentiment_summary" in sentiment_analysis:
            sentiment_summary = sentiment_analysis["sentiment_summary"]
            html_content += """            <p><strong>Sentiment Breakdown:</strong></p>
            <ul>
"""
            html_content += (
                f'                <li class="positive">👍 Positive: {sentiment_summary.get("positive", 0)} reviews</li>\n'
            )
            html_content += (
                f'                <li class="negative">👎 Negative: {sentiment_summary.get("negative", 0)} reviews</li>\n'
            )
            html_content += f'                <li class="neutral">😐 Neutral: {sentiment_summary.get("neutral", 0)} reviews</li>\n'
            html_content += "            </ul>\n"

        if "sentiment_percentages" in sentiment_analysis:
            percentages = sentiment_analysis["sentiment_percentages"]
            html_content += """            <p><strong>Sentiment Percentages:</strong></p>
            <ul>
"""
            html_content += f"                <li>Positive: {percentages.get('positive', 0)}%</li>\n"
            html_content += f"                <li>Negative: {percentages.get('negative', 0)}%</li>\n"
            html_content += f"                <li>Neutral: {percentages.get('neutral', 0)}%</li>\n"
            html_content += "            </ul>\n"
    else:
        html_content += """            <div class="warning">
                <strong>⚠️ Data Not Available</strong><br>
                Customer sentiment analysis data could not be accessed at this time. Please try again later or check data connectivity.
            </div>
"""

    html_content += """        </div>

        <div class="section">
            <h2><span class="emoji">📈</span>Market Trend Analysis</h2>
"""

    if "error" not in market_trends:
        category = market_trends.get("category", "Unknown")
        market_sentiment = market_trends.get("market_sentiment", "unknown")

        html_content += f'            <div class="metric"><strong>Product Category:</strong> {category.title()}</div>\n'
        html_content += f'            <div class="metric {market_sentiment}"><strong>Market Sentiment:</strong> {market_sentiment.title()}</div>\n'

        if "current_metrics" in market_trends:
            metrics = market_trends["current_metrics"]
            html_content += """            <p><strong>Current Market Metrics:</strong></p>
            <ul>
"""
            html_content += f"                <li>Search Volume Index: {metrics.get('search_volume', 'N/A')}</li>\n"
            html_content += f"                <li>Price Index: {metrics.get('price_index', 'N/A')}</li>\n"
            html_content += f"                <li>Competition Index: {metrics.get('competition_index', 'N/A')}</li>\n"
            html_content += "            </ul>\n"

        if "trend_changes" in market_trends:
            changes = market_trends["trend_changes"]
            html_content += """            <p><strong>Trend Changes:</strong></p>
            <ul>
"""
            html_content += (
                f"                <li>Monthly Search Change: {changes.get('monthly_search_change_percent', 'N/A')}%</li>\n"
            )
            html_content += (
                f"                <li>Monthly Price Change: {changes.get('monthly_price_change_percent', 'N/A')}%</li>\n"
            )
            html_content += f"                <li>6-Month Growth: {changes.get('six_month_growth_percent', 'N/A')}%</li>\n"
            html_content += "            </ul>\n"

        if "insights" in market_trends and market_trends["insights"]:
            html_content += """            <p><strong>Key Market Insights:</strong></p>
            <ul>
"""
            for insight in market_trends["insights"]:
                html_content += f"                <li>{insight}</li>\n"
            html_content += "            </ul>\n"
    else:
        html_content += """            <div class="warning">
                <strong>⚠️ Data Not Available</strong><br>
                Market trend analysis data could not be accessed at this time. Please try again later or check data connectivity.
            </div>
"""

    html_content += """        </div>

        <div class="section recommendations">
            <h2><span class="emoji">💡</span>Recommendations</h2>
            <p>Based on the analysis above, here are key recommendations:</p>
            <ul>
"""

    recommendations = _generate_recommendations(sentiment_analysis, market_trends)
    for rec in recommendations:
        html_content += f"                <li>{rec}</li>\n"

    html_content += f"""            </ul>
        </div>

        <div class="data-sources">
            <h2><span class="emoji">📊</span>Data Sources</h2>
            <ul>
                <li><strong>Product Information:</strong> Internal product database</li>
                <li><strong>Customer Reviews:</strong> Aggregated from multiple retail platforms</li>
                <li><strong>Market Trends:</strong> Market analysis database</li>
            </ul>
        </div>

        <div class="footer">
            Report generated automatically on {report_date}
        </div>
    </div>
</body>
</html>"""

    return html_content


def _generate_recommendations(sentiment_analysis: dict[str, Any], market_trends: dict[str, Any]) -> list[str]:
    recommendations = []

    if "error" not in sentiment_analysis:
        overall_sentiment = sentiment_analysis.get("overall_sentiment", "")
        avg_rating = sentiment_analysis.get("average_rating", 0)

        if overall_sentiment == "positive" and avg_rating >= 4:
            recommendations.append("Strong customer satisfaction - consider expanding marketing efforts")
        elif overall_sentiment == "negative" or avg_rating < 3:
            recommendations.append("Address customer concerns to improve satisfaction ratings")

        if "sentiment_percentages" in sentiment_analysis:
            negative_pct = sentiment_analysis["sentiment_percentages"].get("negative", 0)
            if negative_pct > 30:
                recommendations.append("High negative sentiment - investigate common customer complaints")

    if "error" not in market_trends:
        market_sentiment = market_trends.get("market_sentiment", "")

        if market_sentiment == "bullish":
            recommendations.append("Positive market trends - good time for product promotion")
        elif market_sentiment == "bearish":
            recommendations.append("Market challenges detected - focus on competitive differentiation")

        if "trend_changes" in market_trends:
            growth = market_trends["trend_changes"].get("six_month_growth_percent", 0)
            if growth > 15:
                recommendations.append("Strong growth trend - consider increasing inventory")
            elif growth < -10:
                recommendations.append("Declining trend - review pricing and positioning strategy")

    if not recommendations:
        if "error" in sentiment_analysis and "error" in market_trends:
            recommendations.append("Data sources are currently unavailable - please ensure connectivity and try again")
            recommendations.append("Once data is accessible, re-run analysis for actionable insights")
        else:
            recommendations.append("Continue monitoring market conditions and customer feedback")

    return recommendations
