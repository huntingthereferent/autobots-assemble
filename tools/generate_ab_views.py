"""Legacy entry point; the canonical source is `tools/generate_work_views.py`."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.generate_work_views import *

if __name__ == '__main__':
    main()
