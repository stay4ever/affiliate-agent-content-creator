# ContentCreator

AI-powered SEO content generation agent for affiliate marketing. Part of the
affiliate agent marketplace ecosystem.

## Overview

ContentCreator is a standalone agent that generates professional affiliate
marketing content. It supports six content types, each with tailored templates,
section structures, and SEO optimization.

## Installation

```bash
pip install affiliate-agent-content-creator
```

## Quick Start

### CLI

```bash
# Generate a product review
content-creator "Sony WH-1000XM5 Headphones" --type review --keyword "best noise cancelling headphones"

# Generate a comparison article
content-creator "AirPods Pro 2 vs Sony WH-1000XM5" --type comparison --keyword "airpods vs sony"

# Generate a buying guide
content-creator "Best Wireless Headphones 2026" --type buying_guide --verbose
```

### Python API

```python
import asyncio
from affiliate_agent_content_creator.entry import run_content_creator

result = asyncio.run(run_content_creator(
    topic="Sony WH-1000XM5 Wireless Headphones",
    content_type="review",
    keyword="best noise cancelling headphones",
    output_dir="./output",
    verbose=True,
))

print(result["article_path"])
print(result["seo_report"])
```

## Supported Content Types

| Type         | Word Count Range | Sections | Description                          |
|--------------|------------------|----------|--------------------------------------|
| review       | 2,000 - 3,000    | 9        | In-depth single product review       |
| comparison   | 2,500 - 3,500    | 9        | Side-by-side product comparison      |
| buying_guide | 3,000 - 4,500    | 9        | Comprehensive purchasing guide       |
| how_to       | 1,500 - 2,500    | 7        | Step-by-step instructional article   |
| listicle     | 2,000 - 3,000    | 5        | Curated top-N product list           |
| roundup      | 2,500 - 4,000    | 8        | Category product roundup             |

## Tools

The agent uses two built-in tools:

- **generate_content_brief** - Creates a structured content plan with sections,
  word count targets, CTA placements, and SEO/affiliate guidelines.
- **optimize_content_seo** - Analyzes written content for word count, keyword
  density, heading structure, and provides actionable improvement suggestions.

## Features

- Structured content briefs tailored to each content type
- SEO optimization with keyword density analysis
- FTC-compliant affiliate disclosure templates
- Automatic meta title and description generation
- Markdown output ready for publishing

## License

MIT
