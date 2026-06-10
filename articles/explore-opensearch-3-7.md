---
title: "[翻訳] OpenSearch 3.7 リリース紹介"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "observability", "prometheus", "vectorsearch", "security"]
publication_name: "opensearch"
published: true
published_at: 2026-06-09
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/explore-opensearch-3-7/

### オブザーバビリティシグナルの統合、可視化の効率化、AI アプリケーション向けベクトル検索の高速化

[OpenSearch 3.7](https://opensearch.org/downloads/) では、より速くシステムを構築、発見、提供するための新しいツール群が提供されます。オブザーバビリティチームは、ネイティブ Prometheus 統合によるデータソースへの統一アクセスで、探索を効率化し、成果に至る時間を短縮できます。検索分野では、Search Relevance Workbench でのレレバンスチューニングがより簡単かつ強力になり、AI アプリケーションは大幅に高いスループットでベクトルを取得できるようになりました。新機能には以下が含まれます。

- ログ、トレース、メトリクスを単一のインターフェースでクエリ、アラート、SLO 追跡
- サービス、環境、メトリクスに対応するパラメータ化された単一ダッシュボードの構築と、クエリを再実行せずに結果を整形する機能
- ベクトル取得速度が最大 5.5 倍に向上
- 新しい正規化手法とランキング手法によるハイブリッド検索の最適化
- Index State Management (ISM) ポリシー変更のプレビュー機能

OpenSearch 3.7 の詳細については続きをお読みください。変更点の全リストは[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-3.6.0.md)を参照してください。

## オブザーバビリティとアナリティクス

[オブザーバビリティ](https://docs.opensearch.org/latest/observing-your-data)チームは、ツールの切り替えや、サービス・環境・シグナルタイプごとにほぼ同一の可視化を維持することに多くの時間を費やしています。OpenSearch 3.7 はこれらの問題に対処し、最近リリースされた [OpenSearch Observability Stack](https://opensearch.org/platform/observability-stack/) を活用した単一の運用ビューをテレメトリ全体で提供します。ネイティブ [Prometheus](https://prometheus.io/) サポートにより、既にログやトレースのクエリを行っている同じインターフェースにメトリクスが取り込まれ、完全な PromQL、統合アラート、Service Level Objective (SLO) カタログが利用可能になります。タブや認証コンテキストを切り替えることなく、シグナル間の相関分析が行えます。新しいダッシュボード変数とデータ変換機能により、数十の重複パネルを単一のパラメータ化テンプレートと 1 つのクエリで置き換えることができます。これらの機能は OpenSearch [observability playground](http://observability.playground.opensearch.org) で試すことができます。

### OpenSearch Dashboards から Prometheus メトリクスをネイティブにクエリ

[OpenSearch Dashboards](https://opensearch.org/platform/opensearch-dashboards/) が既存の Prometheus インスタンスにデータソースとして直接接続できるようになりました。データの移行やスタックの変更なしに [PromQL](https://observability.opensearch.org/docs/investigate/#promql) でメトリクスをクエリできます。データソースセレクタを単一の Prometheus サーバー、HA ペア、リージョン間のフェデレーションに向けると、既存のレコーディングルール、アラートルール、Alertmanager のルーティングはそのまま動作し続けます。OpenSearch はプロプライエタリな形式に変換するのではなく PromQL をネイティブにサポートしているため、Dashboards で作成したクエリはポータブルです。レコーディングルール、curl コマンド、PromQL を理解する他のツールにそのままコピーできます。既存の OpenSearch のログ・トレース取り込み機能と組み合わせることで、メトリクスのギャップが埋まり、単一のインターフェース、単一のタイムセレクタ、単一の認証コンテキストで 3 つのシグナルタイプすべてを表示できます。

### Explore Metrics で調査を加速

新しい [Explore Metrics](https://observability.opensearch.org/docs/investigate/discover-metrics/#explore-mode) ビューは、何かがおかしいことは分かっているがまだ何をクエリすべきか分からない場合の出発点を提供します。シグナル対応のデータセットセレクタが Prometheus データソースを自動検出し、メトリクスビルダーでメトリクス名からラベル、集約、関数へとナビゲートしながら、各ステップで有効な PromQL をリアルタイムに生成します。ビルダーと生のクエリエディタは同期を保つため、クリック操作でクエリを形成し、エディタに落として手動で微調整できます。ヒストグラム、instant クエリと range クエリの比較、ラベルのオートコンプリート、ダッシュボード変数のすべてがすぐに利用可能です。「何かがおかしい」状態から的確なクエリに到達するまでの時間を短縮します。[observability playground](https://observability.playground.opensearch.org/w/8xYRJ9/app/explore/metrics/#/?_g=(filters:!(),query:(dataset:(displayName:%27Log%20Dataset%20-%20Local%20Cluster%27,id:%275e9ecdd0-5418-11f1-ba61-c93b4ff6c8ce%27,isRemoteDataset:!f,timeFieldName:time,title:%27logs-otel-v1*%27,type:INDEX_PATTERN),language:kuery,query:%27%27),refreshInterval:(pause:!t,value:0),time:(from:now-5h,to:now))&_q=(dataset:(dataSource:(),id:ObservabilityStack_Prometheus,language:PROMQL,signalType:metrics,timeFieldName:Time,title:ObservabilityStack_Prometheus,type:PROMETHEUS),language:PROMQL,query:%27%27)&_a=(legacy:(columns:!(_source),interval:auto,isDirty:!f,sort:!()),tab:(logs:(),patterns:(usingRegexPatterns:!f)),ui:(activeTabId:logs,showHistogram:!t))) で新しいメトリクスワークスペースを試すことができます。

![Explore Metrics](/images/explore-opensearch-3-7/6527d38a90f4.gif)
*Explore Metrics は Prometheus データソースを自動検出し、メトリクス名からラベル、集約へとナビゲートできます*

### OpenSearch と Prometheus のアラートを 1 つのビューに統合

OpenSearch 3.7 では、OpenSearch モニターと Prometheus アラートルールを単一のインボックスに統合する実験的な[統合アラートビュー](https://docs.opensearch.org/latest/observing-your-data/alerting/unified-alerts-view/)が導入されました。重大度順にソートされ、サービスごとにグループ化されます。Alertmanager のルーティングツリーが読み取り専用で視覚的にレンダリングされ、YAML を grep することなく誰がページングされたか、その理由を確認できます。既存のアラートパイプラインは変更なく動作し続け、Dashboards はそれに読みやすいインターフェースを提供するだけです。オンコールチームにとって、これはインシデント対応中に両方のシステムのアラート状態を確認するための単一の場所を意味します。この機能は [observability playground](http://observability.playground.opensearch.org/app/observability-alerting) の専用ワークスペースで試すことができます。

![統合アラートビュー](/images/explore-opensearch-3-7/284bab89f88e.png)
*統合アラートビューは OpenSearch モニターと Prometheus アラートルールを単一のインボックスに統合し、データソース、重大度、状態によるフィルタリングが可能です*

### エラーバジェット残量優先のランキングで SLO を追跡

3.7 で実験的機能として導入された新しい [SLO カタログ](https://docs.opensearch.org/latest/observing-your-data/slo/index/)は、すべての SLO をエラーバジェットの残量順にランク付けするため、違反に最も近い目標が常に最初に表示されます。各 SLO エントリにはバーンレートアラート、マルチウィンドウ評価、SLO を駆動する基盤メトリクスへの直接リンクが含まれます。ワークフローは次の通りです。バジェットの消費を検知し、メトリクスを確認し、原因を調査して解決策を提供する。これらすべてが同じインターフェース内で完結します。[observability playground](https://observability.playground.opensearch.org/w/8xYRJ9/app/observability-apm-slo#/slos) で試すことができます。

### ダッシュボード変数で再利用可能なテンプレート駆動ダッシュボードを構築

OpenSearch Dashboards が[ダッシュボード変数](https://docs.opensearch.org/latest/dashboards/visualize/visualization-editor/dashboard-variables/index/)をサポートし、サービス・環境・メトリクスごとにほぼ同一のコピーを維持する代わりに、再利用可能なプレースホルダーでダッシュボードをパラメータ化できるようになりました。数十の一回限りの可視化を単一のテンプレートで置き換えることができます。変数を一度定義し、visualization editor のクエリで参照するだけです。変数はクエリがバックエンドに到達する前にテキスト置換で解決されるため、フィールド名、フィルタ値、集約、ディメンションなど、クエリの任意の部分を変更できます。2 つの変数タイプを異なるワークフローに使用します。カスタム変数は単一選択または複数選択動作の固定オプションリストを定義し、クエリ変数はデータからオプションを動的に生成します。変数がクエリ構造を変更するため、単一のテンプレートでサービス、環境、メトリクスの任意の組み合わせに対応できます。

![ダッシュボード変数](/images/explore-opensearch-3-7/949657387d58.png)
*単一のパラメータ化ダッシュボードがヘッダーのドロップダウン変数コントロールを使用してサービスや環境に対応します*

### データ変換でクエリ結果をランタイムで整形

OpenSearch Dashboards の [visualization editor](https://docs.opensearch.org/latest/dashboards/visualize/visualization-editor/) で、クエリを再実行せずにクエリ結果を直接変換できるようになりました。制限、ソート、フィルタ、計算フィールド、集約を含む変換パイプラインを定義し、生の結果を単一のベースクエリから新しい可視化に整形できます。メトリクス分析ワークフローでは、変換が複数の PromQL クエリにまたがって動作し、より豊かな複合ビューを実現します。これにより、ダッシュボード開発が高速化されます。1 つのクエリで多くの可視化を駆動でき、以前はクエリの変更が必要だった調整が完全にプレゼンテーション層で行えるようになります。

## 検索の高度化

OpenSearch 3.7 は、スタック全体で検索速度、レレバンスチューニング、AI 統合を改善します。

### doc values によるベクトル取得が最大 5.5 倍高速化

OpenSearch ベクトルエンジンで、検索リクエスト中に `docvalue_fields` を使用して k-NN ベクトルを取得できるようになりました。以前はベクトルは `_source` フィールドからのみ利用可能で、保存されたドキュメント全体の読み取り、解凍、再構築が必要でした。このオーバーヘッドを回避し、バッチ最近傍検索やリランキングパイプラインなどのワークロードで大幅なパフォーマンス改善が得られます。これはクエリあたり多くのベクトルを返すワークロードで特に重要です。768 次元ベクトルの場合、k=1000 で標準の `_source` 取得と比較して最大 5.5 倍のエンドツーエンド検索レイテンシの改善、k=100 で最大 2.5 倍の改善を実現します。この機能は Lucene および Faiss k-NN エンジンのすべての圧縮レベルで動作し、再インデックスは不要です。ベクトルはスループットを最大化するためにデフォルトでバイナリ形式で返されますが、JSON 配列も利用可能です。詳細は[ドキュメント](https://docs.opensearch.org/latest/vector-search/performance-tuning-search/#retrieve-vectors-using-doc-values)を参照してください。

### Search Relevance Workbench で UI から判定セットを直接アップロード

[Search Relevance Workbench](https://docs.opensearch.org/latest/search-plugins/search-relevance/using-search-relevance-workbench/) では、以前はレレバンス判定をインポートするために API 呼び出しが必要でした。これは REST エンドポイントに慣れていないプロダクトマネージャーや検索アナリストにとって障壁でした。標準形式(クエリ、ドキュメント ID、評価の CSV)の判定ファイルを、クエリセットをアップロードするのと同じ方法で OpenSearch Dashboards から直接アップロードできるようになりました。最大 10,000 行(10 判定で 1,000 クエリ分)をサポートし、Quepid などのツールからエクスポートした評価を取り込み、コードを一行も書かずに実験ですぐに使用できます。

### z_score と Reciprocal Rank Fusion でハイブリッド検索の最適化を拡張

[Search Relevance Workbench](https://docs.opensearch.org/latest/search-plugins/search-relevance/using-search-relevance-workbench/) のハイブリッドオプティマイザが、z_score 正規化と Reciprocal Rank Fusion (RRF) の 2 つの追加手法を評価するようになりました。以前はオプティマイザはクエリあたり 66 バリアント(`min_max` と `l2` 正規化、3 つの平均ベース結合方法、11 のウェイトポイントの組み合わせ)をテストしていました。拡張されたマトリクスは `z_score` と `arithmetic_mean` のペア(z_score が負の値を生成するため、唯一数学的に有効な組み合わせ)と、経験的に選択された 5 つの `rank_constant` 値による RRF を追加し、クエリあたり合計 82 バリアントになりました。`rank_constant` リスト `({1, 5, 10, 20, 60})` は 100K ドキュメントコーパスで 15 候補をスキャンし、検索等価性でグループ化して選択されました。40 以上の値はすべて同一の top-10 結果を生成するため、単一の代表値(業界標準の k=60)でそのプラトー全体をカバーします。また、フルスイープの代わりに実験ごとに特定の手法を選択することもでき、RRF チューニングのみに焦点を当てるチームはその 5 バリアントのみをリクエストしてより速く結果を得られます。

### ML コネクタに予測時に動的ヘッダーを渡す

外部モデルサービスと統合する ML コネクタが、リクエストごとの[動的ヘッダー](https://docs.opensearch.org/latest/ml-commons-plugin/remote-models/connectors/#configuring-dynamic-headers)をサポートするようになりました。以前はコネクタヘッダーは作成時に一度だけ解決されるため、トレース ID やデバッグフラグなどの一意のメタデータを個々の `_predict` リクエストに添付する方法がありませんでした。コネクタヘッダーで `${parameters.*}` プレースホルダー置換を使用して、各 `_predict` 呼び出しにランタイム値を渡すことができ、数百から数千のモデル呼び出しにわたる本番グレードのリクエスト追跡が可能になります。セキュリティ検証により、認証関連ヘッダーへの `${parameters.*}` はクレデンシャルインジェクションを防ぐためにブロックされます。

### セマンティック検索とハイブリッド検索のエンドポイント簡素化でエージェントの長期記憶にアクセス

[エージェントメモリ](https://docs.opensearch.org/latest/ml-commons-plugin/agentic-memory/)に専用の `_semantic_search` と `_hybrid_search` エンドポイントが追加されました。プレーンテキストクエリを受け付け、メモリコンテナに設定されたモデルを使用して自動的にエンベディングを生成します。以前は長期記憶の検索には、手動でのエンベディング生成、複雑な k-NN クエリの構築、キーワード検索とベクトル検索の組み合わせが必要でした。セマンティック検索はニューラルエンベディングを使用して、正確なキーワードが一致しない場合でもコンテキスト的に関連する記憶を取得し、ハイブリッド検索は BM25 キーワードスコアリングとベクトル類似度を設定可能な重みで組み合わせて精度と再現率のバランスを取ります。組み込みのネームスペース、タグ、フィルタサポートにより、カスタム DSL クエリなしでエージェントが正しいメモリスライスを取得でき、正確なコンテキスト想起に依存する RAG パターンやマルチターン推論ワークフローを加速します。

### エージェントの一括登録とマルチモーダル入力による会話が本番対応に

最近のリリースで実験的に導入された[統合エージェント登録](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/agents/index/#unified-registration-method) API と `conversational_v2` [エージェントタイプ](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/agents/conversational/)が、GA (一般提供) となり本番環境で利用可能になりました。統合登録 API は、コネクタ作成、モデル登録、エージェント設定、パラメータマッピングの 4 ステップのエージェントセットアップを、シンプルなモデルブロックで駆動される単一の API 呼び出しに集約し、コネクタとモデルリソースを自動生成します。`conversational_v2` エージェントタイプは、プレーンテキスト、マルチモーダルコンテンツブロック(画像、動画、ドキュメント)、完全なメッセージベースの会話履歴をサポートする標準化された入力インターフェースを提供し、カスタムコネクタ設定は不要です。レスポンスは停止理由、アシスタントメッセージ、メモリセッション ID、トークン使用量メトリクスを含む一貫した出力形式に従います。この標準は今後のリリースで他のエージェントタイプにも拡張される予定です。

## スケーラビリティとレジリエンシー

OpenSearch 3.7 は、より安全なポリシー管理、より深いクエリ診断、よりきめ細かいワークロード制御を追加します。

### ISM ポリシーを適用前にドライラン

OpenSearch 3.7 は [Index State Management](https://docs.opensearch.org/latest/im-plugin/ism/index/) (ISM) の Simulate API を追加しました。ポリシーがインデックスに与える影響を、クラスタ状態を変更せずにプレビューできます。`POST /_plugins/_ism/simulate` を保存済みポリシー ID またはインラインポリシー本体とターゲットインデックスのリストで呼び出すと、各インデックスの現在のライフサイクル状態が報告され、すべての遷移条件がライブインデックスメトリクスに対して評価され、次にどの状態に移行するかが示されます。ISM ポリシーにはインデックスの削除などの不可逆なアクションが含まれる可能性があるため、ポリシー適用前に条件と状態遷移を検証することで、遷移が期待通りに進むことを確認できます。Simulate API はワイルドカードインデックスパターンをサポートし、管理対象と非管理対象の両方のインデックスで動作し、インラインポリシー本体も受け付けるため、保存前にポリシーを検証できます。

### Query Insights から低速クエリを直接プロファイル

[Query Insights](https://docs.opensearch.org/latest/observing-your-data/query-insights/index/) はレイテンシ、CPU、メモリ順にランク付けされた最も遅いクエリを表示しますが、これまでクエリが遅い理由を調査するには Profile API に切り替えて結果を手動で相関付ける必要がありました。OpenSearch 3.7 は OpenSearch Dashboards Dev Tools にクエリプロファイラツールを追加します。このツールは分割ペインエディタを提供し、左側にクエリを入力すると右側に完全なプロファイリングの内訳が表示されます。色分けされた実行タイミング、ページネーション付きのシャードレベルパフォーマンス詳細、折りたたみ可能なクエリ階層が含まれ、保存済みクエリのインポートや結果のエクスポートも可能です。さらに重要なのは、Query Details ページに **Open in Profiler** オプションが追加され、クエリを事前に読み込んでワンクリックでプロファイラを起動できることです。低速クエリの発見から実行内訳の検査までの完全なワークフローが OpenSearch Dashboards 内で完結します。

### Workload Management にグループごとの検索設定を追加

OpenSearch [Workload Management](https://docs.opensearch.org/latest/tuning-your-cluster/availability-and-recovery/workload-management/wlm-feature-overview/) (WLM) がグループごとの設定オーバーライドをサポートするようになりました。以前は多くの検索設定がクラスタレベルまたはリクエストごとにのみ設定可能でした。WLM グループにより、クラスタ管理者は検索タイムアウト、キャンセル間隔、最大バケット数などの設定をグループごとに制御できます。制限はグループにルーティングされるすべてのリクエストに自動的に適用されます。マルチテナントドメインにおいて、テナントごとのきめ細かい制御と、過度に許容的なリクエストパラメータからの保護を提供します。

## セキュリティとインフラストラクチャ

OpenSearch 3.7 は、スコープ付きのクレデンシャルレベル権限によりアクセス制御を強化します。

### API キーにセキュリティ権限を直接スコープ

OpenSearch 3.7 は [API キー](https://docs.opensearch.org/latest/api-reference/security/api-keys/create/)を導入しました。クラスタ権限とインデックス権限をキーに直接関連付けます。ユーザーのロールからアクセスを導出する既存の認証方法とは異なり、API キーはセキュリティ管理者がキーに実際に必要な権限のみを持つスコープ付きの長寿命クレデンシャルを発行できます。キーを作成し、許可するアクションとインデックスパターンを指定すると、発行元管理者のロールセットに依存せずに最小権限を適用する不透明なクレデンシャルを受け取ります。キーは設定可能な有効期限、クラスタ全体での同期的な無効化、自動的なシステムインデックス保護をサポートします。これにより、データのインデックス作成やクエリの実行を行うサービス間通信や CI/CD パイプラインに適しています。

## はじめに

OpenSearch 3.7 は現在、[さまざまなディストリビューション](https://opensearch.org/downloads/)で利用可能で、[OpenSearch Playground](https://playground.opensearch.org/app/home#/) で試すことができます。詳細は[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-3.7.0.md)、[ドキュメントリリースノート](https://github.com/opensearch-project/documentation-website/blob/main/release-notes/opensearch-documentation-release-notes-3.7.0.md)、更新された[ドキュメント](https://docs.opensearch.org/latest/)を参照してください。フィードバックは[コミュニティフォーラム](https://forum.opensearch.org/)やプロジェクトの [Slack](https://www.opensearch.org/slack.html) でお寄せください。
