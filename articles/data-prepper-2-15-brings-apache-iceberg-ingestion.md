---
title: "[翻訳] Data Prepper 2.15 で Apache Iceberg 取り込みと Prometheus メトリクスをサポート"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "dataprepper", "iceberg", "prometheus", "observability"]
publication_name: "opensearch"
published: true
published_at: 2026-04-06
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/data-prepper-2-15-brings-apache-iceberg-ingestion-and-prometheus-metrics-support/

OpenSearch Data Prepper のメンテナーは、[Data Prepper 2.15](https://github.com/opensearch-project/data-prepper/releases/tag/2.15.0) のリリースを発表しました。このバージョンでは、Apache Iceberg からのデータ取り込みが可能になりました。また、リモートライトソースとオープンソース Prometheus へのデータ送信機能により、Prometheus のサポートが拡張されています。

## Apache Iceberg ソース

[Apache Iceberg](https://iceberg.apache.org/) は、レイクハウスアーキテクチャで広く使用されているオープンテーブルフォーマットです。Iceberg テーブルは、キュレーションおよび変換されたデータの信頼できる唯一の情報源 (Single Source of Truth) として機能することが多くあります。検索やリアルタイムダッシュボードのために、OpenSearch をこれらのテーブルと同期させることは一般的なニーズです。これまでは、Iceberg の変更ログを読み取って OpenSearch に書き込むために、分散コンピューティングエンジン上にカスタムの取り込みジョブを構築する必要があり、本質的にはデータ移動タスクであるにもかかわらず、運用上の複雑さが増していました。

Data Prepper 2.15 では、Iceberg テーブルから行レベルの変更をキャプチャし、OpenSearch などのシンクターゲットに取り込む実験的な `iceberg` ソースプラグインが導入されました。このプラグインは、まずテーブルの完全な状態をエクスポートし、その後、新しいスナップショットを継続的にポーリングして、増分の `INSERT`、`UPDATE`、`DELETE` 操作を処理します。

以下のパイプライン例では、REST カタログを使用して Iceberg テーブルから変更を読み取り、OpenSearch に書き込みます。

```yaml
iceberg-cdc-pipeline:
  source:
    iceberg:
      tables:
        - table_name: "my_database.my_table"
          catalog:
            type: rest
            uri: "http://iceberg-rest-catalog:8181"
            io-impl: "org.apache.iceberg.aws.s3.S3FileIO"
            client.region: "us-east-1"
          identifier_columns: ["id"]
  sink:
    - opensearch:
        hosts: ["https://localhost:9200"]
        index: "my-index"
        action: "${getMetadata(\"bulk_action\")}"
        document_id: "${getMetadata(\"document_id\")}"
```

## オープンソース Prometheus をシンクとして使用

Data Prepper 2.14 では、[Amazon Managed Service for Prometheus](https://aws.amazon.com/prometheus/) へのメトリクス書き込み機能が導入されました。Data Prepper 2.15 では、Prometheus シンクがオープンソースの [Prometheus](https://prometheus.io/) もサポートするようになりました。認証なし、または HTTP ベーシック認証を使用して、AWS 認証なしで任意の Prometheus 互換エンドポイントにメトリクスを送信できます。

以下のパイプライン例では、ベーシック認証を使用してオープンソース Prometheus インスタンスにメトリクスを書き込みます。

```yaml
prometheus-pipeline:
  source:
    otel_metrics_source:
  sink:
    - prometheus:
        url: "http://my-prometheus-server:9090/api/v1/write"
        authentication:
          http_basic:
            username: "myuser"
            password: "mypassword"
```

## Prometheus ソース

Data Prepper 2.15 では、[Prometheus Remote-Write プロトコル](https://prometheus.io/docs/specs/prw/remote_write_spec_2_0/)を通じてメトリクスを取り込む新しい Prometheus ソースが導入されました。これにより、Prometheus サーバーから Data Prepper にメトリクスを直接転送でき、Data Prepper はそれらを OpenTelemetry 互換のメトリクスイベントに変換して下流の処理に渡します。

このソースは、HTTP 経由で Snappy 圧縮された Protobuf エンコードの Remote-Write リクエストを受け付け、カウンター、ゲージ、ヒストグラム、サマリーを含むすべての標準的な Prometheus メトリクスタイプをサポートします。Prometheus シンクと組み合わせて使用することで、Data Prepper 内でエンドツーエンドの Prometheus メトリクスパイプラインを構築できます。

以下のパイプライン例では、Prometheus サーバーからメトリクスを受信し、OpenSearch に書き込みます。

```yaml
prometheus-pipeline:
  source:
    prometheus:
      port: 9090
      path: "/api/v1/write"
  sink:
    - opensearch:
        hosts: ["https://localhost:9200"]
        index: prometheus-metrics
```

## コンポーザブル関数

Data Prepper の式 (Expression) を使用すると、パイプラインを動的にカスタマイズできます。式を使用して、データのルーティング、イベントの変更、パイプライン設定内での条件付きロジックの適用が可能です。式の中で関数を使用してリッチな条件を構築している方もいるかもしれません。Data Prepper 2.15 では、関数を組み合わせてさらに高度な式を作成できるようになりました。

たとえば、イベントを JSON 文字列に変換し、その文字列の長さを取得することで、イベントのおおよそのサイズを計算できます。

```yaml
- add_entries:
    entries:
      - key: "approximateSize"
        value_expression: 'length(toJsonString())'
```

## アプリケーションパフォーマンスモニタリングの改善

Data Prepper 2.15 では、APM サービスマッププロセッサーにおいて、Prometheus にエクスポートされるレイテンシメトリクスのメトリクス名に `_seconds` サフィックスが重複し、`latency_seconds_seconds` となっていた問題が修正されました。メトリクス名は `latency_seconds` として正しくエクスポートされるようになりました。

## その他の主な変更点

このリリースには、以下の追加改善が含まれています。

- `s3` シンクがサーバーサイド暗号化用のカスタム KMS キーをサポートするようになりました。
- 新しい `s3_enrich` プロセッサーにより、S3 バケットに保存されたデータでイベントをエンリッチできるようになりました。
- Data Prepper の式で新しい部分文字列関数 `substringAfter`、`substringBefore`、`substringAfterLast`、`substringBeforeLast` がサポートされるようになりました。
- `sqs` シンクが実験的ではなくなり、本番環境で使用できるようになりました。

## はじめに

Data Prepper 2.15 を使い始めるには、以下のリソースを参照してください。

- すべての変更点については、[2.15.0 リリースノート](https://github.com/opensearch-project/data-prepper/releases/tag/2.15.0)を参照してください。
- Data Prepper をダウンロードするには、[ダウンロードページ](https://opensearch.org/downloads.html)にアクセスしてください。
- Data Prepper の使い方については、[Getting started with OpenSearch Data Prepper](https://opensearch.org/docs/latest/data-prepper/getting-started/) を参照してください。
- Data Prepper の今後の予定については、[Data Prepper Project Roadmap](https://github.com/orgs/opensearch-project/projects/221) を参照してください。

## コントリビューターへの感謝

このリリースに貢献してくださった以下のコミュニティメンバーに感謝します。

- [bagmarnikhil](https://github.com/bagmarnikhil) — Nikhil Bagmar
- [BhattacharyaSumit](https://github.com/BhattacharyaSumit) — Sumit Bhattacharya
- [Davidding4718](https://github.com/Davidding4718) — Siqi Ding
- [dinujoh](https://github.com/dinujoh) — Dinu John
- [divbok](https://github.com/divbok) — Divyansh Bokadia
- [dlvenable](https://github.com/dlvenable) — David Venable
- [enuraju](https://github.com/enuraju) — Raju Enugula
- [graytaylor0](https://github.com/graytaylor0) — Taylor Gray
- [JongminChung](https://github.com/JongminChung)
- [kaimst](https://github.com/kaimst) — Kai Sternad
- [Keyur-S-Patel](https://github.com/Keyur-S-Patel) — Keyur Patel
- [kkondaka](https://github.com/kkondaka) — Krishna Kondaka
- [kylehounslow](https://github.com/kylehounslow) — Kyle Hounslow
- [lawofcycles](https://github.com/lawofcycles) — Sotaro Hikita
- [oeyh](https://github.com/oeyh) — Hai Yan
- [ps48](https://github.com/ps48) — Shenoy Pratik
- [srikanthpadakanti](https://github.com/srikanthpadakanti) — Srikanth Padakanti
- [TomasLongo](https://github.com/TomasLongo) — Tomas
- [vamsimanohar](https://github.com/vamsimanohar) — Vamsi Manohar
- [Zhangxunmt](https://github.com/Zhangxunmt) — Xun Zhang
