# ContentFactory

An AI-powered content production system that coordinates research, scripting, media generation, and automated video production.

## Vision

ContentFactory aims to turn a topic, trend, or script into a completed video through an orchestrated production workflow.

The system supports:

- Short-form video production
- Long-form video production
- Faceless content
- AI-avatar content
- Trend-to-video workflows
- Script-to-video workflows

## Core Technologies

| Technology | Responsibility |
|---|---|
| Python | Backend and workflow execution |
| Claude | AI reasoning, orchestration, scripting, and production planning |
| ChatGPT | Image generation and editing through supported access |
| Google Gemini / Flow | Image and video generation through supported access |
| Local TTS | Voiceover generation |
| FFmpeg | Video composition and rendering |
| vidIQ | YouTube research and trend discovery |

Provider integrations will initially use existing subscription access where technically supported. API integrations may be introduced later when necessary.

## Architecture

```text
ContentFactory/
├── .claude/
├── apps/
├── backend/
├── integrations/
├── media_engine/
├── workflows/
├── storage/
├── tests/
├── docs/
├── CLAUDE.md
├── README.md
└── pyproject.toml
```

## Production Workflows

### 1. Trend-to-Video

Discover a topic, research it, develop a script, create media assets, generate narration, and render the final video.

### 2. Script-to-Video

Accept an existing script and convert it into a completed video through the production pipeline.

## Development Principles

- Keep the architecture modular.
- Separate AI reasoning from deterministic execution.
- Isolate external provider integrations.
- Reuse components across different production workflows.
- Keep credentials and generated media out of Git.
- Validate each component through automated tests.

## Development Status

**Phase:** Initial project foundation.

Planned implementation milestones:

1. Repository and project setup.
2. Claude orchestration.
3. Media asset management.
4. Image and video generation integrations.
5. Audio generation.
6. Automated video composition.
7. Trend research integration.
8. End-to-end production workflow.

## Current Scope

The initial development focuses on backend orchestration, media integrations, and production automation.

Frontend and dashboard development are intentionally postponed.