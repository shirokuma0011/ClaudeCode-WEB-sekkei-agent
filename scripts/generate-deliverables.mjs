import fs from "node:fs/promises";
import path from "node:path";
import {
  IMAGE_FILENAMES,
  csvEscape,
  htmlEscape,
  parseInputMarkdown,
  projectDirectory
} from "./lib.mjs";

const args = process.argv.slice(2);
const force = args.includes("--force");
const positional = args.filter((arg) => arg !== "--force");
const [inputArgument, projectSlug] = positional;

if (!inputArgument || !projectSlug) {
  console.error("Usage: node scripts/generate-deliverables.mjs <input.md> <project-slug> [--force]");
  process.exit(1);
}

const inputPath = path.resolve(process.cwd(), inputArgument);
const outputDir = projectDirectory(projectSlug);

async function exists(target) {
  try {
    await fs.access(target);
    return true;
  } catch {
    return false;
  }
}

if (!(await exists(inputPath))) {
  throw new Error(`Input file not found: ${inputPath}`);
}

if (await exists(outputDir)) {
  const current = await fs.readdir(outputDir);
  if (current.length > 0 && !force) {
    throw new Error(`Output already exists: ${outputDir}. Use --force only after confirming it may be replaced.`);
  }
  if (force) await fs.rm(outputDir, { recursive: true, force: true });
}

const source = await fs.readFile(inputPath, "utf8");
const fields = parseInputMarkdown(source);
const value = (key, fallback) => fields[key]?.trim() || `[仮設定] ${fallback}`;

const projectName = value("事業名・サービス名", projectSlug.replaceAll("-", " "));
const business = value("事業内容", "事業内容の詳細を公開前に確認してください");
const purpose = value("サイトの目的", "問い合わせ獲得と認知向上");
const audience = value("ターゲット", "事業内容に関心を持つ見込み顧客");
const mood = value("希望する雰囲気", "信頼感、清潔感、現代的、親しみやすい");
const conversion = value("問い合わせ・CV方法", "問い合わせフォーム");
const assets = value("写真素材", "画像生成プロンプト10件を納品");
const implementation = value("実装前提", "HTML/CSS/JavaScript");

const pages = [
  { file: "index.html", name: "ホーム", purpose: "価値を短時間で伝え、主要導線へ案内する" },
  { file: "service.html", name: "サービス", purpose: "提供内容と選び方を具体的に説明する" },
  { file: "about.html", name: "私たちについて", purpose: "方針と信頼材料を伝える" },
  { file: "case.html", name: "事例・利用シーン", purpose: "利用イメージを伝える（公開前に実例へ差し替え）" },
  { file: "contact.html", name: "お問い合わせ", purpose: "不安を減らして問い合わせへつなげる" },
  { file: "privacy.html", name: "プライバシー", purpose: "個人情報の取り扱い方針を示す（法務確認が必要）" }
];

const imageUses = [
  ["ホーム ヒーロー", "第一印象とブランドの世界観を伝える", "1920x1080", "ブランドの価値が伝わる象徴的なメインビジュアル"],
  ["サービス概要", "主な提供内容を直感的に示す", "1600x1200", "主なサービスの利用場面を表すイメージ"],
  ["特徴", "選ばれる理由を視覚的に補強する", "1600x1200", "サービスの特徴を具体的に示すイメージ"],
  ["詳細説明", "品質や工程の細部を伝える", "1600x1200", "丁寧な仕事や品質を表すディテール"],
  ["利用シーン1", "顧客の利用イメージを作る", "1600x1067", "サービスを利用する自然な場面"],
  ["利用シーン2", "別のニーズや時間帯を示す", "1600x1067", "異なる利用場面を表すイメージ"],
  ["顧客像", "想定顧客が自分ごと化できるようにする", "1400x1400", "想定する顧客像を表す自然な人物イメージ"],
  ["スタッフ・姿勢", "人柄と信頼感を補う", "1400x1400", "誠実な対応姿勢を表すスタッフのイメージ"],
  ["外観・空間", "訪問や利用前の不安を減らす", "1600x1200", "ブランドの雰囲気を表す外観または空間"],
  ["CTA", "最終行動を後押しする", "1920x800", "問い合わせや予約への前向きな気持ちを表すイメージ"]
];

