"""Launch the full AI Multi-Agent Web Application Generator (Backend + Frontend)."""

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
PYTHON_EXE = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
if not PYTHON_EXE.is_file():
    PYTHON_EXE = Path(sys.executable)


def main():
    print("=" * 65)
    print("  [*] Starting AI Multi-Agent Web Application Generator")
    print("=" * 65)

    # 1. Start Backend FastAPI Server
    print("\n[1/2] Starting Backend FastAPI server on http://127.0.0.1:8000 ...")
    backend_cmd = [
        str(PYTHON_EXE),
        "-m",
        "uvicorn",
        "app.main:app",
        "--reload",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=str(BACKEND_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # 2. Start Frontend Vite Server
    print("[2/2] Starting Frontend Vite UI on http://localhost:5173 ...")
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(FRONTEND_DIR),
    )

    time.sleep(2)
    print("\n" + "=" * 65)
    print("  [SUCCESS] All Services Running!")
    print("  - Frontend UI:  http://localhost:5173")
    print("  - Backend API:  http://127.0.0.1:8000")
    print("  - Swagger Docs: http://127.0.0.1:8000/docs")
    print("=" * 65)
    print("Press Ctrl+C to stop all services.\n")

    try:
        webbrowser.open("http://localhost:5173")
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        backend_proc.terminate()
        frontend_proc.terminate()


if __name__ == "__main__":
    main()
