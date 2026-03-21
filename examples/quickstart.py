"""Quickstart example for the ContentCreator agent."""

import asyncio
from affiliate_agent_content_creator.entry import run_content_creator


async def main():
    # Generate a product review
    result = await run_content_creator(
        topic="Sony WH-1000XM5 Wireless Headphones",
        content_type="review",
        keyword="best noise cancelling headphones",
        output_dir="./output",
        verbose=True,
    )

    print(f"\nArticle saved to: {result['article_path']}")
    print(f"Word count: {result['seo_report']['word_count']}")
    print(f"Keyword density: {result['seo_report']['keyword_density']}%")

    # Generate a comparison article
    result = await run_content_creator(
        topic="AirPods Pro 2 vs Sony WH-1000XM5",
        content_type="comparison",
        keyword="airpods pro vs sony xm5",
        output_dir="./output",
        verbose=True,
    )

    print(f"\nArticle saved to: {result['article_path']}")

    # Generate a buying guide
    result = await run_content_creator(
        topic="Best Wireless Headphones 2026",
        content_type="buying_guide",
        keyword="best wireless headphones",
        output_dir="./output",
        verbose=True,
    )

    print(f"\nArticle saved to: {result['article_path']}")


if __name__ == "__main__":
    asyncio.run(main())
