
# ContentFactory

## Project Overview

ContentFactory is an AI-powered content production system designed to automate and coordinate the creation of short-form and long-form video content.

The system supports two primary workflows:

1. Trend-to-Video: Discover trends, research topics, generate scripts, create media assets, and produce videos.
2. Script-to-Video: Accept an existing script and convert it into a completed video.

## Architecture

Follow the existing repository architecture.

- `backend/`: API, orchestration, workflows, services, and database logic.
- `integrations/`: External provider integrations such as vidIQ, Anthropic, TTS, image generation, and video generation.
- `media_engine/`: Voice processing, subtitles, animations, composition, and rendering.
- `workflows/`: Content production workflows for Shorts, long-form, and faceless content.
- `storage/`: Generated project assets and media.
- `tests/`: Automated tests.
- `docs/`: Technical and project documentation.
- `.claude/`: Claude Code configuration, skills, agents, and rules.

## Development Principles

1. Preserve the established architecture and directory structure.
2. Do not introduce new frameworks or major dependencies without discussing the reason.
3. Keep external integrations isolated from core business logic.
4. Keep AI-driven decisions separate from deterministic processing.
5. Write modular, reusable, testable code.
6. Handle errors explicitly, especially around external APIs and media generation.
7. Never hardcode API keys, tokens, or credentials.
8. Write tests for important business logic and workflows.

## Working Instructions

- Before implementing a feature, inspect the relevant existing code.
- Explain the implementation approach before making significant architectural changes.
- Avoid creating unnecessary files or abstractions.
- Do not modify unrelated modules.
- Update documentation when architecture or behaviour changes.
- Ask before changing the established architecture.

## Current Development Scope

- Focus on backend, AI orchestration, integrations, and media automation.
- Do not build the frontend or dashboard yet.
- Implement the system incrementally, validating each component before moving forward.
