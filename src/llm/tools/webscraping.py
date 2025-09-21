import json
from datetime import datetime, timedelta
from typing import Any
from fuzzywuzzy import fuzz
from pathlib import Path
from pydantic_ai import RunContext
from loguru import logger


current_dir = Path(__file__).parent
data_dir = current_dir / ".." / ".." / ".." / "data"


def load_retailers():
    retailers_path = data_dir / "retailers.json"
    with open(retailers_path, "r") as f:
        return json.load(f)


def load_products():
    products_path = data_dir / "products.json"
    with open(products_path, "r") as f:
        return json.load(f)


def load_retailer_config():
    config_path = data_dir / "retailer_config.json"
    with open(config_path, "r") as f:
        return json.load(f)


def load_market_data():
    market_path = data_dir / "market_data.json"
    with open(market_path, "r") as f:
        return json.load(f)


def load_reviews():
    reviews_path = data_dir / "reviews.json"
    with open(reviews_path, "r") as f:
        return json.load(f)


retailers = load_retailers()
product_database = load_products()
retailer_config = load_retailer_config()
market_data = load_market_data()
reviews = load_reviews()


def normalize_product_name(product_name: str) -> str:
    return product_name.lower().strip()


def get_most_similar_product(product_name: str) -> str:
    return max(product_database, key=lambda x: fuzz.token_sort_ratio(product_name, x["name"]))["name"]


def generate_delivery_date() -> str:
    days_ahead = market_data["delivery"]["default_days"]
    delivery_date = datetime.now() + timedelta(days=days_ahead)
    return delivery_date.strftime("%Y-%m-%d")


def available_products(ctx: RunContext) -> str:
    ctx.available_products = [product["name"] for product in product_database]
    return json.dumps([product["name"] for product in product_database])


def generate_retailer_data(base_price: float, retailer: str) -> dict[str, Any]:
    # Get retailer-specific configuration
    retailer_info = retailer_config.get(retailer, {})

    # Use fixed price variation
    price_variation = market_data["pricing"]["base_variation"]
    price = round(base_price * price_variation, 2)

    # Get fixed discount from retailer config or use default
    discount_percentage = retailer_info.get("discount", market_data["pricing"]["default_discount"])
    discounted_price = round(price * (1 - discount_percentage / 100), 2) if discount_percentage > 0 else price

    # Get fixed values from retailer config or use defaults
    availability = retailer_info.get("availability", market_data["default_availability"])
    shipping_cost = retailer_info.get("shipping_cost", 9.99)
    promotion = retailer_info.get("promotion", market_data["default_promotion"])
    rating = retailer_info.get("rating", market_data["reviews"]["default_rating"])
    review_count = retailer_info.get("review_count", market_data["reviews"]["default_count"])
    url = retailer_info.get("url_format", f"https://{retailer.lower().replace(' ', '')}.com/product/mock-url")

    return {
        "retailer": retailer,
        "price": discounted_price,
        "original_price": price if discount_percentage > 0 else None,
        "discount_percentage": discount_percentage,
        "currency": "USD",
        "availability": availability,
        "shipping_cost": shipping_cost,
        "estimated_delivery": generate_delivery_date(),
        "promotion": promotion,
        "rating": rating,
        "review_count": review_count,
        "url": url,
        "last_updated": datetime.now().isoformat(),
    }


def generate_rating_distribution(product_info: dict | None = None) -> dict[str, int]:
    if product_info and "rating_distribution" in product_info:
        rating_dist = product_info["rating_distribution"]
        return {
            "5_star": rating_dist["5_star"],
            "4_star": rating_dist["4_star"],
            "3_star": rating_dist["3_star"],
            "2_star": rating_dist["2_star"],
            "1_star": rating_dist["1_star"],
        }
    raise ValueError("Product info does not contain rating distribution")


def fetch_product_data(ctx: RunContext, product_name: str) -> str:
    if product_name not in [product["name"] for product in product_database]:
        return json.dumps({"error": "Product not found"})
    logger.info(f"Product data for product: {product_name} loaded")
    ctx.deps.product_name = product_name

    product_info = next(product for product in product_database if product["name"] == product_name)
    retailer_data = [generate_retailer_data(product_info["base_price"], retailer) for retailer in retailers]
    prices = [data["price"] for data in retailer_data if data["availability"] != "Out of Stock"]
    min_price = min(prices) if prices else None
    max_price = max(prices) if prices else None
    avg_price = round(sum(prices) / len(prices), 2) if prices else None
    ratings = [data["rating"] for data in retailer_data]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else None
    total_reviews = sum(data["review_count"] for data in retailer_data)

    product_info = {
        "product_info": {
            "name": product_info["name"],
            "brand": product_info["brand"],
            "category": product_info["category"],
            "description": product_info["description"],
            "specifications": product_info["specifications"],
        },
        "pricing_data": {
            "min_price": min_price,
            "max_price": max_price,
            "average_price": avg_price,
            "currency": "USD",
            "price_range_percentage": round(((max_price - min_price) / min_price) * 100, 1) if min_price and max_price else None,
        },
        "availability_summary": {
            "total_retailers": len(retailer_data),
            "in_stock_count": len([r for r in retailer_data if r["availability"] == "In Stock"]),
            "out_of_stock_count": len([r for r in retailer_data if r["availability"] == "Out of Stock"]),
            "limited_stock_count": len([r for r in retailer_data if r["availability"] == "Limited Stock"]),
        },
        "rating_summary": {
            "average_rating": avg_rating,
            "total_reviews": total_reviews,
            "rating_distribution": generate_rating_distribution(product_info),
        },
        "retailers": retailer_data,
        "scraping_metadata": {
            "timestamp": datetime.now().isoformat(),
            "search_query": product_name,
            "data_sources": len(retailers),
            "success_rate": 100.0,
        },
    }
    ctx.deps.product_info = product_info
    return json.dumps(product_info)


def fetch_product_reviews(ctx: RunContext, product_name: str) -> str:
    logger.info(f"Fetching reviews for product: {product_name}")

    if product_name not in [product["name"] for product in product_database]:
        return json.dumps({"error": "Product not found"})

    if product_name in reviews:
        ctx.deps.reviews_data = reviews[product_name]
        logger.info(f"Reviews for product: {product_name} loaded")
        return json.dumps(reviews[product_name])
    return json.dumps({"error": "Reviews not found for this product"})
