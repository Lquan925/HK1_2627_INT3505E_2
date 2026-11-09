import sys
from pathlib import Path

# Add src to sys.path so product_api can be found without setting PYTHONPATH
src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from product_api import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)


