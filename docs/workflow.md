# パイプライン概要（人間向け）

このリポジトリは、Claude Codeのサブエージェント機能を使って、事業概要からWebサイト設計一式を6工程で生成する。各工程の詳細な指示は `.claude/agents/` にあり、Claude Codeはそれをサブエージェントのシステムプロンプトとして読み込む。

## 工程と成果物

```text
入力: examples/*.md 形式の事業概要
  │
  ├─ 0. npm run generate      決定論的な雛形（全必須ファイルの初期版）
  │
  ├─ 1. sekkei-requirements   00_project-summary.md, 01_requirements.md
  ├─ 2. sekkei-blueprint      02_website-blueprint.md, 05_ui-ux-design.md, 08_responsive-design.md
  ├─ 3. sekkei-copy-seo       03_copywriting.md, 04_seo-plan.md
  ├─ 4. sekkei-visual         09_visual-assets-plan.md, 10_image-prompts.md, assets/{prompts.json,image-index.csv,images/}
  ├─ 5. sekkei-implementation-qa
  │                           06_animation-js-spec.md, 07_css-design.md, 11_implementation-instructions.md,
  │                           12_quality-checklist.md, implementation-starter/
  └─ 6. sekkei-packager       npm run validate → npm run zip → <slug>-website-package.zip
```

## 引き継ぎの契約

- 各工程は `output/<project-slug>/` 内のファイルだけを引き継ぎ元とする。会話履歴に依存しない。
- 下流で矛盾を見つけた場合は上流ファイルを修正し、報告に含める。
- 各工程の「完了条件」を満たさない限り次へ進まない。マスターエージェント（`CLAUDE.md`）が報告を読み、不足があれば同じ工程を再実行する。

## なぜ雛形を先に作るのか

`npm run generate` は、検証に合格する最小構成を決定論的に作る。これにより、

- サブエージェントは「空から書く」のではなく「雛形を事業固有の内容へ書き換える」作業に集中できる。
- どの工程で失敗しても、`npm run validate` が不足ファイルや不整合を機械的に指摘できる。
- ファイル名、JSONキー、CSV列名などの契約が `scripts/lib.mjs` に一元化される。

## 画像モード

| モード | 条件 | 納品物 |
|---|---|---|
| `prompts-only`（標準） | `assets/images/` に画像がない | `10_image-prompts.md`, `assets/prompts.json`, `assets/image-index.csv`, `assets/images/README.md` |
| `generated-images` | `IMAGE_FILENAMES` の10枚がすべて存在 | 上記に加え画像10枚 |

Claude Code自体は画像を生成しない。画像が必要な場合は、`assets/prompts.json` を外部の画像生成ツールに渡し、生成結果を指定ファイル名で配置してから再度 `npm run validate` を実行する。`scripts/image-provider.example.mjs` は、独自の画像生成アダプターを書く際の雛形である。

## Claude Codeでの拡張ポイント

- `.claude/agents/*.md` の `model` を工程ごとに変えられる（例: 機械的な工程6を軽量モデルに）。
- `.claude/settings.json` の `permissions` に、プロジェクトで許可するコマンドを追加できる。
- `.claude/skills/web-sekkei/SKILL.md` を複製して、特定業種向けの固定フローを作れる。
- `docs/industry-presets/` に業種を追加すると、工程1と3が参照する。
