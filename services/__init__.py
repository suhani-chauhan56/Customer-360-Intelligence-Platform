"""Root services namespace pointing to streamlit_app/services."""
from pathlib import Path
import sys

_streamlit_app_services = Path(__file__).resolve().parent.parent / "streamlit_app" / "services"
_streamlit_app_dir = Path(__file__).resolve().parent.parent / "streamlit_app"

if str(_streamlit_app_dir) not in sys.path:
    sys.path.insert(0, str(_streamlit_app_dir))

__path__ = [str(_streamlit_app_services)]
