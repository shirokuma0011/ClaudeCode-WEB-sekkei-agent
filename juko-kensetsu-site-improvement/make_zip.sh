#!/usr/bin/env bash
# 設計書一式をzipにまとめる
set -euo pipefail
cd "$(dirname "$0")"

python3 build_html.py

OUT="重光建設_サイト改善設計書_v1.0.zip"
rm -f "$OUT"

zip -r -q "$OUT" \
  README.md \
  設計書_全文.html \
  docs/ \
  images/ \
  wireframes-src/ \
  build_html.py \
  make_zip.sh \
  -x '*.DS_Store' '*__pycache__*' '*.tmp'

echo "作成: $OUT"
unzip -l "$OUT" | tail -3
