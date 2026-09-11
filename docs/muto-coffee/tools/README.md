# tools/

## capture_site.py

現行サイトのスクリーンショット・掲載画像・メタ情報を収集するスクリプトです。

### なぜ必要か

本設計書を作成したセッションでは、**組織のネットワーク送信ポリシーにより
muto-coffee.com への直接アクセスが遮断されており**、サイトの実画面・掲載画像・
HTML ソースを取得できませんでした。

このスクリプトを **ネットワーク制限のない環境で実行する**ことで、
設計書の現状分析を実測値で裏付けられます。

### 準備

```bash
python3 -m pip install playwright requests beautifulsoup4 pillow
python3 -m playwright install chromium
```

### 実行

```bash
cd tools

# 既定（設計書に記載の URL 一覧が対象）
python3 capture_site.py

# サイト内を巡回して対象を自動で広げる
python3 capture_site.py --crawl --max-pages 60

# 出力先を変える
python3 capture_site.py --out ../images/actual
```

### 出力されるもの

| ファイル | 内容 |
|---|---|
| `screenshots/pc/*.png` | PC 幅 1440px のフルページ画像 |
| `screenshots/sp/*.png` | スマホ幅 390px のフルページ画像 |
| `assets/*` | ページに掲載されている画像の実体 |
| `report_pages.csv` | URL・title・description・canonical・見出し構造・JSON-LD の有無 |
| `report_images.csv` | 画像ごとの寸法・容量・形式・alt の有無と**判定** |
| `report_summary.md` | 要約。**まずこれを開いてください** |

### 結果の使い方

1. `report_summary.md` で問題の全体像をつかむ
2. `report_images.csv` の「判定」が NG の画像を、設計書 `03_デザインシステム.md` §6.3 の仕様で書き出し直す
3. `report_pages.csv` の title / description を、設計書 `04_技術要件・SEO・計測設計.md` §4.1 の設計に差し替える
4. `--crawl` で得た URL 一覧を、`04_技術要件・SEO・計測設計.md` §2 のリダイレクト対応表に反映する
5. スクリーンショットを `../images/actual/` に置き、現状分析の裏付けとする

### 注意

- サイトに負荷をかけないよう、リクエスト間に 0.5 秒の待機を入れています。`--max-pages` を過度に大きくしないでください。
- 自社サイトに対して実行する前提のスクリプトです。
