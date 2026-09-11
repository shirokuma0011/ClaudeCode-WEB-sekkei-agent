# assets/originals/ — 現行サイトの画像置き場

このフォルダは**空**です。

本設計書を作成した実行環境は外部ネットワークが遮断されており
（egress proxy による 403 CONNECT 拒否。全ドメインで再現）、
`www.kyoushin-jt.co.jp` の画像を取得して同梱することができませんでした。

## 画像を取得する手順

ネットワークに繋がるお手元のPCで、以下を実行してください。

```bash
cd design/kyoushin-jt
chmod +x tools/fetch-site-assets.sh
./tools/fetch-site-assets.sh
```

実行すると、このフォルダに現行サイトの全画像が保存され、
あわせて `tools/_crawl/` に次の3つのCSVが生成されます。

| ファイル | 用途 |
|---|---|
| `urls.csv` | 全URLの棚卸し → 設計書 03章5節の301リダイレクト表に反映 |
| `images.csv` | 画像の容量一覧 → 300KB超を 05章7節の基準で再書き出し |
| `meta.csv` | title / description / alt欠落数 → 07章2節の新title案と突合 |

wget が入っていない場合は、スクリプトが手動取得の手順を表示します。

## このフォルダに入れるもの

- 現行サイトから取得した画像（リニューアル時の移行元・比較対象）
- 差し替え前の原本

新規に書き出した画像は、`05_デザインシステム.md` 7.2節の命名規則にしたがって
別フォルダ（例: `assets/images/`）に配置してください。
