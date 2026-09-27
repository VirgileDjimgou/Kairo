"""Export the FastAPI OpenAPI schema deterministically.

Usage (from the repository root or any directory):

    python services/api/scripts/export_openapi.py --output docs/api/openapi.json
    python services/api/scripts/export_openapi.py > /tmp/openapi.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))


def render_schema() -> str:
    from app.main import app

    schema = app.openapi()
    return json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=None, help="Write to this path instead of stdout.")
    args = parser.parse_args()

    rendered = render_schema()
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
