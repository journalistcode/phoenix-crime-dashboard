@echo off
REM One-click runner for Windows (PowerShell preferred)
IF NOT EXIST ".venv\Scripts\python.exe" (
  python -m venv .venv
)
.venv\Scripts\pip.exe install --upgrade pip
IF EXIST requirements_streamlit.txt (
  .venv\Scripts\pip.exe install -r requirements_streamlit.txt
) ELSE (
  .venv\Scripts\pip.exe install pandas plotly streamlit
)
echo Starting Streamlit app...
.venv\Scripts\streamlit.exe run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
pause
