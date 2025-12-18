import subprocess
import os
import time
import webbrowser
import traceback

try:
    # PyInstaller runtime folder
    RUNTIME_DIR = os.path.dirname(os.path.abspath(__file__))

    PYTHON_EXE = os.path.join(RUNTIME_DIR, "python", "python.exe")
    HOST = "127.0.0.1"
    PORT = "8000"

    print("=== CONNECTING TO THE MATRIX ===")
    print("RUNTIME_DIR:", RUNTIME_DIR)
    print("PYTHON_EXE:", PYTHON_EXE)
    print("Exists:", os.path.exists(PYTHON_EXE))

    server = subprocess.Popen(
        [
            PYTHON_EXE,
            "-m",
            "uvicorn",
            "app:app",
            "--app-dir",
            RUNTIME_DIR,
            "--host",
            HOST,
            "--port",
            PORT,
        ],
        cwd=RUNTIME_DIR
    )

    time.sleep(1)
    webbrowser.open(f"http://{HOST}:{PORT}")

    print(f"Server running at http://{HOST}:{PORT}")
    print("Close this window to stop the server.")

    while True:
        time.sleep(1)

except Exception:
    print("\n=== LAUNCHER CRASHED ===")
    traceback.print_exc()
    input("\nPress Enter to close...")
