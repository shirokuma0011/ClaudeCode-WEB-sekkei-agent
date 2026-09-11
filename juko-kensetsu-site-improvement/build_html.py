#!/usr/bin/env python3
"""設計書Markdown一式を1枚のHTMLに結合する（画像は相対パスで参照）。"""
import os, re, glob, html
import markdown

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(BASE, 'docs')

TITLES = {
    '00': 'エグゼクティブサマリー', '01': '現状分析', '02': 'ターゲットとゴール設計',
    '03': 'サイト構成・URL設計', '04': 'ページ別設計', '05': 'デザインガイドライン',
    '06': 'SEO・集客設計', '07': '技術要件・実装仕様', '08': 'コンテンツ制作計画',
    '09': '計測設計とKPI', '10': '実施計画・体制・概算費用', '11': '前提条件と要確認事項',
}

CSS = """
:root{--pri:#2F5D4B;--pri-d:#1E3F33;--acc:#C4933F;--base:#F6F2EA;--txt:#2B2B2B;--sub:#6B6B6B;--bd:#D9D2C5}
*{box-sizing:border-box}
body{margin:0;font-family:"Hiragino Kaku Gothic ProN","Yu Gothic","Noto Sans JP","IPAPGothic",sans-serif;
     color:var(--txt);line-height:1.9;font-size:15px;background:#fff}
.wrap{max-width:1000px;margin:0 auto;padding:0 24px 120px}
header.doc{background:var(--pri-d);color:#fff;padding:56px 24px;margin-bottom:40px}
header.doc .inner{max-width:1000px;margin:0 auto}
header.doc h1{font-size:30px;margin:0 0 10px;font-weight:700;letter-spacing:.04em;color:#fff}
header.doc p{margin:4px 0;opacity:.9;font-size:14px}
nav.toc{background:var(--base);border:1px solid var(--bd);padding:24px 28px;margin:0 0 48px;border-radius:3px}
nav.toc h2{margin:0 0 12px;font-size:17px;color:var(--pri-d)}
nav.toc ol{margin:0;padding-left:22px}
nav.toc li{margin:5px 0}
nav.toc a{color:var(--pri);text-decoration:none}
nav.toc a:hover{text-decoration:underline}
section.chapter{margin:0 0 72px;padding-top:24px;border-top:3px solid var(--pri);}
h1,h2,h3,h4{line-height:1.45;letter-spacing:.03em}
h1{font-size:26px;color:var(--pri-d);margin:16px 0 20px}
h2{font-size:21px;color:var(--pri-d);margin:40px 0 14px;padding-left:12px;border-left:5px solid var(--acc)}
h3{font-size:17px;margin:28px 0 10px;color:var(--pri)}
h4{font-size:15px;margin:20px 0 8px}
.tw{overflow-x:auto;margin:16px 0;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%;margin:0;font-size:13.5px}
th,td{border:1px solid var(--bd);padding:8px 11px;text-align:left;vertical-align:top}
th{background:var(--base);font-weight:700;white-space:nowrap}
td code,th code{white-space:nowrap}
code{background:#F2F0EB;padding:2px 5px;border-radius:2px;font-size:.9em;
     font-family:"SF Mono",Consolas,"Courier New",monospace}
pre{background:#1E2320;color:#E8E6E1;padding:16px 18px;border-radius:3px;overflow-x:auto;font-size:12.5px;line-height:1.65}
pre code{background:none;color:inherit;padding:0}
blockquote{margin:16px 0;padding:12px 18px;background:#FFF8E9;border-left:4px solid var(--acc);color:#5A4520}
blockquote p{margin:4px 0}
ul,ol{padding-left:26px}
li{margin:5px 0}
hr{border:0;border-top:1px solid var(--bd);margin:40px 0}
a{color:var(--pri)}
img{max-width:100%;height:auto;border:1px solid var(--bd);border-radius:2px;display:block;margin:12px 0}
figure{margin:24px 0;padding:16px;background:var(--base);border:1px solid var(--bd);border-radius:3px}
figure figcaption{font-size:13px;color:var(--sub);margin-bottom:8px;font-weight:700}
.figs{margin:32px 0}
strong{font-weight:700}
@media print{header.doc{background:#1E3F33 !important;-webkit-print-color-adjust:exact;print-color-adjust:exact}
  section.chapter{page-break-before:always}
  nav.toc{page-break-after:always}}
@media (max-width:767px){.wrap{padding:0 16px 60px}header.doc{padding:32px 16px}header.doc h1{font-size:22px}
  h1{font-size:21px}h2{font-size:18px}table{font-size:12px;min-width:520px}th,td{padding:6px 7px;white-space:normal}
  .tw{border:1px solid var(--bd);border-radius:2px}}
"""

