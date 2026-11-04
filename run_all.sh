#!/bin/bash
# Install, run security unit tests (no API calls), then run evals for every domain.
set -e
python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
python -m pytest -q tests
for d in hr ecommerce; do
  echo "=== domain: $d ==="
  python -m evals.run_eval --domain "$d"
done
