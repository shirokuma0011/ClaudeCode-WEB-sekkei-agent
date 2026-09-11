#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
capture_site.py — muto-coffee.com のスクリーンショット・掲載画像・メタ情報を収集する

--------------------------------------------------------------------------
なぜこのスクリプトが必要か
--------------------------------------------------------------------------
本設計書を作成したセッションでは、組織のネットワーク送信ポリシー（egress proxy）
により muto-coffee.com への直接アクセスが遮断されており、
サイトの実画面・掲載画像・HTML ソースを取得できませんでした。

このスクリプトを **ネットワーク制限のない環境**（店舗の PC、制作会社の開発機など）
で実行すると、設計書の現状分析を実測値で補強できます。

--------------------------------------------------------------------------
準備
--------------------------------------------------------------------------
    python3 -m pip install playwright requests beautifulsoup4 pillow
    python3 -m playwright install chromium

--------------------------------------------------------------------------
使い方
--------------------------------------------------------------------------
    # 既定（設計書に記載の URL 一覧を対象に取得）
    python3 capture_site.py

    # 出力先を指定
    python3 capture_site.py --out ../images/actual

    # 対象 URL を自分で指定
    python3 capture_site.py --url https://muto-coffee.com/ https://muto-coffee.com/news/

    # サイト内を自動巡回して URL を集めてから取得（最大 60 ページ）
    python3 capture_site.py --crawl --max-pages 60

--------------------------------------------------------------------------
出力
--------------------------------------------------------------------------
    <out>/screenshots/pc/<slug>.png     PC 幅 1440px のフルページ画像
    <out>/screenshots/sp/<slug>.png     スマホ幅 390px のフルページ画像
    <out>/assets/<ファイル名>            ページに掲載されている画像の実体
    <out>/report_pages.csv              URL / title / description / OGP / 見出し / 容量
    <out>/report_images.csv             画像 URL / 寸法 / 容量 / 形式 / alt の有無
    <out>/report_summary.md             要約（重い画像・alt 抜け・title 重複など）

report_images.csv の「判定」列に NG が並ぶ画像が、表示速度を損なっている犯人です。
設計書 04 章 §5（表示速度の要件）の目標値と突き合わせて使ってください。
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

DEFAULT_URLS = [
    "https://muto-coffee.com/",
    "https://muto-coffee.com/news/",
    "https://www.muto-coffee.com/shop/",
    "https://www.muto-coffee.com/shop/help/about",
    "https://www.muto-coffee.com/shop/help/tradelaw",
    # 設計書 data/page_inventory.csv で確認できた商品 ID
    *[f"https://www.muto-coffee.com/shop/products/detail/{i}"
      for i in (8, 10, 11, 12, 15, 17, 20, 34, 37, 41, 55)],
]

# 設計書 04 章 §5.2 の目標値
SIZE_LIMITS = {
    "hero": 250 * 1024,
    "section": 150 * 1024,
    "product": 100 * 1024,
    "thumb": 50 * 1024,
}
GENERIC_SIZE_LIMIT = 200 * 1024  # 一般的な上限として判定に使う

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36 SiteAuditBot/1.0")


def slugify(url: str) -> str:
    """URL をファイル名に使える文字列へ変換する。"""
    p = urlparse(url)
    path = unquote(p.path).strip("/")
    name = f"{p.netloc}_{path}" if path else p.netloc
    name = re.sub(r"[^\w\-.]+", "_", name, flags=re.UNICODE)
    return name[:120] or "index"


def human(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n / 1024 / 1024:.2f} MB"
    if n >= 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n} B"


