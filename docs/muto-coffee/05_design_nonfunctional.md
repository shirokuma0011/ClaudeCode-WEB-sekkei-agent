# 05. デザイン・非機能要件

## 1. トーン＆マナー

| 観点 | 方針 |
|---|---|
| キーワード | 静かな路地裏、木とレザー、焙煎の手仕事、誠実、上質だが気取らない |
| 全体印象 | 余白を広く取り、写真（焙煎機・豆・カップ・店内）を主役にする。装飾は最小限 |
| 文体 | 丁寧語。News は店主の声として一人称を許容。英字ラベル（About／Menu／News／Access）と日本語本文の併用 |
| 写真 | 自然光、暖色寄り。人物は手元中心。スタンプ的な加工はしない |

現行サイトの実際の配色・書体は未確認（99章）。以下は再構築時の提案値であり、現行ブランド資産（ロゴ・店頭サイン）に合わせて最終決定する。

## 2. カラーパレット【提案】

| 役割 | 名称 | HEX | 用途 |
|---|---|---|---|
| Primary | Roast Brown | `#4A3327` | 見出し、ボタン、ロゴ |
| Primary Light | Latte | `#8C6A50` | ホバー、リンク |
| Accent | Copper | `#B8733A` | CTA（Online Shop）、バッジ |
| Background | Cream | `#F7F3EE` | ページ背景 |
| Surface | White | `#FFFFFF` | カード、フォーム |
| Text | Charcoal | `#2B2523` | 本文 |
| Text Sub | Stone | `#6F6661` | 補足、日付 |
| Border | Sand | `#E2D9CF` | 罫線 |
| Success／Error | `#3B7D4F`／`#B23A3A` | 営業中表示、フォームエラー |

コントラスト: Text on Cream = 13.2:1、Accent on White = 4.6:1（AA 準拠）。Accent 上の白文字はボタンなど大きめの文字に限定する。

## 3. タイポグラフィ【提案】

| 用途 | 書体 | サイズ（PC／SP） | 行間 |
|---|---|---|---|
| 見出し（英字） | Cormorant Garamond または同系セリフ | 40／28px | 1.2 |
| 見出し（日本語） | Noto Serif JP | 28／22px | 1.4 |
| 本文 | Noto Sans JP | 16／15px | 1.8 |
| 価格・数値 | Noto Sans JP（tabular-nums） | 16px | – |
| ラベル・日付 | Noto Sans JP | 13px | 1.5 |

Web フォントは表示遅延を避けるため `font-display: swap`、日本語はサブセット配信。ショップ（EC-CUBE）側も同じ CSS 変数を読み込み、ヘッダー・フッター・ボタンの見た目を店舗サイトと揃える。

## 4. コンポーネント規約

| コンポーネント | 仕様 |
|---|---|
| ボタン（Primary） | 高さ 48px、角丸 4px、背景 Accent、文字 白、ホバーで 10% 暗く |
| ボタン（Secondary） | 枠線 Primary、背景 透明 |
| カード（商品） | 画像 1:1、余白 16px、影なし、枠線 Border |
| バッジ（焙煎度） | 小型ピル。浅煎り=Latte、中煎り=Copper、深煎り=Roast Brown |
| News 行 | 日付（Stone）＋カテゴリラベル＋タイトル。行全体がリンク |
| フォーム | ラベル上置き、入力高さ 48px、エラーは赤文字＋アイコン＋枠線 |

## 5. 画像・アセット

| 種別 | 仕様 |
|---|---|
| ヒーロー | 1920×1080、WebP、200KB 以下 |
| 商品画像 | 1200×1200、WebP、背景は白または木目で統一 |
| News サムネイル | 1200×800 |
| ロゴ | SVG（モノクロ版も用意） |
| OGP | 1200×630、店名入り |
| favicon | SVG＋PNG 32/180/512 |

## 6. SEO 設計

### 6.1 title／description

| ページ | title | description（120字以内） |
|---|---|---|
| トップ | MUTO coffee roastery ｜ 中野の自家焙煎スペシャルティコーヒー | 中野駅南口徒歩2分。GIESEN 焙煎機で毎日焙煎するスペシャルティコーヒーとハンドドリップ、自家製ケーキ。豆の販売・オンラインショップも。 |
| News 一覧 | News ｜ MUTO coffee roastery | 営業のお知らせ、新入荷豆、セール情報。 |
| News 詳細 | {記事タイトル} ｜ MUTO coffee roastery | 記事冒頭 100 字 |
| ショップ TOP | オンラインショップ ｜ MUTO coffee roastery | 焙煎したてのコーヒー豆を全国へ。クレジットカード決済、3営業日以内発送。 |
| 商品詳細 | {商品名} 200g ｜ MUTO coffee roastery オンラインショップ | 焙煎度・精製方法・味わいの要約 |

