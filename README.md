# irir

A Textual-based TUI framework for working with local LLMs (Ollama), managing conversations,
and augmenting prompts with YouTube transcripts.

## Quickstart

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Run the app

```bash
python "Modern TUI.py"
```

### 3) (Optional) Smoke test

```bash
python -m modern_tui.smoke
```

## Usage Highlights

- **Chat with local models** via the model selector (Ollama-backed).
- **Conversation management** (create/rename/delete/export/import).
- **YouTube transcript tools** (summarize/append/replace input).
- **Multi-model sends** with compare view.

## Project Layout

See [ARCHITECTURE.md](ARCHITECTURE.md) for module-level detail. Core entry points:

- `Modern TUI.py` — Thin launcher that runs `modern_tui.app.AIClient`.
- `modern_tui/app.py` — Main Textual app (UI + workflows).
- `modern_tui/workers.py` — Background tasks (summarization, transcripts, spinner).
- `modern_tui/compare.py` — Compare/diff helpers for multi-model responses.
- `modern_tui/conversations.py` — Persistence helpers.
- `modern_tui/smoke.py` — Headless smoke test harness.

## Progress Components

This repo includes two reusable progress modules:

- `modern_tui/progress.py` — Lightweight animated + stateless renderer.
- `modern_tui/progress_enhanced.py` — Full-featured, spring-based progress system.

See [PROGRESS_GUIDE.md](PROGRESS_GUIDE.md) for full documentation and examples.
