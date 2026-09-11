# 07. SEOと計測設計

## 1. 現状の最大の問題

課題A-2（00章・01章）のとおり、**全ページのtitleが同一の接尾辞で埋まっています**。

```
施工例 -外観・外構- | 協進住宅|協進建設|八王子市|不動産    ← 30文字中、固有部分は9文字
PLAN集 | 協進住宅|協進建設|八王子市|不動産                  ← 固有部分は6文字
```

検索結果ではタイトルが全角30文字前後で省略されるため、
**ページ固有の情報が表示されない状態**です。加えて、パイプ区切りのキーワード羅列は
Googleによるタイトル書き換えの対象になりやすく、意図しない表示につながります。

---

## 2. title / description 設計ルール

### 2.1 title

```
{ページ固有の内容} | {ブランドまたは社名}
```

- **全角32文字以内**。固有部分を**必ず先頭**に置く。
- 社名は**末尾に1つだけ**。「協進住宅」「不動産」等の重複は削除。
- 同じtitleのページを作らない。

| ページ | 新title | 文字数 |
|---|---|---|
| トップ | 八王子の注文住宅・分譲住宅なら協進建設 \| ステイブルハウス | 29 |
| `/custom-home/` | 注文住宅ステイブルハウス｜八王子の高気密高断熱住宅 \| 協進建設 | 31 |
| `/custom-home/performance/` | 高気密高断熱の性能｜UA値・C値で選ぶ家 \| 協進建設 | 26 |
| `/custom-home/zeh-bels/` | ZEH・BELS★★★★の省エネ住宅と補助金 \| 協進建設 | 25 |
| `/custom-home/plans/` | 間取りプラン集｜八王子の注文住宅 \| 協進建設 | 22 |
| `/property/` | 八王子市の物件情報｜新築分譲住宅・売地 \| 協進建設 | 25 |
| `/property/new-house/` | 八王子市の新築分譲住宅一覧 \| 協進建設 | 19 |
| `/property/land/` | 八王子市の売地・建築条件付売地 \| 協進建設 | 21 |
| `/property/{id}/` | 【新築分譲】八王子市八木町 3LDK 3,480万円 \| 協進建設 | 29 |
| `/renovation/` | 八王子のリフォーム・リノベーション \| 協進建設 | 22 |
| `/works/` | 施工事例｜八王子の新築・リノベーション \| 協進建設 | 24 |
| `/works/{id}/` | 八王子市I様邸｜共働き夫婦の4LDK新築事例 \| 協進建設 | 26 |
| `/about/company/` | 会社概要｜株式会社協進建設（八王子市） | 19 |
| `/contact/` | お問い合わせ・資料請求 \| 協進建設 | 17 |

### 2.2 meta description

- **全角90〜120文字**。ページの要約＋行動喚起を1文含める。
- テンプレート自動生成に頼らず、**主要20ページは手書き**。
- 物件・事例の詳細は、フィールド値から自動生成でよい。

```
例 /custom-home/performance/:
「協進建設の高気密高断熱住宅の性能をUA値・C値の実測データで解説します。
夏涼しく冬暖かい家が、実際に光熱費をいくら抑えるのか。ZEH基準・BELS★★★★の
根拠と断熱材・サッシの仕様までご紹介します。無料の資料請求を受付中です。」（112文字）
```

### 2.3 見出し構造

- `h1` は**1ページに1つ**。titleと同じである必要はなく、ページ内で自然な日本語に。
- `h2` → `h3` の階層を飛ばさない（08章のアクセシビリティ要件でもあります）。
- 見出しをデザイン目的で使わない（大きく見せたいだけなら CSS で）。

---

## 3. キーワード設計

### 3.1 軸となる検索意図

| 意図 | 主要キーワード | 対応ページ |
|---|---|---|
| 会社を探す | 八王子 工務店 / 八王子 注文住宅 / 八王子 ハウスメーカー | `/custom-home/` |
| 性能で選ぶ | 高気密高断熱 八王子 / ZEH 八王子 / BELS 工務店 / UA値 / C値 | `/custom-home/performance/`, `/zeh-bels/` |
| 物件を探す | 八王子 新築 戸建 / 八王子市◯◯町 土地 / 建築条件付売地 八王子 | `/property/*` |
| リフォーム | 八王子 リフォーム / 八王子 リノベーション / 断熱リフォーム 八王子 | `/renovation/` |
| 費用を知る | 注文住宅 費用 八王子 / リフォーム 相場 八王子 | `/custom-home/price/`, `/renovation/price/` |
| 補助金 | ZEH 補助金 2026 / 子育てエコホーム | `/custom-home/zeh-bels/` |
| 指名 | 協進建設 / ステイブルハウス 八王子 | トップ・会社情報 |