現行のサイト名表記は「MUTO coffee roastery」と「MUTO coffee roastary」（News 側のタイトル末尾）が混在している。正しい綴りは roastery であり、WordPress の一般設定「サイトのタイトル」を修正する（06章）。

### 6.2 構造化データ（JSON-LD）

トップ（店舗）:

```json
{
  "@context": "https://schema.org",
  "@type": "CafeOrCoffeeShop",
  "name": "MUTO coffee roastery",
  "url": "https://muto-coffee.com/",
  "telephone": "+81-3-6382-5439",
  "address": {
    "@type": "PostalAddress",
    "postalCode": "164-0001",
    "addressRegion": "東京都",
    "addressLocality": "中野区",
    "streetAddress": "中野3-34-18",
    "addressCountry": "JP"
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Friday", "Saturday", "Sunday"],
      "opens": "11:30",
      "closes": "19:00"
    }
  ],
  "servesCuisine": "Coffee",
  "sameAs": [
    "https://www.instagram.com/mutocoffeeroastery/",
    "https://www.facebook.com/mutocoffeeroastery/"
  ]
}
```

商品詳細:

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "ケニア／キリニャガ カムワンギ・ファクトリー",
  "image": "https://muto-coffee.com/shop/html/upload/save_image/xxx.jpg",
  "description": "Washed / フレンチ。完熟果実やベリーの凝縮感、なめらかな酸味と甘み。",
  "brand": { "@type": "Brand", "name": "MUTO coffee roastery" },
  "offers": {
    "@type": "Offer",
    "url": "https://muto-coffee.com/shop/products/detail/12",
    "priceCurrency": "JPY",
    "price": "2200",
    "availability": "https://schema.org/InStock"
  }
}
```

News 詳細には `NewsArticle`、各ページに `BreadcrumbList` を出力する。

### 6.3 その他

| 項目 | 方針 |
|---|---|
| canonical | 02章 R-06 |
| sitemap | 店舗サイト `/sitemap.xml`、ショップ `/shop/sitemap.xml`。`robots.txt` で両方を宣言 |
| OGP／Twitter Card | 全ページ。商品詳細は商品画像、News は アイキャッチ |
| 見出し構造 | h1 は1ページ1つ。セクションは h2、カード内は h3 |
| Google ビジネスプロフィール | 営業時間・定休日をサイトと同期。臨時休業は両方更新 |

## 7. アクセシビリティ

| 項目 | 基準 |
|---|---|
| コントラスト | 本文 4.5:1 以上、大文字 3:1 以上 |
| キーボード | 全ての操作要素にフォーカス可視化。ハンバーガーメニューはフォーカストラップ |
| 代替テキスト | 商品画像は商品名、装飾画像は空 alt |
| フォーム | `label` と `input` を関連付け。エラーは `aria-describedby` |
| 動き | 自動再生スライダーは使わない。使う場合は停止ボタン |
| 言語 | `<html lang="ja">` |
| 電話 | `tel:` リンク。SP で即発信可能 |

## 8. パフォーマンス

| 指標 | 目標 | 施策 |
|---|---|---|
| LCP | 2.5秒以内 | ヒーロー画像の事前読み込み、WebP、CDN またはサーバー側キャッシュ |
| CLS | 0.1以下 | 画像に width／height 指定、Web フォントの swap |
| INP | 200ms以下 | JS は最小限。埋め込み（地図・Instagram）は遅延読み込み |
| 転送量 | トップ 1.5MB 以下 | 画像最適化、未使用 CSS 削除 |

## 9. セキュリティ

| 項目 | 方針 |
|---|---|
| 通信 | 全ページ HTTPS、HSTS |
| 管理画面 | WordPress `/wp-admin/`、EC-CUBE `/shop/admin/` とも IP 制限またはベーシック認証＋強固なパスワード。二要素認証を推奨 |
| 更新 | WordPress／EC-CUBE 本体とプラグインを月次で更新。EC-CUBE 3 系はサポート終了のため、4 系への移行を計画（06章） |
| 決済 | カード情報は決済代行のトークン方式で非保持。PCI DSS 対応は代行側に委ねる |
| フォーム | CSRF トークン、reCAPTCHA 等のスパム対策 |
| バックアップ | 日次自動、外部保管、復元手順を文書化 |
| ログ | 管理画面ログイン失敗の監視、WAF（レンタルサーバー提供のもので可） |
| 個人情報 | 会員情報は EC-CUBE DB のみで保持。CSV エクスポートはローカルに残さない |
