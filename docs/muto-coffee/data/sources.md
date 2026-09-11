# 出典一覧

本設計書の現状分析は、以下の公開情報に基づいています。
調査日: 2026-09-11

## 重要な注記

> **本セッションの実行環境では、組織のネットワーク送信ポリシーにより `muto-coffee.com` を含む外部サイトへの直接アクセスが遮断されていました。**
> このため以下の情報は **検索エンジン経由で取得できた URL・ページタイトル・スニペットと、第三者媒体の記述** を突き合わせて構成しています。
> **サイト本体の HTML・実画面のスクリーンショット・掲載画像は取得できていません。**

---

## 1. 公式サイト（検索経由で URL とタイトルを確認）

| URL | 確認できた内容 |
|---|---|
| https://muto-coffee.com/ | トップ。title「MUTO coffee roastery - 中野 / 東京」 |
| https://muto-coffee.com/news/ | News 一覧。title「News一覧 \| MUTO coffee roastary」（綴り誤記） |
| https://www.muto-coffee.com/shop/ | ショップ TOP |
| https://www.muto-coffee.com/shop/products/detail/{8,10,11,12,15,17,20,34,37,41,55} | 商品詳細。商品名と価格 |
| https://www.muto-coffee.com/shop/help/about | 当サイトについて |
| https://www.muto-coffee.com/shop/help/tradelaw | 特商法表記。株式会社 Lounge M / 武藤修一郎 |
| https://muto-coffee.com/{日本語スラッグ}/ | News 個別記事 7 件（詳細は page_inventory.csv） |

## 2. 公式 SNS

| 媒体 | URL | 確認できた内容 |
|---|---|---|
| Instagram | https://www.instagram.com/mutocoffeeroastery/ | フォロワー約 482、投稿 9 件 |
| Facebook | https://www.facebook.com/mutocoffeeroastery/ | アカウントの存在 |

## 3. 第三者媒体（店舗情報・メニュー・評判）

| 媒体 | URL | 参照した内容 |
|---|---|---|
| 食べログ | https://tabelog.com/tokyo/A1319/A131902/13173656/ | 店舗基本情報、口コミ |
| 食べログ（英語） | https://tabelog.com/en/tokyo/A1319/A131902/13173656/ | 同上 |
| ヒトサラ | https://hitosara.com/0031259291/ | 店舗情報、地図 |
| ホットペッパー | https://www.hotpepper.jp/strJ004213921/ | 店舗情報 |
| さんたつ by 散歩の達人（記事） | https://san-tatsu.jp/articles/217904/ | 店主コメント、店内の様子、ハンドドリップの説明 |
| さんたつ by 散歩の達人（スポット） | https://san-tatsu.jp/spots/217928/ | 営業時間、定休日、アクセス |
| Retty | https://retty.me/area/PRE13/ARE12/SUB1201/100001172410/ | 口コミ、メニュー |
| Retty（メニュー） | https://retty.me/area/PRE13/ARE12/SUB1201/100001172410/menu/ | 店内メニューと価格 |
| CafeSnap | https://cafesnap.me/c/353 | 店舗情報、Wi-Fi・電源の有無 |
| CafeSnap（メニュー） | https://cafesnap.me/c/353/menu | メニュー |
| 号外NET 中野区 | https://nakano.goguynet.jp/2025/03/25/muto/ | 2025年の記事。店の雰囲気、毎朝焙煎 |
| 中野経済新聞 | https://nakano.keizai.biz/headline/557/ | 開業時の記事（2014年10月3日開業） |
| 無印良品 中野マルイ | https://www.muji.com/jp/ja/shop/045289/articles/other/346071 | 中野まち歩き記事。店の紹介 |
| Only Roaster | https://onlyroaster.com/mutocoffee/ | ロースタリー情報、GIESEN 焙煎機 |
| 楽天ぐるなび | https://r.gnavi.co.jp/mnfjkjaf0000/ | 店舗情報、地図 |
| Yelp | Yelp 内 店舗ページ | 英語レビューの存在 |
| Trip.com | https://www.trip.com/moments/detail/nakano-ward-60625-129811327/ | 訪日客のレビュー |
| Wanderlog | https://wanderlog.com/place/details/3377907/muto-coffee-roastery | 英語での紹介 |
| くふうトリップ（旧RETRIP） | https://rtrp.jp/spots/638ed500-ad05-4e77-89a8-a28dbfafd83d/ | 店舗情報 |
| MEQQE | https://meqqe.jp/spots/10271776 | 店舗情報 |
| Yahoo!マップ | https://map.yahoo.co.jp/v3/place/rUw5XZ25Lig | 口コミ、営業時間 |
| チーズケーキ通信 | https://cheese-cake.net/muto-coffee/ | ベイクドチーズケーキの詳細 |
| こじんまり個人カフェ巡りの記録 | https://www.hirorocafe.com/entry/2019/09/03/... | 2019年の訪問記。店内の様子 |
| 「つ」な関西人の観察日記 | https://tukanana.cocolog-nifty.com/blog/2014/10/muto-coffee-roa.html | 2014年の訪問記（開業直後） |
| 山口的おいしいコーヒーブログ | https://coffee-beans-ranking.com/area-69087/ | 中野のコーヒー豆販売店まとめ |

## 4. 情報の不一致について

営業時間と定休日は媒体によって記述が異なります。**設計書では【要確認】として扱い、店舗へのヒアリングを必須としています。**

| 内容 | 記述している媒体の傾向 |
|---|---|
| 11:30〜19:00（L.O. 18:00）／水曜・木曜休 | 多数派 |
| 11:30〜19:30（L.O. 19:00）／木曜＋第1・第3水曜休 | 一部媒体 |
| 木曜休（水曜の記述なし） | 一部媒体 |

この不一致自体が、設計書の「課題 B」の根拠となっています。

## 5. 価格情報の扱い

`products.csv` および `store_menu.csv` に記載した価格は、**検索結果のスニペットおよび第三者媒体に現れた値**です。
掲載時期が不明なものを含むため、**すべて実装前に店舗への確認が必要**です。改定されている可能性があります。
