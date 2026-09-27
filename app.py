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

for p in [str(APP_DIR), str(ROOT_DIR)]:
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)

# Execute the primary Streamlit application
import streamlit_app.app