# --------------------------------------------------------------------------
# 1. スクリーンショットとページ情報
# --------------------------------------------------------------------------
def capture(urls: list[str], out: Path, crawl: bool, max_pages: int) -> tuple[list[dict], list[dict]]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright が見つかりません。\n"
                 "  python3 -m pip install playwright\n"
                 "  python3 -m playwright install chromium")

    pc_dir = out / "screenshots" / "pc"
    sp_dir = out / "screenshots" / "sp"
    pc_dir.mkdir(parents=True, exist_ok=True)
    sp_dir.mkdir(parents=True, exist_ok=True)

    pages: list[dict] = []
    images: list[dict] = []
    seen: set[str] = set()
    queue = list(urls)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx_pc = browser.new_context(viewport={"width": 1440, "height": 900},
                                     user_agent=UA, device_scale_factor=1)
        ctx_sp = browser.new_context(viewport={"width": 390, "height": 844},
                                     user_agent=UA, device_scale_factor=2,
                                     is_mobile=True, has_touch=True)

        while queue and len(seen) < max_pages:
            url = queue.pop(0)
            norm = url.split("#")[0].rstrip("/") or url
            if norm in seen:
                continue
            seen.add(norm)
            slug = slugify(url)
            print(f"[{len(seen):>3}] {url}")

            try:
                page = ctx_pc.new_page()
                resp = page.goto(url, wait_until="networkidle", timeout=45000)
                page.wait_for_timeout(1200)

                info = page.evaluate("""() => {
                    const get = (sel, attr='content') => {
                        const el = document.querySelector(sel);
                        return el ? (el.getAttribute(attr) || '') : '';
                    };
                    return {
                        title: document.title || '',
                        description: get('meta[name="description"]'),
                        ogTitle: get('meta[property="og:title"]'),
                        ogImage: get('meta[property="og:image"]'),
                        canonical: get('link[rel="canonical"]', 'href'),
                        robots: get('meta[name="robots"]'),
                        lang: document.documentElement.lang || '',
                        h1: [...document.querySelectorAll('h1')].map(e => e.innerText.trim()),
                        h2: [...document.querySelectorAll('h2')].map(e => e.innerText.trim()),
                        jsonld: [...document.querySelectorAll('script[type="application/ld+json"]')].length,
                        generator: get('meta[name="generator"]'),
                        images: [...document.querySelectorAll('img')].map(img => ({
                            src: img.currentSrc || img.src || '',
                            alt: img.getAttribute('alt'),
                            w: img.naturalWidth, h: img.naturalHeight,
                            dw: img.getAttribute('width'), dh: img.getAttribute('height'),
                            loading: img.getAttribute('loading') || ''
                        })).filter(i => i.src && !i.src.startsWith('data:')),
                        links: [...document.querySelectorAll('a[href]')].map(a => a.href)
                    };
                }""")

                page.screenshot(path=str(pc_dir / f"{slug}.png"), full_page=True)
                html_bytes = len((page.content() or "").encode("utf-8"))
                page.close()

                sp = ctx_sp.new_page()
                sp.goto(url, wait_until="networkidle", timeout=45000)
                sp.wait_for_timeout(1200)
                sp.screenshot(path=str(sp_dir / f"{slug}.png"), full_page=True)
                sp.close()

                pages.append({
                    "URL": url,
                    "HTTPステータス": resp.status if resp else "",
                    "title": info["title"],
                    "titleの文字数": len(info["title"]),
                    "description": info["description"],
                    "descriptionの文字数": len(info["description"]),
                    "canonical": info["canonical"],
                    "og:title": info["ogTitle"],
                    "og:image": info["ogImage"],
                    "robots": info["robots"],
                    "lang": info["lang"],
                    "generator": info["generator"],
                    "h1の数": len(info["h1"]),
                    "h1": " / ".join(info["h1"]),
                    "h2の数": len(info["h2"]),
                    "JSON-LDの数": info["jsonld"],
                    "img要素の数": len(info["images"]),
                    "HTML容量": human(html_bytes),
                    "PCスクショ": f"screenshots/pc/{slug}.png",
                    "SPスクショ": f"screenshots/sp/{slug}.png",
                })

                for im in info["images"]:
                    images.append({
                        "掲載ページ": url,
                        "画像URL": im["src"],
                        "alt": "" if im["alt"] is None else im["alt"],
                        "alt属性なし": "YES" if im["alt"] is None else "",
                        "実寸幅": im["w"], "実寸高": im["h"],
                        "width属性": im["dw"] or "", "height属性": im["dh"] or "",
                        "loading": im["loading"],
                    })

                if crawl:
                    host = urlparse(url).netloc.replace("www.", "")
                    for link in info["links"]:
                        lp = urlparse(link)
                        if lp.scheme not in ("http", "https"):
                            continue
                        if lp.netloc.replace("www.", "") != host:
                            continue
                        if re.search(r"\.(jpg|jpeg|png|gif|webp|pdf|zip|svg)$", lp.path, re.I):
                            continue
                        n = link.split("#")[0].rstrip("/") or link
                        if n not in seen and link not in queue:
                            queue.append(link)

            except Exception as e:  # 1 ページの失敗で全体を止めない
                print(f"      ! 失敗: {e}")
                pages.append({"URL": url, "HTTPステータス": "ERROR", "title": str(e)})

            time.sleep(0.5)

        browser.close()

    return pages, images


