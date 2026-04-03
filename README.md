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

## Docker

The recommended way to run ContentCreator in production is via Docker.
The image is published to the GitHub Container Registry on every push to `main`.

### Pull the latest image

```bash
docker pull ghcr.io/stay4ever/affiliate-agent-content-creator:latest
```

### Run with Docker

```bash
docker run --rm \
  --env ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  --env ANTHROPIC_MODEL="claude-haiku-4-5" \
  -v "$(pwd)/output:/app/output" \
  ghcr.io/stay4ever/affiliate-agent-content-creator:latest \
  "Best Running Shoes 2025" --type buying_guide
```

**Key flags:**
- `--env ANTHROPIC_API_KEY` — required; never bake this into the image
- `-v "$(pwd)/output:/app/output"` — mount a host directory to persist generated Markdown files
- `--env ANTHROPIC_MODEL` — optional; defaults to `claude-haiku-4-5`

### Run with Docker Compose

```bash
# 1. Copy the example environment file and fill in your API key
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...

# 2. Start the agent
docker compose run --rm affiliate-agent "Best Wireless Headphones 2026" --type roundup
```

### Build the image locally

```bash
docker build -t affiliate-agent .
docker run --rm \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -v "$(pwd)/output:/app/output" \
  affiliate-agent "Sony WH-1000XM5" --type review
```

### Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | ✅ Yes | — | Your Anthropic API key |
| `ANTHROPIC_MODEL` | No | `claude-haiku-4-5` | Model to use for generation |
| `ANTHROPIC_MAX_TOKENS` | No | `8192` | Global token ceiling per call |
| `ANTHROPIC_MAX_TOKENS_REVIEW` | No | — | Per-type override for reviews |
| `ANTHROPIC_MAX_TOKENS_BUYING_GUIDE` | No | — | Per-type override for buying guides |
| `ANTHROPIC_MAX_TOKENS_COMPARISON` | No | — | Per-type override for comparisons |
| `ANTHROPIC_MAX_TOKENS_HOW_TO` | No | — | Per-type override for how-to guides |
| `ANTHROPIC_MAX_TOKENS_LISTICLE` | No | — | Per-type override for listicles |
| `ANTHROPIC_MAX_TOKENS_ROUNDUP` | No | — | Per-type override for roundups |
| `CONTENT_OUTPUT_DIR` | No | `./output` | Directory for generated Markdown files |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity (`DEBUG` or `INFO`) |

See `.env.example` for the full annotated reference.

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
