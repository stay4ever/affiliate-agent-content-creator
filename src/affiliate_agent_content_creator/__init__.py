"""affiliate-agent-content-creator — AI-powered SEO content generator.

Public re-exports
-----------------
- ``run_content_creator`` — async coroutine; primary Python API entry point.
- ``ContentType``          — enum of the six supported content types.
- ``ContentResult``        — TypedDict returned by ``run_content_creator``.
"""

from affiliate_agent_content_creator.entry import ContentResult, ContentType, run_content_creator

__all__ = ["run_content_creator", "ContentType", "ContentResult"]
__version__ = "0.1.0"