md = markdown.Markdown(extensions=['tables', 'fenced_code', 'attr_list', 'sane_lists'])

def slug(n): return 'ch' + n

parts = []
toc = []
for path in sorted(glob.glob(os.path.join(DOCS, '*.md'))):
    num = os.path.basename(path)[:2]
    title = TITLES.get(num, os.path.basename(path))
    with open(path, encoding='utf-8') as f:
        text = f.read()
    # 先頭の「# NN. タイトル」行は章ヘッダとして使うので除去
    text = re.sub(r'^#\s+.*?\n', '', text, count=1)
    md.reset()
    body = md.convert(text)
    body = body.replace('<table>', '<div class="tw"><table>').replace('</table>', '</table></div>')
    # images/xxx.png への参照を <img> として拾えるようにはしない（本文中はコード参照のため）
    toc.append((num, title))
    parts.append(
        f'<section class="chapter" id="{slug(num)}">'
        f'<h1>{num}. {html.escape(title)}</h1>{body}</section>'
    )

# 図版ギャラリー
FIGS = [
    ('01_sitemap_current.png', '現行サイト構成（推定）'),
    ('02_sitemap_proposed.png', '提案サイト構成'),
    ('03_user_flow.png', 'ユーザー導線図'),
    ('04_design_tokens.png', 'カラー・タイポグラフィ仕様'),
    ('05_priority_matrix.png', '改善施策 優先度マトリクス'),
    ('06_layout_grid.png', '共通レイアウト・グリッド仕様'),
    ('10_wf_top_pc.png', 'ワイヤーフレーム：トップページ（PC）'),
    ('11_wf_top_sp.png', 'ワイヤーフレーム：トップページ（スマートフォン）'),
    ('12_wf_concept_pc.png', 'ワイヤーフレーム：家づくりのこだわり'),
    ('13_wf_works_list_pc.png', 'ワイヤーフレーム：施工事例 一覧'),
    ('14_wf_works_detail_pc.png', 'ワイヤーフレーム：施工事例 詳細'),
    ('15_wf_voice_pc.png', 'ワイヤーフレーム：お客様の声'),
    ('16_wf_flow_pc.png', 'ワイヤーフレーム：家づくりの流れ・費用'),
    ('17_wf_company_pc.png', 'ワイヤーフレーム：会社案内'),
    ('18_wf_contact_pc.png', 'ワイヤーフレーム：お問い合わせ（PC）'),
    ('19_wf_contact_sp.png', 'ワイヤーフレーム：お問い合わせ（スマートフォン）'),
]
figs_html = ['<section class="chapter" id="figs"><h1>付録. 図版一覧</h1><div class="figs">']
for fn, cap in FIGS:
    if os.path.exists(os.path.join(BASE, 'images', fn)):
        figs_html.append(
            f'<figure><figcaption>{html.escape(cap)}　<code>images/{fn}</code></figcaption>'
            f'<img src="images/{fn}" alt="{html.escape(cap)}" loading="lazy"></figure>')
    else:
        figs_html.append(f'<figure><figcaption>{html.escape(cap)}（未生成: images/{fn}）</figcaption></figure>')
figs_html.append('</div></section>')

toc_html = '\n'.join(
    f'<li><a href="#{slug(n)}">{n}. {html.escape(t)}</a></li>' for n, t in toc
) + '<li><a href="#figs">付録. 図版一覧</a></li>'

out = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>重光建設株式会社 Webサイト改善設計書 v1.0</title>
<style>{CSS}</style>
</head>
<body>
<header class="doc"><div class="inner">
<h1>重光建設株式会社　Webサイト改善設計書</h1>
<p>対象サイト: https://www.juko-kensetsu.co.jp/　／　バージョン 1.0　／　作成日 2026-09-11</p>
<p>設計事務所が原点という強みを、施工事例と第三者の声で裏づけ、スマートフォンから相談できる状態にする。</p>
</div></header>
<div class="wrap">
<nav class="toc"><h2>目次</h2><ol>{toc_html}</ol></nav>
<blockquote><p><strong>重要な前提</strong>：本設計書の作成環境ではネットワーク制限により対象サイト本体へアクセスできませんでした。
現状分析は公開情報からの推定を含みます。事実確認が必要な項目は第11章に一覧化しています。実装着手前に必ず実機で照合してください。</p></blockquote>
{''.join(parts)}
{''.join(figs_html)}
</div>
</body>
</html>"""

with open(os.path.join(BASE, '設計書_全文.html'), 'w', encoding='utf-8') as f:
    f.write(out)
print('built: 設計書_全文.html', len(out), 'bytes')
