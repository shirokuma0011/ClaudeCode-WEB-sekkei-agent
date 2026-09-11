---
name: web-sekkei
description: 事業概要の入力ファイルから、要件定義・設計・コピー/SEO・画像プロンプト10件・実装スターター・品質チェックリスト・納品ZIPまでを6工程のサブエージェントで一貫生成する。「Webサイト一式を作って」「設計書とZIPを作って」という依頼で使う。
arguments: [input, slug]
argument-hint: "<input.md> <project-slug> [--force]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# Webサイト制作パイプライン

入力ファイル `$input` から、`output/$slug/` に納品一式を生成する。引数が渡されていない場合は、入力ファイルのパスと `project-slug`（英小文字・数字・ハイフン、1〜64文字）をユーザーに確認してから始める。

全工程で `docs/guidelines/common-rules.md` の共通ルールを適用する。

## 0. 準備

1. `$input` が存在し、`【事業内容】` などの見出しを含むことを確認する。
2. `output/$slug/` が既に存在して中身がある場合は、その内容を確認する。上書きしてよいとユーザーが明示した場合のみ `--force` を付ける。それ以外は別のslugを提案して止まる。
3. 雛形を生成する。

```bash
npm run generate -- $input $slug
```

出力されるJSONの `outputDir` を、以降のサブエージェントに渡す絶対パスとして使う。

## 1〜6. サブエージェントを順番に起動

`Agent` ツールで次のサブエージェントを**この順番で、1つずつ**起動する。並列にしない。各起動時のプロンプトには必ず次を含める。

- `project-slug`: `$slug`
- 出力ディレクトリの絶対パス
- 入力ファイルの絶対パス
- 直前の工程の報告（主CV、ページ一覧、修正した上流成果物など）

| 工程 | subagent_type | 完了の確認 |
|---|---|---|
| 1 | `sekkei-requirements` | `00`, `01` が事業固有の内容で埋まっている |
| 2 | `sekkei-blueprint` | `02`, `05`, `08` にサイトマップと共通UIがある |
| 3 | `sekkei-copy-seo` | `03`, `04` にページ別コピーとメタ情報がある |
| 4 | `sekkei-visual` | `09`, `10`, `assets/` の3ファイルが10件で一致 |
| 5 | `sekkei-implementation-qa` | `06`, `07`, `11`, `12` と `implementation-starter/` が設計と一致 |
| 6 | `sekkei-packager` | validate が終了コード0、ZIPが存在 |

各工程の報告を読み、完了条件を満たしていない場合は同じサブエージェントに不足を伝えて再実行する。次工程へ不足を持ち越さない。

## 7. 最終確認

```bash
npm run validate -- $slug --require-zip
```

終了コード0を確認してから最終報告を書く。

## 最終報告の形式

- ZIPのパス
- 画像モード（Claude Codeには画像生成機能がないため、ユーザーが画像を用意していない限り `prompts-only`）
- 画像プロンプト数、HTMLページ数
- `[仮設定]` と `[要確認]` の主な項目
- 上流成果物を修正した工程とその内容
- 公開前にユーザーが行う作業（実データ差し替え、法務確認、フォーム送信先の設定など）

画像本体を生成していないのに生成したと表現しない。検証に失敗した状態でZIPが存在すると報告しない。
