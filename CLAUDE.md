# 全業種対応 Webサイト制作マスターエージェント

このリポジトリで作業するClaude Codeは、ユーザーの事業概要から納品可能なWebサイト設計一式を作るマスターエージェントとして振る舞う。

## 目的

`output/<project-slug>/` に、要件定義から実装スターターまでを生成し、検証に合格した成果物だけをZIP化する。

## 共通ルール

事実・仮設定・要確認事項の分離、捏造禁止、出力先の制限、画像の扱いは次のファイルで定義している。マスターエージェントとすべてのサブエージェントに適用される。

@docs/guidelines/common-rules.md

## 起動方法

- ユーザーが `/web-sekkei <input.md> <project-slug>` を実行した場合は、`.claude/skills/web-sekkei/SKILL.md` の手順に従う。
- 「このファイルからWebサイト一式を作って」のような自然言語依頼でも、同じ手順を適用する。入力ファイルがない場合は `examples/restaurant-input.md` の形式で事業情報を確認し、`examples/` には書かずスクラッチ用に `output/<project-slug>/input.md` として保存する。

## 実行順序

雛形生成のあと、次の6つのサブエージェント（`.claude/agents/`）を順番に起動し、各工程の完了条件を満たしてから次へ進む。

| 工程 | サブエージェント | 主な成果物 |
|---|---|---|
| 1 | `sekkei-requirements` | `00_project-summary.md`, `01_requirements.md` |
| 2 | `sekkei-blueprint` | `02_website-blueprint.md`, `05_ui-ux-design.md`, `08_responsive-design.md` |
| 3 | `sekkei-copy-seo` | `03_copywriting.md`, `04_seo-plan.md` |
| 4 | `sekkei-visual` | `09_visual-assets-plan.md`, `10_image-prompts.md`, `assets/` |
| 5 | `sekkei-implementation-qa` | `06_animation-js-spec.md`, `07_css-design.md`, `11_implementation-instructions.md`, `12_quality-checklist.md`, `implementation-starter/` |
| 6 | `sekkei-packager` | `<project-slug>-website-package.zip` |

- 各サブエージェントには、`project-slug`、出力ディレクトリの絶対パス、入力ファイルのパス、直前工程の報告内容を渡す。
- 前工程の成果物を次工程の唯一の引き継ぎ元とし、矛盾を見つけた場合は上流成果物を修正して整合させる。
- サブエージェントが完了条件を満たせなかったと報告した場合は、不足を補ってから次へ進む。次工程へ「あとで直す」を持ち越さない。

## 必須成果物

- `README.md`
- `00_project-summary.md` から `12_quality-checklist.md` までの13ファイル
- `assets/prompts.json`
- `assets/image-index.csv`
- `assets/images/` 配下の画像10枚、または `assets/images/README.md`
- 5ページ以上を含む `implementation-starter/`
- `<project-slug>-website-package.zip`

ファイル名・列名・画像ファイル名は `scripts/lib.mjs` の `REQUIRED_FILES` と `IMAGE_FILENAMES` が正である。検証はこれらに対して行われる。

## コマンド

```bash
npm run generate -- <input-file> <project-slug>   # 決定論的な雛形を生成（既存があれば失敗。上書きは --force）
npm run validate -- <project-slug>                # 必須ファイル・画像情報・HTMLページ数を検証
npm run zip -- <project-slug>                     # 検証合格時のみZIP化し、再検証
npm test                                          # スモークテストと設定ファイルの検査
```

検証が失敗した場合はZIP化せず、エラーを修正して再検証する。`.claude/settings.json` でこれらのコマンドは許可済みなので、確認なしで実行してよい。

## ファイル操作の作法

- 成果物の作成・修正には `Write` / `Edit` ツールを使い、`output/<project-slug>/` の外を変更しない。
- リポジトリ本体（`docs/`、`scripts/`、`.claude/`）の変更は、ユーザーがこのリポジトリ自体の改善を依頼した場合に限る。
- `.env`、鍵ファイル、認証情報を読まない。成果物やログにも書かない。
- 既存の `output/<project-slug>/` を消す前に中身を確認し、ユーザーの無関係な変更を消さない。

## 最終報告

最終回答では次を簡潔に報告する。

- ZIPのパス
- 画像モード（`prompts-only` または `generated-images`）
- 画像プロンプト数、HTMLページ数
- `[仮設定]` と `[要確認]` の主な項目
- 上流成果物を修正した場合はその内容

Claude Codeには画像生成機能がないため、ユーザーが画像を用意していない限り「画像本体を生成した」と表現してはならない。

## このリポジトリ自体の開発

- Node.js 20以上、外部依存なし。ESM（`.mjs`）で書く。
- `scripts/lib.mjs` の定数を変えたら `docs/`、`.claude/agents/`、`tests/` の該当箇所も更新する。
- 変更後は `npm test` を通す。
