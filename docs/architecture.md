# Architecture

Two production modes: `trend_to_video` and `script_to_video` (see `backend/orchestration/models.py`).

- `backend/` — orchestration, services, API, database.
- `integrations/` — vidIQ, Anthropic, TTS, image/video generation adapters.
- `media_engine/` — voice processing, subtitles, animation, composition, rendering.
- `workflows/` — Shorts, long-form and faceless workflows.
- `storage/` — generated assets (git-ignored contents).

Status: only `ProductionJob` and its enums exist so far; everything else is a placeholder.