### 3.2 勝てる領域の見極め

「八王子 注文住宅」は大手ポータルと大手ハウスメーカーが上位を占めるため、
短期での上位表示は困難です。**先に取るべきは以下の3領域**です。

1. **物件の個別ページ** — 「八王子市八木町 新築」等の具体的な検索は競合が少なく、
   購買意欲が最も高い。物件をDB化する最大の理由がこれです。
2. **性能の技術情報** — 「UA値」「C値」「BELS 星4」は検索数は小さいが、
   検討が深い層に刺さり、かつ同社が本当に語れる領域（E-E-A-T）。
3. **エリア×用途の組み合わせ** — 「八王子 断熱リフォーム」「日野市 建築条件付売地」等。
   Phase 2 のエリアページ（F-23）で面を取ります。

> **注意**: キーワードを詰め込んだ文章を書かないでください。
> 現行titleがまさにその状態であり、評価されないどころか逆効果です。
> 「お客様に説明するときの言葉」で書き、キーワードは自然に含まれていれば十分です。

---

## 4. 構造化データ（JSON-LD）

### 4.1 全ページ共通: Organization / LocalBusiness

```json
{
  "@context": "https://schema.org",
  "@type": ["GeneralContractor", "RealEstateAgent"],
  "name": "株式会社協進建設",
  "url": "https://www.kyoushin-jt.co.jp/",
  "logo": "https://www.kyoushin-jt.co.jp/assets/logo.png",
  "image": "https://www.kyoushin-jt.co.jp/assets/ogp.jpg",
  "telephone": "+81-42-XXX-XXXX",
  "email": "info@kyoushin-jt.co.jp",
  "address": {
    "@type": "PostalAddress",
    "postalCode": "192-XXXX",
    "addressRegion": "東京都",
    "addressLocality": "八王子市",
    "streetAddress": "（要確認・NAP統一後の正式表記）",
    "addressCountry": "JP"
  },
  "geo": { "@type": "GeoCoordinates", "latitude": 35.XXXX, "longitude": 139.XXXX },
  "openingHoursSpecification": [{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
    "opens": "09:00", "closes": "18:00"
  }],
  "areaServed": [
    {"@type":"City","name":"八王子市"}, {"@type":"City","name":"日野市"},
    {"@type":"City","name":"多摩市"}, {"@type":"City","name":"あきる野市"}
  ],
  "foundingDate": "1998"
}
```

### 4.2 物件詳細: RealEstateListing

```json
{
  "@context": "https://schema.org",
  "@type": "RealEstateListing",
  "name": "【新築分譲】八王子市八木町 3LDK",
  "url": "https://www.kyoushin-jt.co.jp/property/1042-yagicho-newhouse/",
  "datePosted": "2026-09-01",
  "image": ["https://.../property-1042-01-1200.webp"],
  "offers": {
    "@type": "Offer", "price": 34800000, "priceCurrency": "JPY",
    "availability": "https://schema.org/InStock"
  },
  "about": {
    "@type": "SingleFamilyResidence",
    "numberOfRooms": 3,
    "floorSize": { "@type": "QuantitativeValue", "value": 98.54, "unitCode": "MTK" },
    "address": {
      "@type": "PostalAddress",
      "addressRegion": "東京都", "addressLocality": "八王子市", "streetAddress": "八木町"
    }
  }
}
```

- `availability` は物件ステータスに連動:
  販売中 → `InStock` / 商談中 → `LimitedAvailability` / 成約済 → `SoldOut`。

### 4.3 その他

| ページ | スキーマ |
|---|---|
| 全下層 | `BreadcrumbList` |
| 施工事例 | `Article` ＋ `ImageObject` |
| お知らせ | `NewsArticle` |
| よくある質問 | `FAQPage`（該当ページがある場合のみ） |

