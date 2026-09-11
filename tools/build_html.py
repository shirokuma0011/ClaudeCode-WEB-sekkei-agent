"""docs/muto-coffee/*.md から単一ファイルの HTML 版設計書を生成する。

使い方: python3 tools/build_html.py
出力:   docs/muto-coffee/muto-coffee-sekkei.html
依存:   標準ライブラリのみ。mermaid 図は <pre class="mermaid"> として出力する（Artifact 公開時に描画）。
"""
import re, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "muto-coffee"
OUT = SRC / "muto-coffee-sekkei.html"

CHAPTERS = [
    ("01", "01_overview_requirements.md"),
    ("02", "02_site_structure_url.md"),
    ("03", "03_screen_design.md"),
    ("04", "04_function_data_design.md"),
    ("05", "05_design_nonfunctional.md"),
    ("06", "06_operation_improvement.md"),
    ("99", "99_research_log.md"),
]

TAGS = {"確認済": "ok", "推定": "est", "要確認": "chk", "提案": "prop"}
PRIO = {"必須": "must", "推奨": "rec"}

def esc(s):
    return html.escape(s, quote=False)

def inline(s):
    s = esc(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    def tag(m):
        name = m.group(1)
        cls = TAGS.get(name)
        return f'<span class="tag {cls}">{name}</span>' if cls else m.group(0)
    s = re.sub(r"【(確認済|推定|要確認|提案)】", tag, s)
    return s

def cell(s):
    t = s.strip()
    m = re.match(r"^(確認済|推定|要確認|提案)(?:$|（|／|/| )", t)
    if m:
        name = m.group(1)
        rest = t[len(name):]
        return f'<span class="tag {TAGS[name]}">{name}</span>' + (f' <span class="cell-note">{inline(rest)}</span>' if rest else "")
    m = re.match(r"^(必須|推奨)$", t)
    if m:
        return f'<span class="tag {PRIO[t]}">{t}</span>'
    if re.match(r"^\[ \]$", t):
        return '<span class="box"></span>'
    return inline(t)

def split_row(line):
    line = line.strip()
    if line.startswith("|"): line = line[1:]
    if line.endswith("|"): line = line[:-1]
    parts = re.split(r"(?<!\\)\|", line)
    return [p.replace("\\|", "|") for p in parts]

def is_sep(line):
    return re.match(r"^\s*\|?\s*:?-{2,}", line) is not None and set(line.strip()) <= set("|:- ")

def render_table(rows):
    head = split_row(rows[0])
    body = [split_row(r) for r in rows[2:]]
    out = ['<div class="tbl"><table>', "<thead><tr>"]
    for h in head:
        out.append(f"<th>{inline(h.strip())}</th>")
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>")
        for i, c in enumerate(r):
            out.append(f"<td>{cell(c)}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)

def slug(prefix, text, counter):
    counter[0] += 1
    return f"{prefix}-s{counter[0]}"

def render(md, chap):
    lines = md.splitlines()
    out, toc = [], []
    i, n = 0, len(lines)
    counter = [0]
    para = []
    def flush():
        nonlocal para
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para = []
    title = ""
    while i < n:
        line = lines[i]
        if line.startswith("```"):
            flush()
            lang = line[3:].strip()
            j = i + 1
            buf = []
            while j < n and not lines[j].startswith("```"):
                buf.append(lines[j]); j += 1
            code = "\n".join(buf)
            if lang == "mermaid":
                out.append(f'<div class="dia"><pre class="mermaid">{esc(code)}</pre></div>')
            elif lang == "json":
                out.append(f'<pre class="code"><code>{esc(code)}</code></pre>')
            else:
                out.append(f'<pre class="wire"><code>{esc(code)}</code></pre>')
            i = j + 1
            continue
        if line.startswith("# "):
            flush()
            title = re.sub(r"^\d+\.\s*", "", line[2:].strip())
            i += 1; continue
        m = re.match(r"^(#{2,4})\s+(.*)", line)
        if m:
            flush()
            level = len(m.group(1))
            text = m.group(2).strip()
            sid = slug(chap, text, counter)
            if level == 2:
                toc.append((sid, re.sub(r"^\d+\.\s*", "", text)))
            out.append(f'<h{level} id="{sid}">{inline(text)}</h{level}>')
            i += 1; continue
        if line.strip().startswith("|") and i + 1 < n and is_sep(lines[i + 1]):
            flush()
            rows = [line]
            j = i + 1
            while j < n and lines[j].strip().startswith("|"):
                rows.append(lines[j]); j += 1
            out.append(render_table(rows))
            i = j; continue
        if line.startswith("> "):
            flush()
            buf = []
            while i < n and lines[i].startswith("> "):
                buf.append(lines[i][2:]); i += 1
            out.append(f'<aside class="note">{inline(" ".join(buf))}</aside>')
            continue
        m = re.match(r"^(\s*)- (.*)", line)
        if m:
            flush()
            items = []
            while i < n and re.match(r"^\s*- ", lines[i]):
                items.append(re.match(r"^\s*- (.*)", lines[i]).group(1)); i += 1
            checklist = all(it.startswith("[ ] ") for it in items)
            cls = ' class="check"' if checklist else ""
            out.append(f"<ul{cls}>")
            for it in items:
                if checklist:
                    it = it[4:]
                out.append(f"<li>{inline(it)}</li>")
            out.append("</ul>")
            continue
        m = re.match(r"^\d+\. (.*)", line)
        if m:
            flush()
            out.append("<ol>")
            while i < n and re.match(r"^\d+\. ", lines[i]):
                item = re.match(r"^\d+\. (.*)", lines[i]).group(1)
                out.append(f"<li>{inline(item)}</li>"); i += 1
            out.append("</ol>")
            continue
        if line.strip() == "":
            flush(); i += 1; continue
        para.append(line.strip()); i += 1
    flush()
    return title, "\n".join(out), toc

sections, toc_all = [], []
for num, fname in CHAPTERS:
    title, body, toc = render((SRC / fname).read_text(encoding="utf-8"), f"ch{num}")
    sections.append((num, title, body))
    toc_all.append((num, title, toc))

def section_html(num, title, body):
    label = "付録" if num == "99" else f"第{int(num)}章"
    return f'''<section class="chapter" id="ch{num}">
<header class="ch-head"><span class="ch-num">{num}</span><span class="ch-label">{label}</span><h1>{esc(title)}</h1></header>
{body}
</section>'''

toc_html = []
for num, title, toc in toc_all:
    subs = "".join(f'<li><a href="#{sid}">{esc(t)}</a></li>' for sid, t in toc)
    toc_html.append(f'<li class="toc-ch"><a href="#ch{num}"><span class="toc-num">{num}</span>{esc(title)}</a><ul>{subs}</ul></li>')

CSS = r"""
:root{
  --paper:#F4F3EE; --surface:#FBFAF7; --ink:#1E1915; --ink-2:#5B534B; --ink-3:#8A8177;
  --roast:#4A2E22; --bean:#5F7A32; --bean-soft:#E7EDD9; --copper:#B05E2A; --copper-soft:#F4E3D5;
  --slate:#3B5A78; --slate-soft:#DDE6EE; --stone:#6E6A62; --stone-soft:#E8E5DD;
  --rule:#DAD5C9; --rule-soft:#E9E5DC; --code-bg:#ECE9E0; --link:#4E6A22;
  --shadow:0 1px 0 rgba(30,25,21,.06);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#16130F; --surface:#1E1A15; --ink:#ECE6DA; --ink-2:#B9B0A2; --ink-3:#8B8375;
    --roast:#D8B48F; --bean:#A8C066; --bean-soft:#2A331A; --copper:#E08A52; --copper-soft:#3D2717;
    --slate:#8FB2D3; --slate-soft:#1F2C3A; --stone:#A29B8F; --stone-soft:#2B2823;
    --rule:#3A342B; --rule-soft:#2A2621; --code-bg:#221E18; --link:#B4CB74;
    --shadow:none;
  }
}
:root[data-theme="dark"]{
  --paper:#16130F; --surface:#1E1A15; --ink:#ECE6DA; --ink-2:#B9B0A2; --ink-3:#8B8375;
  --roast:#D8B48F; --bean:#A8C066; --bean-soft:#2A331A; --copper:#E08A52; --copper-soft:#3D2717;
  --slate:#8FB2D3; --slate-soft:#1F2C3A; --stone:#A29B8F; --stone-soft:#2B2823;
  --rule:#3A342B; --rule-soft:#2A2621; --code-bg:#221E18; --link:#B4CB74;
  --shadow:none;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:"IBM Plex Sans JP","Hiragino Sans","Yu Gothic",system-ui,sans-serif;
  font-size:15px; line-height:1.85; padding-inline:16px; padding-block:0;
  -webkit-font-smoothing:antialiased;
}
a{color:var(--link); text-decoration-thickness:1px; text-underline-offset:3px}
a:focus-visible,button:focus-visible{outline:2px solid var(--bean); outline-offset:2px}
code{font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace; font-size:.88em; background:var(--code-bg); padding:.1em .38em; border-radius:3px; color:var(--ink)}
strong{font-weight:600}

/* ---------- masthead ---------- */
.mast{max-width:1180px; margin:0 auto; padding-block:40px 28px; border-bottom:1px solid var(--rule)}
.mast .eyebrow{display:flex; flex-wrap:wrap; gap:8px 18px; align-items:center; color:var(--ink-3); font-size:12px; letter-spacing:.12em; text-transform:uppercase}
.mast .eyebrow .dot{width:6px; height:6px; border-radius:50%; background:var(--bean); display:inline-block}
.mast h1.doc-title{
  font-family:"Shippori Mincho B1","Hiragino Mincho ProN","Yu Mincho",serif; font-weight:600;
  font-size:clamp(28px,4.2vw,44px); line-height:1.25; margin:14px 0 6px; color:var(--roast); text-wrap:balance; letter-spacing:.01em;
}
.mast .sub{font-size:16px; color:var(--ink-2); margin:0 0 26px; max-width:70ch}
.meta{display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px 28px; border-top:1px solid var(--rule); padding-top:18px}
.meta div{display:flex; flex-direction:column; gap:2px; min-width:0}
.meta dt{font-size:11px; letter-spacing:.14em; color:var(--ink-3); text-transform:uppercase}
.meta dd{margin:0; font-size:14px; color:var(--ink); overflow-wrap:anywhere}
.meta dd.num{font-variant-numeric:tabular-nums}
.legend{display:flex; flex-wrap:wrap; gap:10px 22px; margin-top:22px; align-items:center; font-size:13px; color:var(--ink-2)}
.legend .item{display:inline-flex; gap:8px; align-items:center}

/* ---------- layout ---------- */
.wrap{max-width:1180px; margin:0 auto; display:grid; grid-template-columns:1fr; gap:0 56px; padding-block:24px 80px}
.toc{display:none}
@media (min-width:1024px){
  .wrap{grid-template-columns:236px minmax(0,1fr)}
  .toc{display:block; position:sticky; top:0; align-self:start; max-height:100vh; overflow-y:auto; padding-block:28px 40px; padding-right:8px; font-size:13px; scrollbar-width:thin}
}
.toc ul{list-style:none; margin:0; padding:0}
.toc > ul > li{margin-bottom:14px}
.toc a{display:block; color:var(--ink-2); text-decoration:none; line-height:1.45; padding:2px 0 2px 10px; border-left:2px solid transparent}
.toc a:hover{color:var(--ink)}
.toc .toc-ch > a{font-weight:600; color:var(--ink); display:flex; gap:8px}
.toc .toc-num{font-family:"IBM Plex Mono",monospace; color:var(--bean); font-weight:500; font-variant-numeric:tabular-nums}
.toc .toc-ch ul{margin:4px 0 0 0}
.toc .toc-ch ul a{font-size:12px; color:var(--ink-3); padding-left:30px}
.toc a.active{border-left-color:var(--bean); color:var(--ink)}
.toc .toc-ch ul a.active{color:var(--ink)}

main{min-width:0; max-width:820px}
.chapter{padding-block:36px 8px; border-bottom:1px solid var(--rule)}
.chapter:last-of-type{border-bottom:0}
.ch-head{display:grid; grid-template-columns:auto 1fr; gap:2px 14px; align-items:baseline; margin-bottom:22px}
.ch-num{font-family:"IBM Plex Mono",monospace; font-size:34px; line-height:1; color:var(--bean); font-variant-numeric:tabular-nums; grid-row:1/3; align-self:center}
.ch-label{font-size:11px; letter-spacing:.16em; color:var(--ink-3)}
.ch-head h1{font-family:"Shippori Mincho B1","Hiragino Mincho ProN","Yu Mincho",serif; font-weight:600; font-size:clamp(22px,3vw,30px); margin:0; line-height:1.3; color:var(--roast); text-wrap:balance}
h2{font-family:"Shippori Mincho B1","Hiragino Mincho ProN","Yu Mincho",serif; font-weight:600; font-size:21px; line-height:1.35; margin:40px 0 12px; padding-top:14px; border-top:1px solid var(--rule-soft); color:var(--ink); text-wrap:balance}
h3{font-size:15.5px; font-weight:600; margin:26px 0 8px; color:var(--ink); letter-spacing:.01em}
h4{font-size:14px; font-weight:600; margin:18px 0 6px; color:var(--ink-2)}
p{margin:0 0 14px; max-width:72ch}
ul,ol{margin:0 0 16px; padding-left:1.4em; max-width:72ch}
li{margin:3px 0}
li::marker{color:var(--ink-3)}
ul.check{list-style:none; padding-left:0}
ul.check li{display:flex; gap:10px; align-items:flex-start; padding:5px 0; border-bottom:1px dashed var(--rule-soft)}
ul.check li::before{content:""; flex:0 0 auto; width:14px; height:14px; margin-top:6px; border:1.5px solid var(--ink-3); border-radius:3px}
aside.note{border-left:3px solid var(--copper); background:var(--copper-soft); padding:10px 14px; margin:8px 0 18px; font-size:14px; max-width:72ch; border-radius:0 4px 4px 0}

/* ---------- tables ---------- */
.tbl{overflow-x:auto; margin:6px 0 22px; border:1px solid var(--rule); border-radius:4px; background:var(--surface); box-shadow:var(--shadow)}
table{border-collapse:collapse; width:100%; font-size:13.5px; line-height:1.6}
th,td{padding:8px 12px; vertical-align:top; text-align:left; border-bottom:1px solid var(--rule-soft)}
th{font-size:11.5px; letter-spacing:.06em; color:var(--ink-3); font-weight:600; background:var(--paper); white-space:nowrap; border-bottom:1px solid var(--rule)}
tbody tr:last-child td{border-bottom:0}
td{min-width:6ch}
td:first-child{white-space:nowrap}
table code{white-space:nowrap}
.cell-note{color:var(--ink-2); font-size:12.5px}

/* ---------- tags ---------- */
.tag{display:inline-block; font-size:11px; line-height:1; padding:4px 7px 3px; border-radius:3px; letter-spacing:.06em; font-weight:600; white-space:nowrap; vertical-align:middle}
.tag.ok{background:var(--bean-soft); color:var(--bean)}
.tag.est{background:var(--stone-soft); color:var(--stone)}
.tag.chk{background:var(--copper-soft); color:var(--copper)}
.tag.prop{background:var(--slate-soft); color:var(--slate)}
.tag.must{background:var(--roast); color:var(--paper)}
.tag.rec{background:transparent; color:var(--ink-2); border:1px solid var(--rule)}
:root[data-theme="dark"] .tag.must{background:var(--roast); color:#1E1915}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]) .tag.must{color:#1E1915} }

/* ---------- code / wireframes / diagrams ---------- */
pre{margin:6px 0 22px; overflow-x:auto; border-radius:4px; font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace; font-size:12.5px; line-height:1.55}
pre code{background:transparent; padding:0; font-size:inherit}
pre.wire{background:var(--surface); border:1px dashed var(--rule); padding:16px 18px; color:var(--ink-2)}
pre.code{background:var(--code-bg); padding:16px 18px; color:var(--ink)}
.dia{background:var(--surface); border:1px solid var(--rule); border-radius:4px; padding:14px; margin:6px 0 22px; overflow-x:auto}
.dia pre.mermaid{margin:0; background:transparent; overflow:visible}
.dia svg{max-width:100%; height:auto}

/* ---------- footer ---------- */
.foot{max-width:1180px; margin:0 auto; padding-block:20px 40px; border-top:1px solid var(--rule); font-size:12.5px; color:var(--ink-3); display:flex; flex-wrap:wrap; gap:6px 24px}
"""

JS = r"""
(function(){
  var links = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  if(!links.length || !('IntersectionObserver' in window)) return;
  var map = {};
  links.forEach(function(a){ map[a.getAttribute('href').slice(1)] = a; });
  var targets = Object.keys(map).map(function(id){ return document.getElementById(id); }).filter(Boolean);
  var current = null;
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting){
        if(current) current.classList.remove('active');
        current = map[e.target.id]; if(current) current.classList.add('active');
      }
    });
  }, {rootMargin:'-10% 0px -75% 0px', threshold:0});
  targets.forEach(function(t){ io.observe(t); });
})();
"""

page = f'''<title>MUTO coffee roastery 設計書</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+JP:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Shippori+Mincho+B1:wght@600&display=swap">
<style>{CSS}</style>
<header class="mast">
  <div class="eyebrow"><span class="dot"></span><span>Web サイト設計書</span><span>Version 1.0</span><span>2026-09-11</span></div>
  <h1 class="doc-title">MUTO coffee roastery 設計書</h1>
  <p class="sub">東京・中野の自家焙煎コーヒー店 <a href="https://muto-coffee.com/">muto-coffee.com</a> を対象に、現行サイト（店舗サイト＋オンラインショップ）の構成を整理し、再構築・改修時にそのまま使える設計仕様としてまとめたもの。</p>
  <dl class="meta">
    <div><dt>対象</dt><dd>https://muto-coffee.com/<br>https://www.muto-coffee.com/shop/</dd></div>
    <div><dt>店舗</dt><dd>東京都中野区中野 3-34-18<br><span class="num">11:30–19:00（L.O. 18:00）／ 定休 水・木</span></dd></div>
    <div><dt>運営</dt><dd>株式会社 Lounge M<br>運営責任者 武藤 修一郎</dd></div>
    <div><dt>作成方法</dt><dd>公開情報（検索インデックス・第三者メディア）の調査に基づく。直接アクセスは未実施</dd></div>
  </dl>
  <div class="legend">
    <span class="item"><span class="tag ok">確認済</span>公開ページ・複数メディアで裏付け</span>
    <span class="item"><span class="tag est">推定</span>URL 構造や CMS の仕様から推定</span>
    <span class="item"><span class="tag chk">要確認</span>実機（ブラウザ）での確認が必要</span>
    <span class="item"><span class="tag prop">提案</span>現行に無い、または変更を推奨する設計</span>
  </div>
</header>
<div class="wrap">
  <nav class="toc" aria-label="目次"><ul>{"".join(toc_html)}</ul></nav>
  <main>
{"".join(section_html(*s) for s in sections)}
  </main>
</div>
<footer class="foot"><span>MUTO coffee roastery Webサイト設計書 v1.0</span><span>作成 2026-09-11</span><span>Markdown 原本: docs/muto-coffee/ （ClaudeCode-WEB-sekkei-agent リポジトリ）</span></footer>
<script>{JS}</script>
'''
OUT.write_text(page, encoding="utf-8")
print("wrote", OUT, OUT.stat().st_size, "bytes")
