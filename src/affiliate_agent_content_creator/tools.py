"""MCP tools for ContentCreator agent: content brief generation and SEO optimization."""

import json
import re


# ---------------------------------------------------------------------------
# Content-type templates
# ---------------------------------------------------------------------------

CONTENT_TEMPLATES = {
    "review": {
        "recommended_sections": [
            "Introduction & Product Overview",
            "Key Features & Specifications",
            "Unboxing & First Impressions",
            "Performance & Testing",
            "Pros & Cons",
            "Pricing & Value for Money",
            "Alternatives & Comparisons",
            "FAQ",
            "Final Verdict & Rating",
        ],
        "target_word_count": {"min": 2000, "max": 3000},
        "cta_placements": [
            "After Introduction",
            "After Pros & Cons",
            "After Final Verdict",
        ],
    },
    "comparison": {
        "recommended_sections": [
            "Introduction & Overview",
            "Quick Comparison Table",
            "Product A - Detailed Review",
            "Product B - Detailed Review",
            "Head-to-Head Feature Comparison",
            "Performance Comparison",
            "Pricing & Value Analysis",
            "FAQ",
            "Which Should You Buy? (Verdict)",
        ],
        "target_word_count": {"min": 2500, "max": 3500},
        "cta_placements": [
            "After Comparison Table",
            "After Each Product Review",
            "After Verdict",
        ],
    },
    "buying_guide": {
        "recommended_sections": [
            "Introduction & Why This Guide Matters",
            "What to Look For (Key Buying Criteria)",
            "Top Picks Overview Table",
            "Detailed Product Reviews",
            "Budget Options",
            "Premium Options",
            "How We Tested & Selected",
            "FAQ",
            "Final Recommendations",
        ],
        "target_word_count": {"min": 3000, "max": 4500},
        "cta_placements": [
            "After Top Picks Table",
            "After Each Product Review",
            "After Budget Options",
            "After Final Recommendations",
        ],
    },
    "how_to": {
        "recommended_sections": [
            "Introduction & What You'll Learn",
            "What You'll Need (Tools & Products)",
            "Step-by-Step Instructions",
            "Tips & Best Practices",
            "Common Mistakes to Avoid",
            "FAQ",
            "Conclusion & Next Steps",
        ],
        "target_word_count": {"min": 1500, "max": 2500},
        "cta_placements": [
            "After Tools & Products List",
            "After Conclusion",
        ],
    },
    "listicle": {
        "recommended_sections": [
            "Introduction & Selection Criteria",
            "The List (Numbered Items with Mini-Reviews)",
            "Comparison Table",
            "FAQ",
            "Conclusion & Top Pick",
        ],
        "target_word_count": {"min": 2000, "max": 3000},
        "cta_placements": [
            "After Each List Item",
            "After Conclusion",
        ],
    },
    "roundup": {
        "recommended_sections": [
            "Introduction & Category Overview",
            "How We Chose These Products",
            "Quick Picks Summary Table",
            "Detailed Product Roundup",
            "Best for Specific Use Cases",
            "Pricing Overview",
            "FAQ",
            "Final Thoughts & Recommendations",
        ],
        "target_word_count": {"min": 2500, "max": 4000},
        "cta_placements": [
            "After Quick Picks Table",
            "After Each Product Section",
            "After Final Thoughts",
        ],
    },
}


# ---------------------------------------------------------------------------
# SEO and affiliate guidelines (shared across all content types)
# ---------------------------------------------------------------------------

SEO_GUIDELINES = {
    "keyword_density": "0.5% - 2.5% of total word count",
    "heading_structure": "Use H2 for main sections, H3 for subsections",
    "meta_title_length": "50-60 characters",
    "meta_description_length": "150-160 characters",
    "internal_linking": "Include 2-4 internal links where relevant",
    "image_alt_text": "Include descriptive alt text with target keyword",
    "url_slug": "Use target keyword in a short, readable URL slug",
    "first_paragraph": "Include target keyword naturally in the first 100 words",
}

AFFILIATE_GUIDELINES = {
    "disclosure": "Include FTC affiliate disclosure at the top of the article",
    "link_placement": "Place affiliate links contextually, not in a way that tricks readers",
    "nofollow": "Use rel='nofollow sponsored' on affiliate links",
    "honesty": "Never make claims you cannot substantiate",
    "balance": "Present both pros and cons for every product reviewed",
}


# ---------------------------------------------------------------------------
# Tool: generate_content_brief
# ---------------------------------------------------------------------------