# --------------------------------------------------------------------------
# 2. 画像の実体をダウンロードして寸法・容量を測る
# --------------------------------------------------------------------------
def fetch_images(images: list[dict], out: Path) -> list[dict]:
    try:
        import requests
    except ImportError:
        print("! requests が無いため画像の実体取得をスキップします")
        return images

    try:
        from PIL import Image
        has_pil = True
    except ImportError:
        print("! Pillow が無いため画像の寸法測定を一部スキップします")
        has_pil = False

    asset_dir = out / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    cache: dict[str, dict] = {}
    sess = requests.Session()
    sess.headers["User-Agent"] = UA

    for row in images:
        src = row["画像URL"]
        if src in cache:
            row.update(cache[src])
            continue
        rec = {"容量": "", "容量バイト": 0, "形式": "", "保存先": "", "判定": ""}
        try:
            r = sess.get(src, timeout=30)
            r.raise_for_status()
            data = r.content
            rec["容量"] = human(len(data))
            rec["容量バイト"] = len(data)
            rec["形式"] = (r.headers.get("Content-Type", "") or "").split(";")[0]

            name = slugify(src)[:100]
            ext = Path(urlparse(src).path).suffix or ".bin"
            dest = asset_dir / f"{name}{'' if name.endswith(ext) else ext}"
            dest.write_bytes(data)
            rec["保存先"] = f"assets/{dest.name}"

            if has_pil:
                try:
                    with Image.open(io.BytesIO(data)) as im:
                        rec["形式"] = im.format or rec["形式"]
                        row["実寸幅"] = row["実寸幅"] or im.width
                        row["実寸高"] = row["実寸高"] or im.height
                except Exception:
                    pass

            problems = []
            if len(data) > GENERIC_SIZE_LIMIT:
                problems.append(f"容量超過({human(len(data))})")
            if "webp" not in rec["形式"].lower() and "svg" not in rec["形式"].lower():
                problems.append("WebP未使用")
            if not row.get("width属性") or not row.get("height属性"):
                problems.append("寸法属性なし")
            if row.get("alt属性なし") == "YES":
                problems.append("alt属性なし")
            rec["判定"] = "NG: " + " / ".join(problems) if problems else "OK"

        except Exception as e:
            rec["判定"] = f"取得失敗: {e}"

        cache[src] = rec
        row.update(rec)

    return images


