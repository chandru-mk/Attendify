"""
Attendify Desktop Window Launcher using Python & Web Browser App Mode
"""

import os
import sys
import time
import subprocess
import urllib.request

APP_PORT = 8501
APP_URL = f"http://localhost:{APP_PORT}"


def is_server_running(url):
    try:
        with urllib.request.urlopen(url, timeout=1) as response:
            return response.status == 200
    except Exception:
        return False


def start_streamlit_server():
    """Starts the Streamlit background process."""
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.headless", "true",
        "--server.port", str(APP_PORT)
    ]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def open_desktop_window():
    """Opens a clean standalone app window without browser URL bars."""
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    if os.path.exists(edge_path):
        subprocess.Popen([edge_path, f"--app={APP_URL}", "--window-size=1280,820"])
    elif os.path.exists(chrome_path):
        subprocess.Popen([chrome_path, f"--app={APP_URL}", "--window-size=1280,820"])
    else:
        import webbrowser
        webbrowser.open(APP_URL)


def main():
    print("Launching Attendify Desktop Application...")
    if not is_server_running(APP_URL):
        print("Starting Streamlit engine...")
        start_streamlit_server()
        for _ in range(15):
            time.sleep(1)
            if is_server_running(APP_URL):
                break

    print("Opening standalone application window...")
    open_desktop_window()
    print("Attendify is now running as a desktop app!")


if __name__ == "__main__":
    main()
