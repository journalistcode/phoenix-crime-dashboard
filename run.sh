#!/bin/bash
set -e
# One-click runner for Linux / macOS
echo "Creating venv (if not exists)..."
python3 -m venv .venv || true
source .venv/bin/activate
pip install --upgrade pip
if [ -f requirements_streamlit.txt ]; then
  pip install -r requirements_streamlit.txt
elif [ -f requirements_combined.txt ]; then
  pip install -r requirements_combined.txt
else
  pip install pandas plotly streamlit
fi
echo "Starting Streamlit app..."
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