const promptSubjects = [
  "an editorial hero scene expressing the brand promise",
  "an authentic service experience with carefully arranged details",
  "a refined visual metaphor for quality and reliability",
  "a close-up of thoughtful craftsmanship and premium materials",
  "a natural everyday customer experience in a welcoming setting",
  "a complementary customer scenario at a different time of day",
  "a candid and inclusive customer portrait in a realistic setting",
  "an approachable professional team moment with natural expressions",
  "a welcoming exterior or interior environment with clear spatial depth",
  "an uplifting wide scene that creates a calm sense of readiness to act"
];

const prompts = IMAGE_FILENAMES.map((filename, index) => {
  const [usage, imagePurpose, recommendedSize, alt] = imageUses[index];
  return {
    id: index + 1,
    filename,
    usage,
    purpose: imagePurpose,
    prompt: `${promptSubjects[index]}, for ${projectName}, ${mood}, premium editorial commercial photography, authentic details, natural lighting, realistic proportions, accessible negative space for web layout, no text, no letters, no logos, no watermark, no recognizable brands`,
    alt,
    recommended_size: recommendedSize
  };
});

await fs.mkdir(path.join(outputDir, "assets", "images"), { recursive: true });
await fs.mkdir(path.join(outputDir, "implementation-starter", "assets", "css"), { recursive: true });
await fs.mkdir(path.join(outputDir, "implementation-starter", "assets", "js"), { recursive: true });
await fs.mkdir(path.join(outputDir, "implementation-starter", "assets", "images"), { recursive: true });

const write = async (relative, content) => {
  const target = path.join(outputDir, relative);
  await fs.mkdir(path.dirname(target), { recursive: true });
  await fs.writeFile(target, content.endsWith("\n") ? content : `${content}\n`, "utf8");
};

await write("README.md", `# ${projectName} Webサイト制作成果物

このディレクトリには、Webサイト設計、コピー・SEO、画像設計、実装スターター、品質確認資料が含まれます。

## プロジェクト

- 目的: ${purpose}
- 対象: ${audience}
- 主なCV: ${conversion}
- 実装前提: ${implementation}

## 画像について

この自動生成では画像ファイル本体を作成していません。画像生成に必要なプロンプト10件を「10_image-prompts.md」「assets/prompts.json」「assets/image-index.csv」に収録しています。生成画像は実在の店舗、商品、スタッフ、実績を示すものとして無断使用せず、必要に応じて「イメージ」と明記してください。

## 公開前に必要な作業

- [仮設定] と [要確認] を検索し、事業者が実データへ差し替える
- 料金、資格、実績、連絡先、所在地、営業時間、規約を確認する
- フォーム送信先、解析、Cookie同意、外部サービス連携を決定する
- 対象業種・地域の法令、広告ガイドライン、アクセシビリティを確認する
`);

await write("00_project-summary.md", `# プロジェクト概要

## 事業

${business}

## サイト方針

- 事業名: ${projectName}
- 目的: ${purpose}
- 対象: ${audience}
- 主なCV: ${conversion}
- 雰囲気: ${mood}
- 写真素材: ${assets}
- 実装: ${implementation}

## 情報の確度

入力にない情報は [仮設定] として扱う。料金、所在地、営業時間、資格、実績、レビュー、法的表示は [要確認] とし、公開前に事業者が確認する。
`);

await write("01_requirements.md", `# 要件定義

## 目標とユーザー

- 事業目標: ${purpose}
- 主なユーザー: ${audience}
- 主CV: ${conversion}
- 成功指標候補: [仮設定] 主CTA到達率、問い合わせ開始率、問い合わせ完了率

## ページ要件

| ページ | 目的 | 必須内容 |
|---|---|---|
${pages.map((page) => `| ${page.name} | ${page.purpose} | 概要、信頼材料、次の行動 |`).join("\n")}

## 機能要件

- レスポンシブナビゲーション
- CTA導線、電話・予約・問い合わせリンク
- FAQの開閉（HTMLのdetailsを優先）
- 問い合わせフォームUI（送信先は未接続）
- フォーカス表示とキーボード操作
- reduced motion対応

## 非機能・制約

- モバイルファースト、WCAG 2.2 AAを目標とする
- 個人情報の外部送信、解析、Cookieは明示的な設定まで無効
- 主要コンテンツはJavaScriptなしでも利用可能
- [要確認] 業界固有の広告・表示義務、プライバシー、Cookie同意
`);