def generate_content_brief(
    content_type: str,
    target_keyword: str,
    context: str = "",
) -> str:
    """Generate a structured content brief for affiliate content creation.

    This tool produces a detailed content plan including recommended sections,
    word count targets, CTA placements, and SEO/affiliate guidelines tailored
    to the requested content type.

    Args:
        content_type: The type of content to generate. One of: review,
            comparison, buying_guide, how_to, listicle, roundup.
        target_keyword: The primary keyword the content should target for SEO.
        context: Optional additional context such as product names, niche
            details, or special requirements.

    Returns:
        A JSON string containing the full content brief.
    """
    content_type = content_type.strip().lower()

    if content_type not in CONTENT_TEMPLATES:
        available = ", ".join(sorted(CONTENT_TEMPLATES.keys()))
        return json.dumps(
            {
                "error": f"Unknown content type '{content_type}'. "
                         f"Available types: {available}"
            },
            indent=2,
        )

    template = CONTENT_TEMPLATES[content_type]

    brief = {
        "content_type": content_type,
        "target_keyword": target_keyword,
        "context": context or "No additional context provided.",
        "recommended_sections": template["recommended_sections"],
        "target_word_count": template["target_word_count"],
        "cta_placements": template["cta_placements"],
        "seo_guidelines": SEO_GUIDELINES,
        "affiliate_guidelines": AFFILIATE_GUIDELINES,
    }

    return json.dumps(brief, indent=2)


# ---------------------------------------------------------------------------
# Tool: optimize_content_seo
# ---------------------------------------------------------------------------

def optimize_content_seo(content: str, target_keyword: str) -> str:
    """Analyze content for SEO quality and provide optimization suggestions.

    This tool checks word count, keyword density, heading structure, and other
    SEO signals, then returns a report with actionable suggestions.

    Args:
        content: The full article text (Markdown) to analyze.
        target_keyword: The primary keyword the content should be optimized for.

    Returns:
        A JSON string containing the SEO analysis report and suggestions.
    """
    target_keyword_lower = target_keyword.strip().lower()

    # ---- Word count ----
    words = content.split()
    word_count = len(words)

    # ---- Keyword analysis ----
    content_lower = content.lower()
    keyword_count = content_lower.count(target_keyword_lower)
    keyword_density = (keyword_count / max(word_count, 1)) * 100

    # ---- Heading analysis ----
    headings = re.findall(r"^#{1,6}\s+.+", content, re.MULTILINE)
    heading_count = len(headings)

    # ---- Checks ----
    word_count_ok = word_count >= 1500
    density_ok = 0.5 <= keyword_density <= 2.5
    headings_ok = heading_count >= 3

    checks = {
        "word_count_ok": word_count_ok,
        "keyword_density_ok": density_ok,
        "headings_ok": headings_ok,
    }

    # ---- Suggestions ----
    suggestions: list[str] = []

    if not word_count_ok:
        suggestions.append(
            f"Content is {word_count} words. Aim for at least 1,500 words "
            f"to improve SEO performance."
        )

    if keyword_density < 0.5:
        suggestions.append(
            f"Keyword density is {keyword_density:.2f}% — too low. "
            f"Include the target keyword '{target_keyword}' more naturally "
            f"throughout the article (aim for 0.5%-2.5%)."
        )
    elif keyword_density > 2.5:
        suggestions.append(
            f"Keyword density is {keyword_density:.2f}% — too high. "
            f"Reduce usage of '{target_keyword}' to avoid keyword stuffing "
            f"(aim for 0.5%-2.5%)."
        )

    if not headings_ok:
        suggestions.append(
            f"Only {heading_count} heading(s) found. Use at least 3 headings "
            f"(H2/H3) to improve readability and SEO."
        )

    # Check for keyword in first 100 words
    first_100 = " ".join(words[:100]).lower()
    if target_keyword_lower not in first_100:
        suggestions.append(
            "Target keyword not found in the first 100 words. "
            "Include it naturally in the opening paragraph."
        )

    # Check for FAQ section
    if "faq" not in content_lower and "frequently asked" not in content_lower:
        suggestions.append(
            "No FAQ section detected. Adding a FAQ section improves "
            "chances of appearing in featured snippets."
        )

    # Check for affiliate disclosure
    disclosure_terms = ["affiliate", "commission", "disclosure"]
    has_disclosure = any(term in content_lower for term in disclosure_terms)
    if not has_disclosure:
        suggestions.append(
            "No affiliate disclosure detected. FTC guidelines require "
            "a clear disclosure when content contains affiliate links."
        )

    if not suggestions:
        suggestions.append("Content looks well-optimized. No major issues found.")

    report = {
        "word_count": word_count,
        "keyword_count": keyword_count,
        "keyword_density": round(keyword_density, 2),
        "heading_count": heading_count,
        "checks": checks,
        "suggestions": suggestions,
    }

    return json.dumps(report, indent=2)
