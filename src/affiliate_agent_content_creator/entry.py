"""Entry point for the ContentCreator agent."""

import asyncio
import json
import os
import sys
from pathlib import Path

from .agent import SYSTEM_PROMPT, get_agent_definition
from .tools import generate_content_brief, optimize_content_seo


async def run_content_creator(
    topic: str,
    content_type: str = "review",
    keyword: str = "",
    output_dir: str = "./output",
    model: str | None = None,
    max_budget_usd: float | None = None,
    verbose: bool = False,
) -> dict:
    """Run the ContentCreator agent to generate affiliate content.

    Args:
        topic: The topic or product to write about.
        content_type: One of review, comparison, buying_guide, how_to,
            listicle, roundup.
        keyword: Target SEO keyword. Defaults to the topic if empty.
        output_dir: Directory to save the generated article.
        model: Optional model override for the underlying LLM.
        max_budget_usd: Optional spending cap for the run.
        verbose: Enable verbose logging.

    Returns:
        A dict with keys: article_path, seo_report, brief.
    """
    target_keyword = keyword or topic

    if verbose:
        print(f"[ContentCreator] Topic: {topic}")
        print(f"[ContentCreator] Content type: {content_type}")
        print(f"[ContentCreator] Target keyword: {target_keyword}")

    # Step 1 - Generate content brief
    if verbose:
        print("[ContentCreator] Generating content brief...")
    brief_json = generate_content_brief(content_type, target_keyword, context=topic)
    brief = json.loads(brief_json)

    if "error" in brief:
        raise ValueError(brief["error"])

    if verbose:
        print(f"[ContentCreator] Brief generated: {len(brief['recommended_sections'])} sections")

    # Step 2 - Build the prompt for the LLM
    prompt = _build_prompt(topic, content_type, target_keyword, brief)

    if verbose:
        print("[ContentCreator] Prompt built, ready for LLM execution.")

    # Step 3 - Execute via affiliate-agent-core (if available) or return prompt
    article_content = None
    try:
        from affiliate_agent_core import run_agent  # type: ignore[import-untyped]

        result = await run_agent(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=prompt,
            model=model,
            max_budget_usd=max_budget_usd,
        )
        article_content = result.get("output", "")
    except ImportError:
        if verbose:
            print(
                "[ContentCreator] affiliate-agent-core not installed. "
                "Returning prompt only."
            )
        article_content = (
            f"<!-- LLM execution skipped: affiliate-agent-core not installed -->\n"
            f"<!-- Prompt that would be sent: -->\n\n{prompt}"
        )

    # Step 4 - SEO optimization check
    if verbose:
        print("[ContentCreator] Running SEO optimization check...")
    seo_json = optimize_content_seo(article_content, target_keyword)
    seo_report = json.loads(seo_json)

    if verbose:
        print(f"[ContentCreator] SEO report: {json.dumps(seo_report, indent=2)}")

    # Step 5 - Save output
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    safe_topic = topic.lower().replace(" ", "-")[:50]
    filename = f"{content_type}-{safe_topic}.md"
    article_path = output_path / filename

    article_path.write_text(article_content, encoding="utf-8")

    if verbose:
        print(f"[ContentCreator] Article saved to {article_path}")

    return {
        "article_path": str(article_path),
        "seo_report": seo_report,
        "brief": brief,
    }


def _build_prompt(
    topic: str,
    content_type: str,
    target_keyword: str,
    brief: dict,
) -> str:
    """Build the user prompt that instructs the LLM to write the article."""
    sections_list = "\n".join(
        f"  {i}. {s}" for i, s in enumerate(brief["recommended_sections"], 1)
    )
    cta_list = "\n".join(f"  - {c}" for c in brief["cta_placements"])
    word_range = brief["target_word_count"]

    return f"""Write a comprehensive {content_type.replace('_', ' ')} article about: {topic}

Target keyword: {target_keyword}

Follow this content brief exactly:

**Recommended Sections:**
{sections_list}

**Target Word Count:** {word_range['min']} - {word_range['max']} words

**CTA Placements:**
{cta_list}

**Requirements:**
1. Use the `generate_content_brief` tool to confirm the article structure.
2. Research the topic thoroughly and write a detailed, helpful article.
3. Include an FTC affiliate disclosure at the very top of the article.
4. Use proper Markdown formatting with H2 (##) and H3 (###) headings.
5. Include a comparison table if relevant to the content type.
6. Add a FAQ section with at least 4 questions.
7. Write a compelling meta title (50-60 chars) and meta description (150-160 chars).
8. Use the `optimize_content_seo` tool to verify the article meets SEO standards.
9. Revise based on SEO feedback before finalizing.

Write the complete article now in Markdown format."""


def main() -> None:
    """CLI entry point for the content-creator command."""
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage: content-creator <topic> [--type TYPE] [--keyword KW] [--verbose]")
        print()
        print("Arguments:")
        print("  topic              The topic or product to write about")
        print()
        print("Options:")
        print("  --type TYPE        Content type: review, comparison, buying_guide,")
        print("                     how_to, listicle, roundup (default: review)")
        print("  --keyword KW       Target SEO keyword (defaults to topic)")
        print("  --verbose          Enable verbose output")
        sys.exit(0)

    topic = args[0]
    content_type = "review"
    keyword = ""
    verbose = False

    i = 1
    while i < len(args):
        if args[i] == "--type" and i + 1 < len(args):
            content_type = args[i + 1]
            i += 2
        elif args[i] == "--keyword" and i + 1 < len(args):
            keyword = args[i + 1]
            i += 2
        elif args[i] == "--verbose":
            verbose = True
            i += 1
        else:
            i += 1

    result = asyncio.run(
        run_content_creator(
            topic=topic,
            content_type=content_type,
            keyword=keyword,
            verbose=verbose,
        )
    )

    print(f"\nArticle saved to: {result['article_path']}")
    print(f"Word count: {result['seo_report']['word_count']}")
    print(f"Keyword density: {result['seo_report']['keyword_density']}%")

    if not all(result["seo_report"]["checks"].values()):
        print("\nSEO Suggestions:")
        for suggestion in result["seo_report"]["suggestions"]:
            print(f"  - {suggestion}")


if __name__ == "__main__":
    main()