await write("02_website-blueprint.md", `# Webサイト設計書

## コンセプト

${mood}を基調に、ユーザーが「自分に合うか」「信頼できるか」「次に何をすべきか」を短時間で判断できる設計とする。

## サイトマップ

| URL | ページ | 目的 | 主CTA |
|---|---|---|---|
${pages.map((page) => `| /${page.file === "index.html" ? "" : page.file} | ${page.name} | ${page.purpose} | ${conversion} |`).join("\n")}

## ホームのセクション

1. ヒーロー: 価値提案、対象、主CTA
2. 課題への共感: ユーザーの状況を具体化
3. サービス概要: 選択肢と適合条件
4. 選ばれる理由: 確認可能な根拠のみ
5. 利用の流れ: 行動後の見通し
6. FAQ: 不安・条件・準備事項
7. 最終CTA: 主CVと代替導線

## ページ間導線

各詳細ページはホーム、関連詳細、問い合わせへ相互リンクする。プライバシーはフォーム近傍とフッターから到達可能にする。
`);

await write("03_copywriting.md", `# コピーライティング案

## ブランドボイス

- 語調: ${mood}
- 方針: 具体的で誠実。ユーザーの判断材料を先に示す。
- 避ける表現: 根拠のないNo.1、絶対、必ず、効果保証、架空の限定性・口コミ・実績

## メインコピー

- H1案: ${projectName}で、納得できる次の一歩を。
- サブコピー案: ${audience}に向けて、必要な情報と選びやすい導線を丁寧に届けます。
- 主CTA案: 詳しく相談する
- 副CTA案: サービスを見る

## ページ別H1

${pages.map((page) => `- ${page.name}: ${page.name === "ホーム" ? `${projectName}で、納得できる次の一歩を。` : `${page.name}｜${projectName}`}`).join("\n")}

## FAQ案

回答内の料金、所要時間、対応範囲、予約条件は [要確認] とし、運用確定後に公開する。
`);

await write("04_seo-plan.md", `# SEO設計

## 方針

事業名・サービス種別・地域・利用目的を軸に、ページごとに異なる検索意図へ対応する。検索順位や成果は保証しない。

| ページ | title案 | 検索意図 | 構造化データ候補 |
|---|---|---|---|
${pages.map((page) => `| ${page.name} | ${page.name}｜${projectName} | ${page.purpose} | ${page.name === "ホーム" ? "Organization / LocalBusiness（該当時）" : "WebPage"} |`).join("\n")}

## 実装要件

- ページ固有のtitle、description、H1を設定
- canonical、OGP、XML sitemap、robots.txtは公開URL確定後に設定
- 内部リンクは説明的な文言にし、リンク目的を明確にする
- 構造化データは画面上の確認済み情報と一致させる
- 画像に寸法、適切なalt、遅延読み込みを設定する（LCP画像を除く）
`);

await write("05_ui-ux-design.md", `# UI/UX設計

## 原則

- モバイルで主CTAと連絡手段を見つけやすくする
- 見出し、余白、色、サイズで階層を作り、装飾だけに依存しない
- ボタンとリンクは役割を視覚・文言の両方で区別する
- エラーは色だけでなく文言で説明する

## 共通UI

- ヘッダー: ロゴ相当テキスト、グローバルナビ、主CTA
- モバイルナビ: aria-expandedを同期し、Escで閉じ、背景スクロールを妨げない
- フォーム: 永続ラベル、必須表示、入力例、エラー要約、完了状態
- フッター: 主要ページ、連絡導線、プライバシー

## アクセシビリティ

WCAG 2.2 AAを目標とし、skip link、ランドマーク、自然な見出し順、キーボード操作、明確なフォーカス、十分なコントラスト、reduced motionを実装する。
`);

await write("06_animation-js-spec.md", `# JavaScript・アニメーション仕様

## 機能

- モバイルナビの開閉とaria-expanded同期
- サンプルフォームのクライアント側検証（外部送信なし）
- ページ内リンクの補助。主要導線は通常リンクのままにする

## 原則

- JavaScriptなしでも情報と主要リンクを利用できる
- prefers-reduced-motion: reduceでは非必須アニメーションを停止する
- スクロール監視や自動再生を必須機能にしない
- 外部解析、Cookie、個人情報送信は未接続
`);

