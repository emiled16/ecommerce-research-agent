from pydantic_ai import Agent
from dataclasses import dataclass
from pydantic_ai.mcp import MCPServerStdio
from typing import Any
from src.llm.prompt import instructions as agent_instructions


from src.llm.tools.report_generator import generate_product_report
from src.llm.tools.market_trend_analysis import analyze_market_trends
from src.llm.tools.sentiment_analysis import get_product_sentiment_analysis
from src.llm.tools.webscraping import fetch_product_data, fetch_product_reviews, get_most_similar_product, available_products
from src.llm.tools.exit_program import exit_program


@dataclass
class ResearchContext:
    product_name: str | None = None
    product_info: dict[str, Any] | None = None
    reviews_data: dict[str, Any] | None = None
    sentiment_analysis: dict[str, Any] | None = None
    market_trends: dict[str, Any] | None = None
    report_path: str | None = None
    category_trends: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_name": self.product_name,
            "product_info": self.product_info,
            "reviews_data": self.reviews_data,
            "sentiment_analysis": self.sentiment_analysis,
            "market_trends": self.market_trends,
            "report_path": self.report_path,
            "category_trends": self.category_trends,
        }


def generate_research_agent(
    instructions: str = agent_instructions,
    model: str = "anthropic:claude-3-5-sonnet-20240620",
    name: str = "researcher",
    tools: list[MCPServerStdio] = [
        generate_product_report,
        analyze_market_trends,
        get_product_sentiment_analysis,
        fetch_product_data,
        fetch_product_reviews,
        get_most_similar_product,
        available_products,
        exit_program,
    ],
):
    return Agent(
        model=model,
        name=name,
        instructions=instructions,
        tools=tools,
        deps_type=ResearchContext,
    )
