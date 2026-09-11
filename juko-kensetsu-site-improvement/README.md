# 重光建設株式会社 Webサイト改善設計書 v1.0

対象サイト: https://www.juko-kensetsu.co.jp/
作成日: 2026-09-11

## この成果物について

八王子市の工務店・重光建設株式会社の公式サイトを、**「問い合わせが生まれるサイト」**へ作り替えるための設計書一式です。
現状分析、情報設計、ページ別ワイヤーフレーム、デザイン仕様、SEO設計、技術要件、実施計画までを含みます。

## ⚠ 重要な前提（必ず最初にお読みください）

本設計書を作成した実行環境ではネットワーク制限により **対象サイト本体（www.juko-kensetsu.co.jp）へアクセスできませんでした。**
そのため現状分析は、検索エンジンの索引情報・各種企業情報サイトに公開された情報から再構成した**推定**を含みます。
事実確認が必要な項目は `docs/11_前提条件と要確認事項.md` に一覧化しています。**実装着手前に必ず実機で照合してください。**

一方、改善方針・情報設計・デザイン仕様・SEO設計・実施計画は、工務店サイトの一般的な成功パターンと同社の事業特性に基づくもので、
現状の細部が多少異なっても**そのまま適用できる設計**にしています。

## ディレクトリ構成

```
juko-kensetsu-site-improvement/
├── README.md                     ← このファイル
├── docs/                         ← 設計書本体（12章）
│   ├── 00_エグゼクティブサマリー.md
│   ├── 01_現状分析.md
│   ├── 02_ターゲットとゴール設計.md
│   ├── 03_サイト構成・URL設計.md
│   ├── 04_ページ別設計.md
│   ├── 05_デザインガイドライン.md
│   ├── 06_SEO・集客設計.md
│   ├── 07_技術要件・実装仕様.md
│   ├── 08_コンテンツ制作計画.md
│   ├── 09_計測設計とKPI.md
│   ├── 10_実施計画・体制・概算費用.md
│   └── 11_前提条件と要確認事項.md
├── images/                       ← 図版・ワイヤーフレーム（PNG 16点）
└── wireframes-src/               ← 図版のHTMLソースと再生成スクリプト
```

## 図版一覧

| ファイル | 内容 |
| --- | --- |
| `images/01_sitemap_current.png` | 現行サイト構成（推定） |
| `images/02_sitemap_proposed.png` | 提案サイト構成 |
| `images/03_user_flow.png` | ユーザー導線図 |
| `images/04_design_tokens.png` | カラー・タイポグラフィ仕様 |
| `images/05_priority_matrix.png` | 改善施策の優先度マトリクス |
| `images/06_layout_grid.png` | 共通レイアウト・グリッド仕様 |
| `images/10_wf_top_pc.png` / `11_wf_top_sp.png` | トップページ（PC/SP） |
| `images/12_wf_concept_pc.png` | 家づくりのこだわり |
| `images/13_wf_works_list_pc.png` | 施工事例 一覧 |
| `images/14_wf_works_detail_pc.png` | 施工事例 詳細 |
| `images/15_wf_voice_pc.png` | お客様の声 |
| `images/16_wf_flow_pc.png` | 家づくりの流れ・費用 |
| `images/17_wf_company_pc.png` | 会社案内 |
| `images/18_wf_contact_pc.png` / `19_wf_contact_sp.png` | お問い合わせ（PC/SP） |

## 読む順番のおすすめ

1. **経営判断だけ知りたい** → `00_エグゼクティブサマリー.md` と `10_実施計画・体制・概算費用.md`
2. **制作会社への発注仕様として使う** → 全章 + `images/` 一式
3. **社内で内製する** → `03` → `04` → `05` → `07` → `08` の順

## 図版の再生成

`wireframes-src/` 内にHTMLソースと `build.sh` があります。Node.js と Playwright がある環境で以下を実行すると全PNGを再生成できます。

```bash
cd wireframes-src && bash build.sh
```