await write("07_css-design.md", `# CSS設計

## デザイントークン

- 色: 背景、前景、ブランド、補助、境界、エラーをカスタムプロパティ化
- 文字: システムフォントを基本にし、可読幅を約68文字へ制限
- 余白: 4px基準の流動的スケール
- 角丸・影: 階層表現に必要な最小限

## レイアウト

- 320pxからモバイルファースト
- clamp()とGrid/Flexboxを使い、固定幅に依存しない
- 画像には幅・高さまたはaspect-ratioを設定し、レイアウトシフトを抑える
- :focus-visibleを明確にし、prefers-reduced-motionを尊重する
`);

await write("08_responsive-design.md", `# レスポンシブ設計

## 基準幅

- 320〜767px: 1カラム、ナビ折りたたみ、CTAを明確化
- 768〜1023px: コンテンツに応じて2カラム
- 1024px以上: 最大幅を設け、余白と読みやすさを優先

## 確認端末・状態

- 320、375、390、768、1024、1440px
- 200%ズーム、長い日本語、英数字連続、画像未読込、エラー表示
- 縦横切替、タッチ、キーボード、reduced motion
`);

await write("09_visual-assets-plan.md", `# ビジュアルアセット計画

## 方針

- 雰囲気: ${mood}
- 生成画像を実績、実在店舗、実在商品、実在スタッフとして誤認させない
- テキストやロゴは画像へ焼き込まずHTMLで提供する

| ID | ファイル名 | 用途 | 目的 | 推奨サイズ | alt |
|---:|---|---|---|---|---|
${prompts.map((item) => `| ${item.id} | ${item.filename} | ${item.usage} | ${item.purpose} | ${item.recommended_size} | ${item.alt} |`).join("\n")}
`);