# --------------------------------------------------------------------------
# 3. レポート出力
# --------------------------------------------------------------------------
def write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    keys: list[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(f"  -> {path}")


def write_summary(pages: list[dict], images: list[dict], out: Path) -> None:
    lines = ["# 現状サイト 実測レポート", "",
             f"取得日時: {time.strftime('%Y-%m-%d %H:%M:%S')}",
             f"対象ページ数: {len(pages)}", f"検出画像数(のべ): {len(images)}", ""]

    ng = [i for i in images if str(i.get("判定", "")).startswith("NG")]
    heavy = sorted([i for i in images if i.get("容量バイト", 0) > GENERIC_SIZE_LIMIT],
                   key=lambda x: -x.get("容量バイト", 0))[:20]
    no_alt = [i for i in images if i.get("alt属性なし") == "YES"]
    no_dim = [i for i in images if not i.get("width属性") or not i.get("height属性")]

    lines += ["## 画像の問題", "",
              f"- 何らかの問題がある画像: **{len(ng)} / {len(images)}**",
              f"- alt 属性がない画像: **{len(no_alt)}**",
              f"- width/height 属性がない画像（CLS の原因）: **{len(no_dim)}**",
              f"- {human(GENERIC_SIZE_LIMIT)} を超える画像: **{len([i for i in images if i.get('容量バイト',0) > GENERIC_SIZE_LIMIT])}**", ""]

    if heavy:
        lines += ["### 容量の大きい画像 上位", "", "| 容量 | 画像URL | 掲載ページ |", "|---|---|---|"]
        for i in heavy:
            lines.append(f"| {i.get('容量','')} | {i['画像URL'][:80]} | {i['掲載ページ'][:60]} |")
        lines.append("")

    titles: dict[str, list[str]] = {}
    for p in pages:
        t = p.get("title", "")
        if t:
            titles.setdefault(t, []).append(p["URL"])
    dup = {t: u for t, u in titles.items() if len(u) > 1}

    lines += ["## メタ情報の問題", ""]
    lines.append(f"- description が空のページ: **{len([p for p in pages if not p.get('description')])}**")
    lines.append(f"- canonical が空のページ: **{len([p for p in pages if not p.get('canonical')])}**")
    lines.append(f"- h1 が 0 個または 2 個以上のページ: **{len([p for p in pages if p.get('h1の数') not in (1, None)])}**")
    lines.append(f"- JSON-LD が無いページ: **{len([p for p in pages if not p.get('JSON-LDの数')])}**")
    lines.append(f"- title が重複しているページ群: **{len(dup)}**")
    lines.append("")

    roastary = [p for p in pages if "roastary" in str(p.get("title", "")).lower()]
    if roastary:
        lines += ["### 綴り誤記「roastary」が含まれる title", ""]
        for p in roastary:
            lines.append(f"- {p['URL']} — {p.get('title','')}")
        lines.append("")

    lines += ["## 次にすること", "",
              "1. `report_images.csv` の「判定」列が NG の画像を、設計書 03 章 §6.3 の仕様で書き出し直す",
              "2. `report_pages.csv` の title / description を、設計書 04 章 §4.1 の設計に差し替える",
              "3. スクリーンショットを設計書の `images/actual/` に置き、現状分析の裏付けとする",
              "4. PageSpeed Insights でトップページを計測し、設計書 04 章 §5.1 の目標値と比較する", ""]

    path = out / "report_summary.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  -> {path}")


def main() -> None:
    ap = argparse.ArgumentParser(description="muto-coffee.com の現状を収集する")
    ap.add_argument("--out", default="../images/actual", help="出力先ディレクトリ")
    ap.add_argument("--url", nargs="*", help="対象 URL（省略時は既定の一覧）")
    ap.add_argument("--crawl", action="store_true", help="サイト内リンクを辿って対象を広げる")
    ap.add_argument("--max-pages", type=int, default=40, help="最大取得ページ数")
    ap.add_argument("--skip-assets", action="store_true", help="画像の実体取得を省略する")
    args = ap.parse_args()

    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    urls = args.url or DEFAULT_URLS

    print(f"出力先: {out}")
    print(f"対象  : {len(urls)} URL（crawl={args.crawl}, 上限={args.max_pages}）\n")

    pages, images = capture(urls, out, args.crawl, args.max_pages)

    if not args.skip_assets:
        print("\n画像の実体を取得しています...")
        images = fetch_images(images, out)

    print("\nレポートを出力しています...")
    write_csv(pages, out / "report_pages.csv")
    write_csv(images, out / "report_images.csv")
    write_summary(pages, images, out)

    print(f"\n完了。{len(pages)} ページ / {len(images)} 画像")
    print(f"まず {out / 'report_summary.md'} を開いてください。")


if __name__ == "__main__":
    main()
