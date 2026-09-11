#!/usr/bin/env bash
#
# fetch-site-assets.sh
# ─────────────────────────────────────────────────────────────────────────
# 現行サイト（www.kyoushin-jt.co.jp）を巡回して以下を取得・生成します。
#
#   1. 全ページのHTML          → _crawl/html/
#   2. 全画像ファイル           → ../assets/originals/
#   3. URL棚卸しCSV            → _crawl/urls.csv       （301リダイレクト表の元データ）
#   4. 画像インベントリCSV      → _crawl/images.csv     （容量・alt有無の棚卸し）
#   5. title/description 一覧   → _crawl/meta.csv       （SEO改善の元データ）
#
# ■ なぜこのスクリプトが必要か
#   本設計書を作成した環境は外部ネットワークが遮断されており、
#   現行サイトの画像を取得して同梱することができませんでした。
#   お手元のPC（ネットワークに繋がる環境）でこれを実行してください。
#
# ■ 使い方
#   chmod +x tools/fetch-site-assets.sh
#   ./tools/fetch-site-assets.sh
#
#   オプション:
#     SITE=https://example.com ./tools/fetch-site-assets.sh   対象サイトを変更
#     DELAY=2 ./tools/fetch-site-assets.sh                     リクエスト間隔(秒)
#
# ■ 必要なもの
#   wget（推奨）または curl、および grep / sed
#   macOS:  brew install wget
#   Ubuntu: sudo apt install wget
#
# ■ マナー
#   相手サーバに負荷をかけないよう、既定で 1秒間隔・同時1接続で巡回します。
#   DELAY を 0 にしないでください。
# ─────────────────────────────────────────────────────────────────────────
set -uo pipefail

SITE="${SITE:-https://www.kyoushin-jt.co.jp}"
DELAY="${DELAY:-1}"
UA="${UA:-Mozilla/5.0 (compatible; SiteAuditBot/1.0; +design-review)}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CRAWL_DIR="$SCRIPT_DIR/_crawl"
HTML_DIR="$CRAWL_DIR/html"
IMG_DIR="$BASE_DIR/assets/originals"

HOST="$(printf '%s' "$SITE" | sed -E 's#^https?://##; s#/.*$##')"

mkdir -p "$HTML_DIR" "$IMG_DIR"

echo "════════════════════════════════════════════════════════════"
echo " サイト資産の取得"
echo "   対象     : $SITE"
echo "   ホスト   : $HOST"
echo "   HTML     : $HTML_DIR"
echo "   画像     : $IMG_DIR"
echo "   間隔     : ${DELAY}秒"
echo "════════════════════════════════════════════════════════════"
echo

# ── 0. 事前確認 ──────────────────────────────────────────────
if ! command -v wget >/dev/null 2>&1; then
  echo "!! wget が見つかりません。"
  echo "   macOS:  brew install wget"
  echo "   Ubuntu: sudo apt install wget"
  echo
  echo "   wget なしで進める場合は、下の [手動取得] の手順を参照してください。"
  echo
  echo "   [手動取得]"
  echo "   1. ブラウザで $SITE を開く"
  echo "   2. 各ページで「名前を付けて保存」→「完全」を選び $HTML_DIR へ保存"
  echo "   3. 画像は保存された _files フォルダから $IMG_DIR へコピー"
  exit 1
fi

echo "→ robots.txt を確認します"
curl -sS -A "$UA" "$SITE/robots.txt" -o "$CRAWL_DIR/robots.txt" 2>/dev/null \
  && { echo "  取得しました:"; sed 's/^/    /' "$CRAWL_DIR/robots.txt" | head -20; } \
  || echo "  robots.txt は取得できませんでした（存在しない可能性があります）"
echo
echo "  ※ robots.txt に Disallow が設定されている場合、そのパスは巡回しないでください。"
echo

# ── 1. サイト全体をミラー ────────────────────────────────────
echo "→ [1/5] サイト全体を巡回します（時間がかかります）"
wget \
  --mirror \
  --page-requisites \
  --adjust-extension \
  --convert-links \
  --no-parent \
  --domains="$HOST" \
  --wait="$DELAY" \
  --random-wait \
  --user-agent="$UA" \
  --execute robots=on \
  --tries=3 \
  --timeout=30 \
  --directory-prefix="$HTML_DIR" \
  --no-verbose \
  --append-output="$CRAWL_DIR/wget.log" \
  "$SITE/" || echo "  （一部のURLで失敗しました。$CRAWL_DIR/wget.log を確認してください）"

SITE_ROOT="$HTML_DIR/$HOST"
echo "  完了: $SITE_ROOT"
echo

