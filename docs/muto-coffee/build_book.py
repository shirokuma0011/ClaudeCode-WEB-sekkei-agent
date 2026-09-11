#!/usr/bin/env python3
"""設計書 Markdown 群を 1 つの HTML 冊子にまとめ、PDF も生成する"""
import re, subprocess, html
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parent
FILES = ["README.md", "00_はじめに.md", "01_現状分析と課題.md", "02_サイト設計.md",
         "03_デザインシステム.md", "04_技術要件・SEO・計測設計.md", "05_実装ロードマップ・見積.md"]
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

CSS = """
@page{size:A4;margin:16mm 14mm}
*{box-sizing:border-box}
:root{--paper:#FAF8F5;--cream:#F1EBE3;--roast:#2B211B;--ash:#6B5F57;
  --bean:#6F4A2E;--ember:#B4542A;--line:#DED5CA;--open:#4A7C59;--closed:#A8762B;--error:#A63D2F}
body{font-family:"IPAPGothic","IPAGothic","Noto Sans JP",sans-serif;background:var(--paper);
  color:var(--roast);font-size:10.5pt;line-height:1.85;letter-spacing:.02em;margin:0;padding:0}
.wrap{max-width:190mm;margin:0 auto;padding:0 4mm}
.cover{text-align:center;padding:64mm 0 40mm;page-break-after:always}
.cover .eyebrow{font-size:11pt;letter-spacing:.3em;color:var(--ash);margin-bottom:14mm}
.cover h1{font-size:27pt;font-weight:700;letter-spacing:.06em;line-height:1.45;margin:0 0 8mm}
.cover .site{font-family:monospace;font-size:11pt;color:var(--bean);margin-bottom:16mm}
.cover .meta{font-size:10pt;color:var(--ash);line-height:2.1}
.cover hr{border:none;border-top:2px solid var(--roast);width:60mm;margin:12mm auto}
.cover .warn{margin:18mm auto 0;max-width:150mm;border:1.5px solid var(--closed);
  border-left-width:5px;background:#FBF6EC;padding:6mm 7mm;text-align:left;font-size:9pt;line-height:1.9}
.cover .warn b{display:block;color:var(--closed);font-size:10.5pt;margin-bottom:2mm}
.toc{page-break-after:always;padding-top:6mm}
.toc h2{font-size:16pt;border-bottom:2px solid var(--roast);padding-bottom:3mm;margin-bottom:6mm}
.toc ol{list-style:none;padding:0;counter-reset:c}
.toc li{counter-increment:c;padding:3mm 0;border-bottom:1px dashed var(--line);font-size:11pt}
.toc li::before{content:counter(c,decimal-leading-zero);color:var(--ember);font-weight:700;margin-right:5mm;font-family:monospace}
.toc li span{color:var(--ash);font-size:9pt;display:block;margin-left:13mm;margin-top:1mm}
.doc{page-break-before:always}
h1{font-size:19pt;font-weight:700;letter-spacing:.04em;border-bottom:3px solid var(--roast);
  padding-bottom:3mm;margin:0 0 7mm;page-break-after:avoid}
h2{font-size:14pt;font-weight:700;margin:9mm 0 4mm;padding-left:4mm;
  border-left:5px solid var(--bean);page-break-after:avoid}
h3{font-size:11.5pt;font-weight:700;margin:6mm 0 3mm;color:var(--bean);page-break-after:avoid}
h4{font-size:10.5pt;font-weight:700;margin:5mm 0 2mm}
p{margin:0 0 3.5mm}
ul,ol{margin:0 0 4mm;padding-left:6mm}
li{margin-bottom:1.5mm}
strong{font-weight:700}
code{font-family:monospace;font-size:9pt;background:var(--cream);padding:.5mm 1.5mm;border-radius:1mm}
pre{background:var(--cream);border:1px solid var(--line);border-radius:1mm;padding:4mm 5mm;
  font-size:8.5pt;line-height:1.7;overflow-x:auto;margin:0 0 4mm;page-break-inside:avoid}
pre code{background:none;padding:0;font-size:8.5pt}
blockquote{border-left:4px solid var(--ember);background:#FDF4EF;margin:0 0 4mm;padding:3.5mm 5mm;
  font-size:9.5pt;line-height:1.9}
blockquote p:last-child{margin-bottom:0}
table{width:100%;border-collapse:collapse;font-size:9pt;margin:0 0 5mm;page-break-inside:avoid}
th,td{border:1px solid var(--line);padding:2mm 3mm;text-align:left;vertical-align:top;line-height:1.7}
th{background:var(--cream);font-weight:700}
hr{border:none;border-top:1px solid var(--line);margin:7mm 0}
img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:1mm;
  margin:3mm 0 5mm;page-break-inside:avoid;display:block}
a{color:var(--bean);text-decoration:none;border-bottom:1px solid rgba(111,74,46,.3)}
.figcap{font-size:8.5pt;color:var(--ash);margin:-3mm 0 6mm;text-align:center}
"""