> **実装後は必ず [リッチリザルトテスト](https://search.google.com/test/rich-results) で検証**してください。
> 構造化データと実際の表示内容が一致しないと、手動対策の対象になり得ます。

---

## 5. NAP統一（課題A-7）

検索インデックス上に**2組の住所・電話番号**が存在します（00章2.1）。

### 対応手順

1. **正を決める** — 現在の本社住所・代表電話を確定する。
2. **サイト内を統一** — フッター、会社概要、構造化データ、`tel:` リンクのすべてを同一表記に。
   表記ゆれ（丁目の「-」と「丁目」、ハイフンの種類）も揃える。
3. **Googleビジネスプロフィール** を正の情報に更新し、オーナー確認を完了させる。
4. **外部サイトの修正依頼** — 宅建協会、ハトマークサイト、いい家ネット、
   ポータルサイト、工務店比較サイト等に掲載されている情報の修正を依頼する。
5. **旧住所がある場合** — 「20XX年に移転しました」と会社概要に明記。
   旧情報にたどり着いた人を迷わせない。

> ローカル検索では、Web上のNAP情報の一貫性が評価に影響します。
> 5の外部サイト修正は地味ですが、地域密着型企業では効果が大きい作業です。

---

## 6. 計測設計（GA4）

### 6.1 導入前提

**リニューアル着手前に、現行サイトへGA4とSearch Consoleを設置し、
最低4週間のベースラインを取得してください。** これがないと効果測定ができません。

### 6.2 コンバージョン定義

| イベント名 | 発火条件 | 重要度 |
|---|---|---|
| `contact_submit` | 問い合わせフォーム送信完了（完了ページ到達） | ★★★ 主要CV |
| `document_request` | 資料請求フォーム送信完了 | ★★★ 主要CV |
| `visit_booking` | 来場予約フォーム送信完了 | ★★★ 主要CV |
| `property_inquiry` | 物件個別の問い合わせ送信（物件IDをパラメータに付与） | ★★★ 主要CV |
| `tel_tap` | `tel:` リンクのタップ | ★★☆ マイクロCV |
| `form_start` | フォームの最初の入力欄にフォーカス | ★☆☆ 離脱分析用 |
| `property_filter` | 物件一覧の絞込み実行（条件をパラメータに） | ★☆☆ ニーズ分析 |
| `plan_view` | 間取り詳細の閲覧 | ★☆☆ |
| `scroll_75` | ページの75%までスクロール | ★☆☆ |

`form_start` と `contact_submit` の差分＝**フォーム離脱率**。
ここが高ければ項目を減らす、というPDCAを回します。

### 6.3 カスタムディメンション

| 名称 | 用途 |
|---|---|
| `property_id` | どの物件が問い合わせを生んだか |
| `property_price_band` | 反応の良い価格帯の把握 |
| `property_area` | エリア別の需要把握 |
| `works_category` | 新築／リノベのどちらに関心が集まるか |
| `inquiry_type` | 資料請求／来場／リフォーム相談の内訳 |

### 6.4 月次レポート項目

1. オーガニック流入数と主要キーワードの順位（Search Console）
2. CV数（種別内訳）とCVR
3. 物件別の閲覧数→問い合わせ数（**営業の在庫戦略に直結**）
4. フォーム離脱率
5. Core Web Vitals の実測値（Search Console のウェブに関する主な指標）
6. 404発生URL（リダイレクト漏れの検出）

### 6.5 プライバシー

- IP匿名化（GA4は既定で実施）。
- Cookie同意バナーは、**日本国内向けのみなら必須ではありません**が、
  プライバシーポリシーでの利用目的の明示は必要です。
- フォームの入力内容をGA4に送信しない（個人情報を計測ツールに入れない）。

---

## 7. 公開直後の監視（4週間）

| 時期 | 確認 |
|---|---|
| 公開当日 | 全ページのステータスコード、robots.txt、canonical、GA4発火、フォーム送信テスト |
| 翌日 | Search Console のカバレッジエラー、sitemap 送信 |
| 1週間後 | 404レポート → リダイレクト漏れを補修 |
| 2週間後 | 旧URLのインデックス減／新URLの増を確認 |
| 4週間後 | 流入・順位のベースライン比較。**一時的な下落は正常**。回復傾向を確認 |

> リニューアル直後は検索流入が一時的に下がることがあります（インデックスの入れ替え期間）。
> **4〜8週間は様子を見てください。** 慌てて元に戻すのが最も損失の大きい対応です。
