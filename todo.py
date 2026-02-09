"""Todo app entry point.

Usage:
    python todo.py          Launch GUI
    python todo.py serve    Start only the API server (for iPhone access)
"""

import sys
import subprocess
import time
import os

SERVER_CMD = [sys.executable, "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def start_server() -> subprocess.Popen:
    """Start the API server as a background process."""
    proc = subprocess.Popen(
        SERVER_CMD,
        cwd=PROJECT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    return proc


def run_serve():
    """Run the server in the foreground."""
    import uvicorn
    print("Starting Todo server on http://0.0.0.0:8000")
    print("Access from iPhone: http://<your-laptop-ip>:8000")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, log_level="info")


def run_gui():
    """Start server in background for iPhone access, then launch the GUI."""
    proc = start_server()
    try:
        from gui import TodoApp
        TodoApp().run()
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        run_serve()
    else:
        run_gui()


if __name__ == "__main__":
    main()