await write("10_image-prompts.md", `# 画像生成プロンプト10件

${prompts.map((item) => `## ${item.id}. ${item.usage}\n\n- ファイル名: \`${item.filename}\`\n- 目的: ${item.purpose}\n- 推奨サイズ: ${item.recommended_size}\n- alt: ${item.alt}\n- Prompt: ${item.prompt}`).join("\n\n")}
`);

await write("11_implementation-instructions.md", `# 実装指示

## 技術と範囲

- ${implementation}
- ${pages.length}ページの静的スターター
- 外部ライブラリ、解析、フォーム送信先は未接続

## 実装原則

- セマンティックHTMLと自然な見出し階層
- モバイルファーストCSS、キーボード操作、reduced motion
- JavaScriptは段階的機能向上。DOM挿入に未信頼HTMLを使わない
- フォームは接続先決定後にCSRF対策、サーバー側検証、スパム対策、保持期間を実装
- 実データ、法的表示、連絡先、画像は公開前に差し替える
`);

await write("12_quality-checklist.md", `# 品質チェックリスト

## 事実・内容

- [ ] [仮設定] と [要確認] を事業者が確認した
- [ ] 価格、資格、実績、レビュー、所在地、営業時間に根拠がある
- [ ] 生成画像を実績写真として誤認させていない

## 表示・機能

- [ ] 320〜1440pxと200%ズームで確認した
- [ ] JavaScriptなしでも主要情報へ到達できる
- [ ] フォーム送信・完了・エラー状態を実環境で確認した

## アクセシビリティ・SEO・性能

- [ ] キーボード、フォーカス、見出し、ラベル、コントラスト、altを確認した
- [ ] title、description、canonical、OGP、構造化データを実URL・実データへ更新した
- [ ] 画像サイズ、圧縮、LCP、CLS、不要スクリプトを確認した

## 法務・プライバシー

- [ ] 個人情報、Cookie、解析、外部埋め込み、業界規制を確認した
- [ ] 公開前に必要な専門家レビューを完了した
`);

await write("assets/prompts.json", `${JSON.stringify(prompts, null, 2)}\n`);
const csvRows = [
  ["id", "filename", "usage", "purpose", "recommended_size", "alt"],
  ...prompts.map((item) => [item.id, item.filename, item.usage, item.purpose, item.recommended_size, item.alt])
];
await write("assets/image-index.csv", csvRows.map((row) => row.map(csvEscape).join(",")).join("\n"));
await write("assets/images/README.md", `# Images

この生成処理では画像生成機能を使用していないため、画像ファイル本体は含まれていません。

次の10件のプロンプトと対応表を画像生成ツールで使用してください。

- ../prompts.json
- ../image-index.csv
- ../../10_image-prompts.md

生成後はファイル名を対応表に合わせ、WebPへ最適化し、内容とaltを人が確認してください。生成画像を実在の店舗、商品、スタッフ、顧客、施工・導入実績として誤認させないでください。
`);

const mainHeadline = `${projectName}で、納得できる次の一歩を。`;
for (const page of pages) {
  const isHome = page.file === "index.html";
  const isContact = page.file === "contact.html";
  const nav = pages
    .map((item) => {
      const current = item.file === page.file ? ' aria-current="page"' : "";
      return `<a href="${item.file}"${current}>${htmlEscape(item.name)}</a>`;
    })
    .join("\n          ");
  const heading = isHome ? mainHeadline : page.name;
  const body = isContact
    ? `<section class="hero"><div class="container"><p class="eyebrow">${htmlEscape(projectName)}</p><h1>${htmlEscape(page.name)}</h1><p>${htmlEscape(page.purpose)}</p></div></section><section class="section"><div class="container prose"><h2>お問い合わせ内容</h2><p>このフォームはUIサンプルで、外部へ送信されません。実装時に送信先、プライバシー表示、サーバー側検証を設定してください。</p><form data-demo-form novalidate><label for="name">お名前</label><input id="name" name="name" autocomplete="name" required><label for="email">メールアドレス</label><input id="email" name="email" type="email" autocomplete="email" required><label for="message">お問い合わせ内容</label><textarea id="message" name="message" rows="6" required></textarea><p class="form-status" role="status" aria-live="polite"></p><button class="button" type="submit">内容を確認する</button></form></div></section>`
    : `<section class="hero"><div class="container"><p class="eyebrow">${htmlEscape(projectName)}</p><h1>${htmlEscape(heading)}</h1><p>${htmlEscape(page.purpose)}</p><a class="button" href="contact.html">${htmlEscape(conversion)}</a></div></section><section class="section"><div class="container grid"><article class="card"><h2>価値と特徴</h2><p>${htmlEscape(business)}</p></article><article class="card"><h2>ご利用の方へ</h2><p>対象: ${htmlEscape(audience)}</p></article><article class="card"><h2>次のステップ</h2><p>詳細条件は公開前に事業者へ確認してください。</p></article></div></section>`;
  const title = isHome ? `${projectName}｜${page.name}` : `${page.name}｜${projectName}`;
  await write(`implementation-starter/${page.file}`, `<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="${htmlEscape(page.purpose)}">
  <title>${htmlEscape(title)}</title>
  <link rel="stylesheet" href="assets/css/style.css">
  <script src="assets/js/main.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#main">本文へ移動</a>
  <header class="site-header">
    <div class="container header-inner"><a class="brand" href="index.html">${htmlEscape(projectName)}</a><button class="menu-button" type="button" aria-expanded="false" aria-controls="global-nav">メニュー</button><nav id="global-nav" aria-label="メインナビゲーション">${nav}</nav></div>
  </header>
  <main id="main">${body}</main>
  <footer class="site-footer"><div class="container"><p>© ${new Date().getFullYear()} ${htmlEscape(projectName)}</p><p><a href="privacy.html">プライバシー</a></p></div></footer>
</body>
</html>`);
}

await write("implementation-starter/assets/css/style.css", `:root {
  --bg: #f7f5f0; --surface: #fff; --text: #20231f; --muted: #62675f;
  --brand: #315c4c; --brand-contrast: #fff; --line: #d8ddd6;
  --radius: 1rem; --shadow: 0 1rem 2.5rem rgb(21 36 29 / .08);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--bg); color: var(--text); font-family: system-ui, -apple-system, "Segoe UI", sans-serif; line-height: 1.7; }
