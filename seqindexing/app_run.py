import sys
from pathlib import Path

# Ensure project root is on sys.path when running as a script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from seqindexing.app import create_app


if __name__ == '__main__':
    server = create_app()
    server.run(debug=True, port=8060, use_reloader=True)

    # dashboard: http://localhost:8060/dashboard/