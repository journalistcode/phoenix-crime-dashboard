Run instructions for the packaged app
==================================

This package contains a Streamlit app and a small helper to run it as a local 'executable' (one-click runner).

Windows:
 - Double-click run.bat (or run it from command line). It will create a virtual environment in the folder (.venv), install required Python packages, and start the app at http://localhost:8501.
 - Make sure `python` is on PATH and is Python 3.8+.

Linux / macOS:
 - Open a terminal in this folder and run `./run.sh` (or double-click and choose 'Run in Terminal'). The script will create a `.venv` virtual environment, install dependencies, and launch the app at http://localhost:8501.
 - Make sure `python3` is installed.

Notes:
 - The first run will download and install packages and can take a few minutes.
 - If you prefer a single-file native executable, I can attempt to create one using PyInstaller (Linux only in this environment) — let me know and I'll try, but compatibility for Streamlit apps in single-file form can be tricky.
