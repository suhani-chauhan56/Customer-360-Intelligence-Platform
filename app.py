"""Root Entrypoint for CustomerAtlas Streamlit Web Application.

Enables standard invocation:
    streamlit run app.py
or
    streamlit run streamlit_app/app.py
"""

import sys
from pathlib import Path

# Resolve directory paths
ROOT_DIR = Path(__file__).resolve().parent
APP_DIR = ROOT_DIR / "streamlit_app"

for p in [str(ROOT_DIR), str(APP_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Execute the primary Streamlit application
import streamlit_app.app
