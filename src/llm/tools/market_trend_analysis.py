import json
from pathlib import Path
from typing import Any
from pydantic_ai import RunContext
from loguru import logger


def _load_market_data() -> dict[str, Any]:
    current_file = Path(__file__)
    data_path = current_file.parent.parent.parent.parent / "data" / "market_trends.json"

    try:
        with open(data_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def analyze_market_trends(ctx: RunContext) -> str:
    product_name = ctx.deps.product_name
    logger.info(f"Analyzing market trends for product: {product_name}")

    logger.info("Loading market data")
    market_data = _load_market_data()
    logger.info("Market data loaded")

    if product_name not in market_data:
        logger.error(f"Market data not found for product: {product_name}")
        return json.dumps({"error": f"Market data not found for product: {product_name}"})

    ctx.deps.market_trends = market_data[product_name]
    logger.info(f"Market trends for product: {product_name} loaded")
    return json.dumps(market_data[product_name])