# ── 2. 画像を収集 ────────────────────────────────────────────
echo "→ [2/5] 画像を $IMG_DIR に集約します"
IMG_COUNT=0
if [ -d "$SITE_ROOT" ]; then
  while IFS= read -r -d '' f; do
    base="$(basename "$f")"
    dest="$IMG_DIR/$base"
    # 同名ファイルは連番を付けて衝突回避
    if [ -e "$dest" ] && ! cmp -s "$f" "$dest"; then
      n=1
      ext="${base##*.}"; stem="${base%.*}"
      while [ -e "$IMG_DIR/${stem}_$n.$ext" ]; do n=$((n+1)); done
      dest="$IMG_DIR/${stem}_$n.$ext"
    fi
    cp -n "$f" "$dest" 2>/dev/null && IMG_COUNT=$((IMG_COUNT+1))
  done < <(find "$SITE_ROOT" -type f \
             \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \
                -o -iname '*.gif' -o -iname '*.svg' -o -iname '*.webp' \
                -o -iname '*.avif' -o -iname '*.ico' \) -print0)
fi
echo "  $IMG_COUNT 件の画像を保存しました"
echo

# ── 3. URL棚卸しCSV ──────────────────────────────────────────
echo "→ [3/5] URL一覧を作成します（301リダイレクト表の元データ）"
{
  echo "旧URL,ローカルファイル,新URL（記入してください）,備考"
  if [ -d "$SITE_ROOT" ]; then
    find "$SITE_ROOT" -type f -name '*.html' | sort | while read -r f; do
      rel="${f#$SITE_ROOT}"
      url="$SITE${rel%.html}"
      printf '%s,%s,,\n' "$url" "$f"
    done
  fi
} > "$CRAWL_DIR/urls.csv"
URL_COUNT=$(( $(wc -l < "$CRAWL_DIR/urls.csv") - 1 ))
echo "  $URL_COUNT 件: $CRAWL_DIR/urls.csv"
echo "  ※ 設計書 03章5節のリダイレクト表と突合し、漏れがないか確認してください"
echo

# ── 4. 画像インベントリCSV ───────────────────────────────────
echo "→ [4/5] 画像インベントリを作成します"
{
  echo "ファイル名,バイト数,KB,形式,備考"
  find "$IMG_DIR" -type f | sort | while read -r f; do
    sz=$(wc -c < "$f" | tr -d ' ')
    kb=$(( sz / 1024 ))
    ext="${f##*.}"
    note=""
    [ "$kb" -gt 300 ] && note="要圧縮(300KB超)"
    printf '%s,%s,%s,%s,%s\n' "$(basename "$f")" "$sz" "$kb" "$ext" "$note"
  done
} > "$CRAWL_DIR/images.csv"
echo "  $CRAWL_DIR/images.csv"
echo "  ※ 300KB超の画像は 設計書05章7節の基準で再書き出ししてください"
echo

# ── 5. title / description / alt 一覧 ────────────────────────
echo "→ [5/5] title・description・alt欠落を抽出します"
{
  echo "ファイル,title,description,img数,alt欠落数"
  if [ -d "$SITE_ROOT" ]; then
    find "$SITE_ROOT" -type f -name '*.html' | sort | while read -r f; do
      title=$(tr '\n' ' ' < "$f" | grep -oiE '<title[^>]*>[^<]*</title>' | head -1 \
              | sed -E 's/<[^>]+>//g; s/,/、/g; s/^ +| +$//g')
      desc=$(tr '\n' ' ' < "$f" \
             | grep -oiE '<meta[^>]+name=["'"'"']description["'"'"'][^>]*>' | head -1 \
             | grep -oiE 'content=["'"'"'][^"'"'"']*' | sed -E 's/^content=.//; s/,/、/g')
      imgs=$(grep -oiE '<img[^>]*>' "$f" | wc -l | tr -d ' ')
      noalt=$(grep -oiE '<img[^>]*>' "$f" | grep -vic 'alt=' || true)
      printf '%s,"%s","%s",%s,%s\n' "$(basename "$f")" "${title:-（なし）}" "${desc:-（なし）}" "$imgs" "${noalt:-0}"
    done
  fi
} > "$CRAWL_DIR/meta.csv"
echo "  $CRAWL_DIR/meta.csv"
echo "  ※ 設計書07章2節の新title案と突合してください"
echo

echo "════════════════════════════════════════════════════════════"
echo " 完了"
echo "════════════════════════════════════════════════════════════"
echo "  画像     : $IMG_DIR ($IMG_COUNT 件)"
echo "  URL一覧  : $CRAWL_DIR/urls.csv ($URL_COUNT 件)"
echo "  画像一覧 : $CRAWL_DIR/images.csv"
echo "  メタ情報 : $CRAWL_DIR/meta.csv"
echo
echo "  次の手順:"
echo "   1. urls.csv の「新URL」列を設計書03章5節にしたがって埋める"
echo "   2. images.csv で「要圧縮」の画像を洗い出す"
echo "   3. meta.csv で alt欠落数 > 0 のページを特定する"
echo "   4. tools/audit-checklist.md の V-1〜V-10 を埋める"
