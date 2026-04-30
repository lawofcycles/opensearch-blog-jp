---
title: "[翻訳] OpenSearch Hadoop connector 2.0 リリース: Spark 4 や Serverless に対応"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "spark", "hadoop", "bigdata"]
publication_name: "opensearch"
published: true
published_at: 2026-04-28
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/introducing-the-opensearch-hadoop-connector-2-0-spark-4-support-opensearch-serverless-and-more/

OpenSearch Hadoop connector 2.0 をリリースしました。Apache Spark 3.5 および 4 への対応、OpenSearch 3.x との互換性、Amazon OpenSearch Serverless のサポートなどが含まれています。

あわせて、セットアップ手順、使用例、設定オプションを記載した [Hadoop connector のドキュメント](https://docs.opensearch.org/latest/clients/hadoop/)も新たに公開しました。本記事では Hadoop connector の概要と、バージョン 2.0 の新機能を紹介します。

## Hadoop connector とは

[Hadoop connector](https://github.com/opensearch-project/opensearch-hadoop) は、[Apache Spark](https://spark.apache.org/)、[Apache Hive](https://hive.apache.org/)、[Hadoop MapReduce](https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html) と OpenSearch の間でデータの読み書きを行うためのコネクタです。これらのシステムはいずれも分散処理基盤であるため、コネクタはコンピュートパーティションと OpenSearch シャードにまたがって読み書きを並列化し、大量データの効率的な処理を実現します。以下の図にそのアーキテクチャを示します。

![OpenSearch Hadoop connector のアーキテクチャ](/images/introducing-the-opensearch-hadoop-connector-2-0/df13ba69355d.png)

## Hadoop connector 2.0 の新機能

2.0 リリースでは以下の主要な機能と改善が含まれています。

### Apache Spark 3.5 および 4 への対応

Hadoop connector 2.0 では、既存の Spark 3.4 モジュールに加えて、Spark 3.5 と Spark 4 の専用モジュールが追加されました。使用している Spark と Scala のバージョンに合ったアーティファクトを選択してください。

| Spark バージョン | Scala バージョン | アーティファクト |
|---|---|---|
| 3.4.x | 2.12 | `org.opensearch.client:opensearch-spark-30_2.12:2.0.0` |
| 3.4.x | 2.13 | `org.opensearch.client:opensearch-spark-30_2.13:2.0.0` |
| 3.5.x | 2.12 | `org.opensearch.client:opensearch-spark-35_2.12:2.0.0` |
| 3.5.x | 2.13 | `org.opensearch.client:opensearch-spark-35_2.13:2.0.0` |
| 4.x | 2.13 | `org.opensearch.client:opensearch-spark-40_2.13:2.0.0` |

Spark 3.5 モジュールにより、Spark 3.5 を含むプラットフォーム上でコネクタを使用できます。Spark 4 モジュールは Spark 4.0 および 4.1 を含む最新の Spark リリースに対応しており、最新の Spark 機能を活用しながら OpenSearch とのデータの読み書きが可能です。

Spark 4 でコネクタを試すには、`--packages` を使ってコネクタを読み込んだ PySpark シェルを起動します。

```
pyspark --packages org.opensearch.client:opensearch-spark-40_2.13:2.0.0
```

データの書き込みと読み取りは以下のように行います。

```python
# OpenSearch にドキュメントを書き込む
df = spark.createDataFrame([("John", 30), ("Jane", 25)], ["name", "age"])
df.write.format("opensearch") \
    .option("opensearch.nodes", "<opensearch host>") \
    .option("opensearch.port", "<port>") \
    .save("people")

# OpenSearch からドキュメントを読み取る
df = spark.read.format("opensearch") \
    .option("opensearch.nodes", "<opensearch host>") \
    .option("opensearch.port", "<port>") \
    .load("people")
df.show()
```

クエリを OpenSearch にプッシュダウンして、条件に一致するドキュメントのみを Spark に転送することもできます。

```python
filtered = spark.read \
    .format("opensearch") \
    .option("opensearch.nodes", "<opensearch host>") \
    .option("opensearch.port", "<port>") \
    .option("opensearch.query", '{"query":{"match":{"name":"John"}}}') \
    .load("people")
filtered.show()
```

認証オプションや Scala、Java、Spark SQL の使用例については、[Hadoop connector のドキュメント](https://docs.opensearch.org/latest/clients/hadoop/)を参照してください。

### Amazon OpenSearch Serverless への対応

[Amazon OpenSearch Serverless](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless.html) コレクションでコネクタを使用できるようになりました。AWS Signature Version 4 認証と `aoss` サービス名を指定して設定します。

```python
df = spark.createDataFrame([("product-1", 29.99), ("product-2", 49.99)], ["name", "price"])
df.write.format("opensearch") \
    .option("opensearch.nodes", "https://<collection-id>.<region>.aoss.amazonaws.com") \
    .option("opensearch.port", "443") \
    .option("opensearch.nodes.wan.only", "true") \
    .option("opensearch.net.ssl", "true") \
    .option("opensearch.aws.sigv4.enabled", "true") \
    .option("opensearch.aws.sigv4.region", "<region>") \
    .option("opensearch.aws.sigv4.service", "aoss") \
    .save("my-collection")
```

### OpenSearch 3.x との互換性

コネクタは REST API を通じて OpenSearch と通信するため、OpenSearch 3.x でも動作していました。本リリースでは、ビルドおよびテストインフラストラクチャを更新し、OpenSearch 3.x クラスタを正式にサポートしています。

## その他の変更点

本リリースには以下の変更も含まれています。

- レガシーの Spark 2.x モジュールを削除しました。
- AWS 認証レイヤーを AWS SDK v1 から v2 に移行しました。これにより、新しいクレデンシャルプロバイダーのサポートが追加され、AWS SDK v1 のメンテナンス終了タイムラインに対応しています。
- 最小ランタイム JDK を 8 から 11 に、最小ビルド JDK を 21 に引き上げました。
- 各種バグ修正により全体的な安定性が向上しています。変更の全リストは [CHANGELOG](https://github.com/opensearch-project/opensearch-hadoop/blob/main/CHANGELOG.md) を参照してください。

## はじめかた

以下のリソースを使って Hadoop connector 2.0 を始めてみてください。

- ダウンロードは [Maven Central のアーティファクト](https://central.sonatype.com/search?q=org.opensearch.client%20opensearch-spark)から入手できます。
- 使用例と設定オプションは [Hadoop connector のドキュメント](https://docs.opensearch.org/latest/clients/hadoop/)を参照してください。
- プロジェクトの詳細は [Hadoop connector リポジトリ](https://github.com/opensearch-project/opensearch-hadoop)を参照してください。

本リリースに関するフィードバックをお待ちしています。質問や提案がありましたら、[コミュニティフォーラム](https://forum.opensearch.org/)にアクセスするか、[GitHub](https://github.com/opensearch-project/opensearch-hadoop/issues) で Issue を作成してください。
