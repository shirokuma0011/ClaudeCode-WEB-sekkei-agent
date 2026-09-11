# Claude Code Web設計エージェント群

短い事業説明から、Webサイトの要件定義、設計、コピー・SEO、UI/UX、画像プロンプト10件、実装スターター、品質チェックリスト、納品ZIPまでを一貫して作るためのClaude Code向けリポジトリです。

[Codex-WEB-sekkei-agent](https://github.com/shirokuma0011/Codex-WEB-sekkei-agent) を移植し、Claude Codeのサブエージェント、スキル、権限設定に合わせて再構成しました。

## Claude Code版の特徴

- `CLAUDE.md` がマスターエージェントの指示を持ち、`docs/guidelines/common-rules.md` を `@import` で常時読み込む
- 6つの専門工程を `.claude/agents/` の**サブエージェント**として定義。各工程は独立したコンテキストで動き、`output/<slug>/` のファイルだけを引き継ぎ元にする
- `/web-sekkei <input.md> <slug>` **スキル**で、雛形生成から6工程の順次実行、検証、ZIP化、最終報告までを一発で起動
- `.claude/settings.json` で `npm run generate/validate/zip` と `output/` 配下の編集を事前許可し、`.env` や鍵ファイルの読み取りを拒否
- `npm test` でスモークテストに加え、CLAUDE.md・サブエージェント・スキル・設定ファイルの整合性を検査
- 事実・ユーザー提供情報・仮設定を分離し、未確認情報の断定を防止
- 医療・法務・金融などで資格、効果、価格、実績を捏造しない安全基準
- モバイルファースト、WCAG 2.2 AAを目標とするアクセシビリティ設計
- project slugの検証、出力先固定、ZIP自己包含防止、厳格な成果物検証
- 静的HTML/CSS/JavaScriptの実装スターターを自動生成（現在ページの `aria-current`、Escapeキーとメニュー外クリックでの閉じる動作を含む）

## 必要環境

- Node.js 20以上
- npm
- Claude Code（CLI、デスクトップアプリ、または claude.ai/code）

外部ランタイム依存はありません。Node.js標準機能だけで動作します。

## 使い方

### Claude Codeで一式を生成する

1. `examples/restaurant-input.md` または `examples/clinic-input.md` をコピーして事業情報を編集します。
2. リポジトリのルートでClaude Codeを起動し、次のように依頼します。

```text
/web-sekkei examples/restaurant-input.md forest-restaurant
```

自然言語で「examples/restaurant-input.md からWebサイト一式を作って」と依頼しても、`CLAUDE.md` の指示により同じ手順が適用されます。

Claude Codeは次の順で動きます。

1. `npm run generate` で検証に合格する雛形を作る
2. `sekkei-requirements` → `sekkei-blueprint` → `sekkei-copy-seo` → `sekkei-visual` → `sekkei-implementation-qa` → `sekkei-packager` の順にサブエージェントを起動し、雛形を事業固有の内容へ書き換える
3. `npm run validate` と `npm run zip` を実行し、ZIPのパス、画像モード、仮設定・要確認事項を報告する

成果物は `output/<project-slug>/`、ZIPは `output/<project-slug>/<project-slug>-website-package.zip` に生成されます。

### スクリプトだけで雛形を作る

```bash
npm run generate -- examples/restaurant-input.md forest-restaurant
npm run validate -- forest-restaurant
npm run zip -- forest-restaurant
```

`generate` は安全で一貫した初期成果物を作る決定論的な補助機能です。既存の出力があると失敗し、`--force` を付けた場合だけ置き換えます。

### 入力ファイルの形式

`【見出し】` で始まる行をセクションとして読み取ります。見出しと同じ行に値を書いても、次の行から書いても構いません。未記入のセクションは `[仮設定]` として補われます。

## 画像モード

- Claude Code自体は画像を生成しません。標準は「プロンプトのみモード」で、`10_image-prompts.md`、`assets/prompts.json`、`assets/image-index.csv`、`assets/images/README.md` を納品します。
- 外部の画像生成ツールで作成した10枚を `assets/images/` に指定ファイル名で配置すると、`validate` が「画像ありモード」として検証します。
- `scripts/image-provider.example.mjs` は、独自の画像生成アダプターを書く際の雛形です。

実在人物、商標、資格、受賞歴、価格、所在地、顧客の声などは、確認できない限り生成画像やコピーで事実として表現しません。

## テスト

```bash
npm test
```

スモークテストは一時ディレクトリにプロジェクトを生成し、検証とZIP作成を確認してから削除します。続けて `tests/check-claude-config.mjs` が、`CLAUDE.md`、`.claude/settings.json`、`.claude/agents/`、`.claude/skills/` の形式と相互参照を検査します。

## 構成

```text
CLAUDE.md                  マスターエージェント指示（Claude Codeが自動で読み込む）
.claude/settings.json      許可・拒否する操作
.claude/agents/            6つの専門サブエージェント
.claude/skills/web-sekkei/ パイプライン起動スキル
docs/guidelines/           全工程共通ルール
docs/workflow.md           パイプラインの人間向け説明
docs/templates/            成果物テンプレート
docs/industry-presets/     業種別の設計補助
scripts/                   生成・検証・ZIP化
tests/                     スモークテストと設定検査
examples/                  入力例
output/                    生成先（成果物はGit管理対象外）
```

## カスタマイズ

- 工程ごとのモデルや使用ツールは `.claude/agents/*.md` の frontmatter で変更できます。
- 業種を追加する場合は `docs/industry-presets/` にファイルを足します。工程1と3が参照します。
- 必須ファイルや画像ファイル名は `scripts/lib.mjs` の `REQUIRED_FILES` と `IMAGE_FILENAMES` が正です。変更したら `.claude/agents/` と `docs/` も合わせて更新し、`npm test` を通してください。

## 注意

生成物は公開前に事業者が確認してください。法令、広告ガイドライン、表示義務、個人情報保護、Cookie同意、アクセシビリティ要件は、対象地域・業種・運用方法に応じて専門家による確認が必要になる場合があります。
