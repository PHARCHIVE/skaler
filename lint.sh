#!/usr/bin/env bash

CWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$CWD"/..

set -e

PY_FILES=$(find . -name "*.py")

python3 -m black .
pylint --errors-only .
# isort phlop tests
python3 -m ruff check .
for FILE in ${PY_FILES[@]}; do
  autoflake -i "$FILE"
done
