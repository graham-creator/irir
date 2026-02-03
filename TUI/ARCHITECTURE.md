# modern_tui — Architecture Overview ✅

Purpose
- A modular Textual-based TUI to interact with local models (Ollama), manage conversations, fetch and summarize YouTube transcripts, and compare multi-model replies.

High-level layout
- `Modern TUI.py` — thin launcher that imports and runs `modern_tui.app.AIClient`.
- `modern_tui/app.py` — main `AIClient` Textual app (UI, workflows, background workers).
- `modern_tui/utils.py` — small utilities (YouTube id extraction, sanitizers).
- `modern_tui/workers.py` — long-running tasks (spinner, transcript fetching, summarization).
- `modern_tui/compare.py` — helpers to extract replies and produce diffs.
- `modern_tui/conversations.py` — persistence helpers for conversations.json.
- `modern_tui/smoke.py` — headless smoke test harness (non-networked validation).

Files added/changed
- `modern_tui/app.py` — moved `AIClient` here for testability and packaging.
- `Modern TUI.py` — now a small launcher that calls `AIClient().run()`.
- `modern_tui/__init__.py` — now exports `AIClient` for convenience.
- `ARCHITECTURE.md` — this document.

Next steps / Recommendations
1. Add unit tests that import `AIClient` and exercise non-UI helpers (mock `ollama`).
2. Move more logic into small, testable functions in `workers` and `compare` for increased coverage.
3. Add integration tests (smoke) to the CI matrix (already present in `modern_tui.smoke`).
4. Optional: provide a lightweight CLI wrapper `modern-tui` for packaged installations.

Design notes
- Avoid side effects on import — heavy setup is inside `app.py` methods and `main()`.
- Global unhandled exception logging is configured in `app.py`.
- UI updates from background work are done via `work(thread=True)` and `call_from_thread` where necessary.
