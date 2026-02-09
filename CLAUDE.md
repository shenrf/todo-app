# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A personal todo list app with a FastAPI REST API backend, a tkinter GUI for the laptop, and a mobile-friendly web UI for iPhone access. The GUI talks directly to SQLite; the web UI talks to the API server. Todos are organized into three categories: **Ruofei**, **Ruiqi**, and **Family**.

## Running

```bash
# Launch GUI (auto-starts API server in background for iPhone access)
python todo.py

# Start only the API server (for iPhone/browser access)
python todo.py serve
```

Server runs on `http://0.0.0.0:8000`. Access from iPhone via `http://<laptop-ip>:8000` on the same Wi-Fi.

## Architecture

- **todo.py** — Entry point. `serve` subcommand runs server only; default launches server + GUI.
- **server.py** — FastAPI app. REST API at `/api/todos` (GET/POST/PUT/DELETE). Serves `static/index.html` at `/`.
- **models.py** — SQLite database layer. All DB access goes through functions here (no ORM). DB file: `todos.db` in project root. `CATEGORIES` list defines the three categories; `init_db()` auto-migrates older DBs.
- **gui.py** — tkinter GUI app. Reads/writes directly via models.py (no API round-trip).
- **static/index.html** — Single-file mobile web UI (inline CSS/JS). Dark theme, touch-friendly. Auto-refreshes every 5s.

## Dependencies

`fastapi` and `uvicorn[standard]` in `requirements.txt`. The GUI uses only tkinter (stdlib). Install with `pip install -r requirements.txt`.

## Key Design Decisions

- SQLite with WAL mode for safe concurrent reads from GUI + web.
- No ORM — direct sqlite3 for simplicity in a single-table app.
- GUI reads SQLite directly for snappy local UX; the API server exists for iPhone access.
- GUI spawns the server as a subprocess and terminates it on exit.
- CORS is fully open (`*`) since this is a personal/local tool.