a { color: inherit; text-underline-offset: .2em; }
button, input, textarea { font: inherit; }
.container { width: min(100% - 2rem, 70rem); margin-inline: auto; }
.skip-link { position: fixed; inset: .5rem auto auto .5rem; z-index: 10; padding: .7rem 1rem; background: #fff; transform: translateY(-160%); }
.skip-link:focus { transform: none; }
.site-header { position: sticky; top: 0; z-index: 5; background: rgb(247 245 240 / .95); border-bottom: 1px solid var(--line); }
.header-inner { min-height: 4rem; display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
.brand { font-weight: 750; text-decoration: none; }
.menu-button { padding: .55rem .8rem; border: 1px solid var(--line); border-radius: .5rem; background: var(--surface); }
nav { display: none; position: absolute; inset: 4rem 1rem auto; padding: 1rem; background: var(--surface); box-shadow: var(--shadow); }
nav[data-open="true"] { display: grid; gap: .75rem; }
nav a { padding: .35rem; }
.hero { padding: clamp(4rem, 12vw, 8rem) 0; background: linear-gradient(135deg, #e0eadf, #f7f5f0 60%); }
.hero h1 { max-width: 16ch; margin: 0; font-size: clamp(2.2rem, 9vw, 5rem); line-height: 1.1; }
.eyebrow { color: var(--brand); font-weight: 700; letter-spacing: .08em; }
.button { display: inline-block; margin-top: 1rem; padding: .8rem 1.15rem; border: 2px solid var(--brand); border-radius: 999px; background: var(--brand); color: var(--brand-contrast); font-weight: 700; text-decoration: none; }
.section { padding: clamp(3rem, 8vw, 6rem) 0; }
.grid { display: grid; gap: 1rem; }
.card { padding: clamp(1.25rem, 4vw, 2rem); border: 1px solid var(--line); border-radius: var(--radius); background: var(--surface); }
.prose { max-width: 46rem; }
form { display: grid; gap: .65rem; }
input, textarea { width: 100%; padding: .8rem; border: 1px solid #737a71; border-radius: .4rem; background: #fff; }
.form-status { min-height: 1.7em; color: var(--brand); font-weight: 650; }
.site-footer { padding: 2rem 0; border-top: 1px solid var(--line); color: var(--muted); }
:focus-visible { outline: 3px solid #cf7b17; outline-offset: 3px; }
@media (min-width: 48rem) {
  .menu-button { display: none; }
  nav, nav[data-open="true"] { position: static; display: flex; padding: 0; background: transparent; box-shadow: none; gap: 1rem; }
  .grid { grid-template-columns: repeat(3, 1fr); }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; }
}`);

await write("implementation-starter/assets/js/main.js", `// 段階的機能向上: このファイルが読み込まれなくても、全ページの情報と主要リンクは利用できる。
const menuButton = document.querySelector(".menu-button");
const navigation = document.querySelector("#global-nav");

if (menuButton && navigation) {
  const setOpen = (open) => {
    menuButton.setAttribute("aria-expanded", String(open));
    navigation.dataset.open = String(open);
  };
  const isOpen = () => menuButton.getAttribute("aria-expanded") === "true";

  menuButton.addEventListener("click", () => setOpen(!isOpen()));

  // Escapeはメニューが開いているときだけ処理し、フォーム入力中などのフォーカスを奪わない。
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && isOpen()) {
      setOpen(false);
      menuButton.focus();
    }
  });

  // メニュー外をクリックしたら閉じる。
  document.addEventListener("click", (event) => {
    if (isOpen() && !navigation.contains(event.target) && !menuButton.contains(event.target)) {
      setOpen(false);
    }
  });
}

const demoForm = document.querySelector("[data-demo-form]");
if (demoForm) {
  demoForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const status = demoForm.querySelector(".form-status");
    if (!demoForm.checkValidity()) {
      demoForm.reportValidity();
      status.textContent = "未入力または形式が正しくない項目があります。";
      return;
    }
    status.textContent = "入力例を確認しました。このサンプルは外部へ送信しません。";
  });
}`);

await write("implementation-starter/README.md", `# Implementation starter

${projectName}向けの静的HTML/CSS/JavaScriptスターターです。

## 含まれるページ

${pages.map((page) => `- \`${page.file}\`: ${page.name}`).join("\n")}

## 未接続・要差し替え

- 画像ファイルと実際のalt
- 連絡先、所在地、営業時間、料金、資格、実績
- 問い合わせフォームの安全なサーバー側送信処理
- プライバシーポリシー、Cookie同意、解析、構造化データ、canonical、OGP

フォームはデモであり、入力内容を外部送信・保存しません。実装時はサーバー側検証、CSRF・スパム対策、通信暗号化、保持期間、同意文言を設計してください。
`);

console.log(JSON.stringify({
  generated: true,
  project: projectSlug,
  outputDir,
  promptCount: prompts.length,
  htmlPageCount: pages.length,
  imageMode: "prompts-only"
}, null, 2));
