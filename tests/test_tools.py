"""Tests for ContentCreator tools."""

import json
import sys
from pathlib import Path

import pytest

# Ensure the package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from affiliate_agent_content_creator.tools import (
    CONTENT_TEMPLATES,
    generate_content_brief,
    optimize_content_seo,
)


# ---------------------------------------------------------------------------
# generate_content_brief tests
# ---------------------------------------------------------------------------


class TestGenerateContentBrief:
    """Tests for the generate_content_brief tool."""

    def test_review_brief(self):
        result = json.loads(generate_content_brief("review", "best headphones"))
        assert result["content_type"] == "review"
        assert result["target_keyword"] == "best headphones"
        assert len(result["recommended_sections"]) == 9
        assert result["target_word_count"]["min"] == 2000
        assert result["target_word_count"]["max"] == 3000
        assert len(result["cta_placements"]) == 3

    def test_comparison_brief(self):
        result = json.loads(generate_content_brief("comparison", "airpods vs sony"))
        assert result["content_type"] == "comparison"
        assert len(result["recommended_sections"]) == 9
        assert result["target_word_count"]["min"] == 2500
        assert result["target_word_count"]["max"] == 3500
        assert len(result["cta_placements"]) == 3

    def test_buying_guide_brief(self):
        result = json.loads(generate_content_brief("buying_guide", "wireless headphones"))
        assert result["content_type"] == "buying_guide"
        assert len(result["recommended_sections"]) == 9
        assert result["target_word_count"]["min"] == 3000
        assert result["target_word_count"]["max"] == 4500
        assert len(result["cta_placements"]) == 4

    def test_how_to_brief(self):
        result = json.loads(generate_content_brief("how_to", "clean headphones"))
        assert result["content_type"] == "how_to"
        assert len(result["recommended_sections"]) == 7
        assert result["target_word_count"]["min"] == 1500
        assert result["target_word_count"]["max"] == 2500
        assert len(result["cta_placements"]) == 2

    def test_listicle_brief(self):
        result = json.loads(generate_content_brief("listicle", "top headphones"))
        assert result["content_type"] == "listicle"
        assert len(result["recommended_sections"]) == 5
        assert result["target_word_count"]["min"] == 2000
        assert result["target_word_count"]["max"] == 3000
        assert len(result["cta_placements"]) == 2

    def test_roundup_brief(self):
        result = json.loads(generate_content_brief("roundup", "headphones roundup"))
        assert result["content_type"] == "roundup"
        assert len(result["recommended_sections"]) == 8
        assert result["target_word_count"]["min"] == 2500
        assert result["target_word_count"]["max"] == 4000
        assert len(result["cta_placements"]) == 3

    def test_unknown_content_type_returns_error(self):
        result = json.loads(generate_content_brief("podcast", "test"))
        assert "error" in result
        assert "podcast" in result["error"]

    def test_brief_includes_seo_guidelines(self):
        result = json.loads(generate_content_brief("review", "test keyword"))
        assert "seo_guidelines" in result
        assert "keyword_density" in result["seo_guidelines"]

    def test_brief_includes_affiliate_guidelines(self):
        result = json.loads(generate_content_brief("review", "test keyword"))
        assert "affiliate_guidelines" in result
        assert "disclosure" in result["affiliate_guidelines"]

    def test_context_is_included(self):
        result = json.loads(
            generate_content_brief("review", "test", context="Extra info here")
        )
        assert result["context"] == "Extra info here"

    def test_empty_context_gets_default(self):
        result = json.loads(generate_content_brief("review", "test"))
        assert result["context"] == "No additional context provided."

    def test_all_content_types_covered(self):
        expected = {"review", "comparison", "buying_guide", "how_to", "listicle", "roundup"}
        assert set(CONTENT_TEMPLATES.keys()) == expected


# ---------------------------------------------------------------------------
# optimize_content_seo tests
# ---------------------------------------------------------------------------


class TestOptimizeContentSeo:
    """Tests for the optimize_content_seo tool."""

    def _make_content(self, word_count=2000, keyword="test keyword", keyword_freq=15):
        """Helper to generate test content with controlled parameters."""
        headings = "## Section One\n\n## Section Two\n\n## Section Three\n\n"
        disclosure = "Disclosure: This post contains affiliate links.\n\n"
        faq = "## FAQ\n\nQ: Is this good?\nA: Yes.\n\n"
        keyword_block = f"{keyword} " * keyword_freq
        filler_count = max(0, word_count - keyword_freq - 50)
        filler = "lorem ipsum dolor sit amet " * (filler_count // 5)
        return f"{disclosure}{headings}{keyword_block}\n\n{filler}\n\n{faq}"

    def test_good_content_passes_all_checks(self):
        content = self._make_content(word_count=2000, keyword_freq=20)
        result = json.loads(optimize_content_seo(content, "test keyword"))
        assert result["checks"]["word_count_ok"] is True
        assert result["word_count"] >= 1500

    def test_short_content_fails_word_count(self):
        content = "## Heading\n\nShort article with test keyword here."
        result = json.loads(optimize_content_seo(content, "test keyword"))
        assert result["checks"]["word_count_ok"] is False
        assert any("1,500 words" in s for s in result["suggestions"])

    def test_low_keyword_density_flagged(self):
        content = self._make_content(word_count=2000, keyword_freq=1)
        result = json.loads(optimize_content_seo(content, "test keyword"))
        assert result["keyword_density"] < 0.5
        assert any("too low" in s for s in result["suggestions"])

    def test_high_keyword_density_flagged(self):
        content = self._make_content(word_count=500, keyword_freq=100)
        result = json.loads(optimize_content_seo(content, "test keyword"))
        assert result["keyword_density"] > 2.5
        assert any("too high" in s for s in result["suggestions"])

    def test_few_headings_flagged(self):
        content = "## Only One Heading\n\n" + "word " * 1600
        result = json.loads(optimize_content_seo(content, "test keyword"))
        assert result["checks"]["headings_ok"] is False

    def test_missing_faq_flagged(self):
        content = "## Heading\n\n## Another\n\n## Third\n\n" + "word " * 1600
        result = json.loads(optimize_content_seo(content, "word"))
        assert any("FAQ" in s for s in result["suggestions"])

    def test_missing_disclosure_flagged(self):
        content = "## Heading\n\n## Another\n\n## Third\n\n" + "word " * 1600
        result = json.loads(optimize_content_seo(content, "word"))
        assert any("disclosure" in s.lower() for s in result["suggestions"])

    def test_keyword_not_in_first_100_words(self):
        filler = "lorem " * 150
        content = f"## Heading\n\n## Two\n\n## Three\n\n{filler}\n\ntest keyword here"
        result = json.loads(optimize_content_seo(content, "test keyword"))
        assert any("first 100 words" in s for s in result["suggestions"])

    def test_report_structure(self):
        content = self._make_content()
        result = json.loads(optimize_content_seo(content, "test keyword"))
        assert "word_count" in result
        assert "keyword_count" in result
        assert "keyword_density" in result
        assert "heading_count" in result
        assert "checks" in result
        assert "suggestions" in result
