"""Todo app entry point.

Usage:
    python todo.py          Launch GUI (connects to cloud API)
    python todo.py serve    Start the API server locally
"""

import sys
import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_serve():
    """Run the server in the foreground (for local development)."""
    import uvicorn
    print("Starting Todo server on http://0.0.0.0:8000")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, log_level="info")


def run_gui():
    """Launch the GUI (talks to the cloud API)."""
    from gui import TodoApp
    TodoApp().run()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        os.chdir(PROJECT_DIR)
        run_serve()
    else:
        run_gui()


if __name__ == "__main__":
    main()