def md_to_html(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    # 画像は相対パスのまま（HTML と同じ階層に置くため、そのまま解決される）
    # 相互リンク(.md)は冊子内では消してテキスト化
    text = re.sub(r"(?<!!)\[([^\]]+)\]\((?!https?:|/)[^)]*\.md[^)]*\)", r"**\1**", text)
    text = re.sub(r"(?<!!)\[([^\]]+)\]\((?!https?:|/)(?:data|tools|images)/[^)]+\)", r"`\1`", text)
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists", "attr_list"])
    # 画像の直後にキャプション
    return body

titles = {
 "README.md": ("目次と概要", "全体像・重要な制約・今すぐできること"),
 "00_はじめに.md": ("はじめに", "目的、調査方法と制約、成果物一覧"),
 "01_現状分析と課題.md": ("現状分析と課題", "店舗プロフィール、現行構成、課題 A〜H と優先度"),
 "02_サイト設計.md": ("サイト設計（情報設計・ワイヤーフレーム）", "統合方針、サイトマップ、全ページの画面設計"),
 "03_デザインシステム.md": ("デザインシステム", "配色、タイポグラフィ、コンポーネント、写真"),
 "04_技術要件・SEO・計測設計.md": ("技術要件・SEO・計測設計", "技術構成、リダイレクト、構造化データ、速度、計測"),
 "05_実装ロードマップ・見積.md": ("実装ロードマップ・見積", "フェーズ 0〜3、工数と費用、運用設計"),
}

parts = [f"<style>{CSS}</style>", '<div class="wrap">']
parts.append("""
<div class="cover">
  <div class="eyebrow">WEB SITE RENEWAL DESIGN DOCUMENT</div>
  <h1>MUTO coffee roastery<br>サイト改善設計書</h1>
  <div class="site">https://muto-coffee.com/</div>
  <hr>
  <div class="meta">
    対象事業者: MUTO coffee roastery（運営: 株式会社 Lounge M）<br>
    所在地: 〒164-0001 東京都中野区中野3-34-18<br>
    作成日: 2026-09-11 ／ 版 1.0
  </div>
  <div class="warn"><b>調査上の制約について</b>
  本設計書を作成した環境では、組織のネットワーク送信ポリシーにより muto-coffee.com への直接アクセスが遮断されていました。
  このためサイト本体の HTML 取得・実画面のスクリーンショット撮影・掲載画像のダウンロードは実行できていません。
  現状分析は、検索エンジン経由で取得できた URL・ページタイトル・スニペットと、第三者媒体の記述を突き合わせて構成しています。
  記述には【確認済】【推定】【要確認】のラベルを付けています。実装着手前に【推定】【要確認】をすべて確認してください。</div>
</div>
""")

toc = ['<div class="toc"><h2>目次</h2><ol>']
for f in FILES:
    t, d = titles[f]
    toc.append(f"<li>{html.escape(t)}<span>{html.escape(d)}</span></li>")
toc.append("</ol></div>")
parts.append("".join(toc))

for f in FILES:
    p = ROOT / f
    parts.append(f'<div class="doc">{md_to_html(p)}</div>')

parts.append("</div>")
out_html = ROOT / "MUTO_coffee_roastery_サイト改善設計書.html"
out_html.write_text("\n".join(parts), encoding="utf-8")
print(f"HTML: {out_html} ({out_html.stat().st_size/1024:.0f}KB)")

out_pdf = ROOT / "MUTO_coffee_roastery_サイト改善設計書.pdf"
subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
                "--no-pdf-header-footer", f"--print-to-pdf={out_pdf}",
                "--virtual-time-budget=20000", f"file://{out_html}"],
               check=True, capture_output=True)
print(f"PDF : {out_pdf} ({out_pdf.stat().st_size/1024/1024:.2f}MB)")
