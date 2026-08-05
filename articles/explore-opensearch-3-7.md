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

### 可観測性シグナルの統合、可視化の効率化、AI アプリケーション向けベクトル検索の高速化

[OpenSearch 3.7](https://opensearch.org/downloads/) は、構築・発見・提供を加速する多数の新しいツールを搭載しています。可観測性の領域では、ネイティブ Prometheus 統合によってデータソースに統一的にアクセスでき、探索の効率化と調査時間の短縮が見込めます。検索の領域では、Search Relevance Workbench によるレレバンスチューニングがより簡単かつ強力になり、AI アプリケーションは大幅に高いスループットでベクトルを取得できるようになりました。主な新機能は以下の通りです。

- ログ、トレース、メトリクスを単一インターフェースでクエリ・アラート・SLO 追跡
- サービスや環境、メトリクスに対応するパラメータ化ダッシュボードの構築。クエリの再実行なしに結果を整形可能
- ベクトル取得が最大 5.5 倍高速化
- 新しい正規化手法とランキング手法によるハイブリッド検索の最適化
- Index State Management (ISM) ポリシー変更のプレビュー

以下で各機能を詳しく紹介します。変更点の全リストは[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-3.7.0.md)を参照してください。

## 可観測性とアナリティクス

[可観測性](https://docs.opensearch.org/latest/observing-your-data)に取り組むチームは、ツール間の切り替えや、サービス・環境・シグナルタイプごとにほぼ同じ可視化の面倒をみることに時間を取られがちです。OpenSearch 3.7 はこの問題に正面から取り組み、最近リリースされた [OpenSearch Observability Stack](https://opensearch.org/platform/observability-stack/) によるテレメトリ横断の統合運用ビューを実現しました。ネイティブ [Prometheus](https://prometheus.io/) サポートにより、ログやトレースを既にクエリしている同じ画面にメトリクスが加わります。PromQL の完全サポート、統合アラート、SLO カタログが揃い、タブや認証コンテキストを切り替えずにシグナル間の相関分析ができます。新しいダッシュボード変数とデータ変換機能を使えば、重複する数十のパネルを 1 つのパラメータ化テンプレートと 1 本のクエリに集約できます。これらの機能は OpenSearch [observability playground](http://observability.playground.opensearch.org) で今すぐ試せます。

### OpenSearch Dashboards から Prometheus メトリクスをネイティブにクエリ

[OpenSearch Dashboards](https://opensearch.org/platform/opensearch-dashboards/) が既存の Prometheus インスタンスにデータソースとして直接接続できるようになりました。データ移行もスタック変更も不要で、[PromQL](https://observability.opensearch.org/docs/investigate/#promql) によるメトリクスクエリが可能です。データソースセレクタを Prometheus サーバー、HA ペア、リージョン間フェデレーションに向けるだけで、既存のレコーディングルール、アラートルール、Alertmanager のルーティングはそのまま動作し続けます。OpenSearch は PromQL をプロプライエタリ形式に変換するのではなくネイティブにサポートしているため、Dashboards で書いたクエリはそのままレコーディングルールや curl コマンド、他の PromQL 対応ツールにコピーできます。既存のログ・トレース取り込みと合わせて、1 つのインターフェース、1 つのタイムセレクタ、1 つの認証コンテキストで 3 種類のシグナルすべてを扱えるようになります。

### Explore Metrics で調査を加速

新しい [Explore Metrics](https://observability.opensearch.org/docs/investigate/discover-metrics/#explore-mode) ビューは、「何かおかしいがまだ何をクエリすべきか分からない」という状況の出発点になります。シグナル対応のデータセットセレクタが Prometheus データソースを自動検出し、メトリクスビルダーでメトリクス名 → ラベル → 集約 → 関数と進みながら、各ステップで有効な PromQL をリアルタイムに生成します。ビルダーと生のクエリエディタは常に同期しているので、クリック操作でクエリを形作り、エディタ側で手動微調整もできます。ヒストグラム、instant/range クエリの比較、ラベルのオートコンプリート、ダッシュボード変数もすぐ使えます。[observability playground](https://observability.playground.opensearch.org/w/8xYRJ9/app/explore/metrics/#/?_g=(filters:!(),query:(dataset:(displayName:%27Log%20Dataset%20-%20Local%20Cluster%27,id:%275e9ecdd0-5418-11f1-ba61-c93b4ff6c8ce%27,isRemoteDataset:!f,timeFieldName:time,title:%27logs-otel-v1*%27,type:INDEX_PATTERN),language:kuery,query:%27%27),refreshInterval:(pause:!t,value:0),time:(from:now-5h,to:now))&_q=(dataset:(dataSource:(),id:ObservabilityStack_Prometheus,language:PROMQL,signalType:metrics,timeFieldName:Time,title:ObservabilityStack_Prometheus,type:PROMETHEUS),language:PROMQL,query:%27%27)&_a=(legacy:(columns:!(_source),interval:auto,isDirty:!f,sort:!()),tab:(logs:(),patterns:(usingRegexPatterns:!f)),ui:(activeTabId:logs,showHistogram:!t))) で試すことができます。

![Explore Metrics](/images/explore-opensearch-3-7/6527d38a90f4.gif)
*Explore Metrics は Prometheus データソースを自動検出し、メトリクス名からラベル、集約へとナビゲートできる*

### OpenSearch と Prometheus のアラートを 1 つのビューに統合

OpenSearch 3.7 では、OpenSearch モニターと Prometheus アラートルールを 1 つのインボックスにまとめる実験的な[統合アラートビュー](https://docs.opensearch.org/latest/observing-your-data/alerting/unified-alerts-view/)が加わりました。重大度順にソートされ、サービス別にグループ化されます。Alertmanager のルーティングツリーが読み取り専用で視覚的に表示されるので、YAML を grep しなくても誰がページングされたか、その理由が一目で分かります。既存のアラートパイプラインはそのまま動き続け、Dashboards が読みやすいインターフェースを被せているだけです。オンコール担当にとっては、インシデント対応中にツールを行き来せず 1 か所でアラート状態を把握できます。[observability playground](http://observability.playground.opensearch.org/app/observability-alerting) の専用ワークスペースで試すことができます。

![統合アラートビュー](/images/explore-opensearch-3-7/284bab89f88e.png)
*統合アラートビューは OpenSearch モニターと Prometheus アラートルールを 1 つのインボックスに統合し、データソース・重大度・状態でフィルタできる*

### エラーバジェット残量優先で SLO を追跡

3.7 で実験的に導入された [SLO カタログ](https://docs.opensearch.org/latest/observing-your-data/slo/index/)は、すべての SLO をエラーバジェットの残量順にランク付けします。違反に最も近い目標が常に先頭に来るため、注意を向けるべき対象が明確です。各 SLO エントリにはバーンレートアラート、マルチウィンドウ評価、基盤メトリクスへの直接リンクが含まれます。バジェット消費の検知 → メトリクス確認 → 原因調査 → 解決策提供まで、同じインターフェースで完結します。[observability playground](https://observability.playground.opensearch.org/w/8xYRJ9/app/observability-apm-slo#/slos) で試せます。

### ダッシュボード変数で再利用可能なテンプレートを構築

OpenSearch Dashboards に[ダッシュボード変数](https://docs.opensearch.org/latest/dashboards/visualize/visualization-editor/dashboard-variables/index/)が追加されました。サービスや環境、メトリクスごとにほぼ同じダッシュボードのコピーを維持する代わりに、再利用可能なプレースホルダーでパラメータ化できます。変数を一度定義して visualization editor のクエリで参照するだけで、数十の可視化を 1 枚のテンプレートに集約できます。変数はバックエンドへのクエリ送信前にテキスト置換されるため、フィールド名、フィルタ値、集約、ディメンションなどクエリの任意の部分を動的に切り替えられます。カスタム変数(固定オプションリスト、単一/複数選択)とクエリ変数(データから動的にオプション生成)の 2 タイプがあり、1 つのテンプレートでサービス・環境・メトリクスの任意の組み合わせに対応可能です。

![ダッシュボード変数](/images/explore-opensearch-3-7/949657387d58.png)
*ヘッダーのドロップダウンで変数を切り替えるだけで、1 つのダッシュボードがサービスや環境に適応する*

### データ変換でクエリ結果をその場で加工

OpenSearch Dashboards の [visualization editor](https://docs.opensearch.org/latest/dashboards/visualize/visualization-editor/) で、クエリを再実行せずに結果を直接変換できるようになりました。制限、ソート、フィルタ、計算フィールド、集約からなる変換パイプラインを定義すれば、1 本のベースクエリから複数の可視化を作り出せます。メトリクス分析では複数の PromQL クエリ結果をまたいだ変換もでき、複合ビューの構築が容易になります。以前はクエリ変更が必要だった調整が、プレゼンテーション層だけで完結します。

## 検索の高度化

OpenSearch 3.7 は、検索速度、レレバンスチューニング、AI 連携をスタック全体で底上げします。

### doc values でベクトル取得が最大 5.5 倍に

OpenSearch ベクトルエンジンで、検索リクエスト中に `docvalue_fields` を使って k-NN ベクトルを取得できるようになりました。従来は `_source` フィールド経由でしかベクトルを取得できず、ドキュメント全体の読み取り・展開・再構築が必要でした。このオーバーヘッドが不要になり、バッチ最近傍検索やリランキングパイプラインなど、クエリあたり多くのベクトルを返すワークロードで大きな恩恵があります。768 次元ベクトルで計測した場合、k=1000 で従来の `_source` 取得比で最大 5.5 倍、k=100 で最大 2.5 倍のレイテンシ改善です。Lucene/Faiss 両エンジンのすべての圧縮レベルで動作し、再インデックスは不要です。ベクトルはデフォルトでバイナリ形式(最大スループット向け)で返されますが、JSON 配列形式も選べます。詳細は[ドキュメント](https://docs.opensearch.org/latest/vector-search/performance-tuning-search/#retrieve-vectors-using-doc-values)を参照してください。

### Search Relevance Workbench で判定セットを UI から直接アップロード

[Search Relevance Workbench](https://docs.opensearch.org/latest/search-plugins/search-relevance/using-search-relevance-workbench/) でレレバンス判定をインポートするには、これまで API 呼び出しが必要でした。REST エンドポイントに慣れていないプロダクトマネージャーや検索アナリストには障壁です。今回、標準形式(クエリ、ドキュメント ID、評価の CSV)の判定ファイルを OpenSearch Dashboards から直接アップロードできるようになりました。最大 10,000 行(10 判定 x 1,000 クエリ)に対応しており、Quepid などのツールからエクスポートした評価をコードなしですぐ実験に使えます。

### z_score と RRF でハイブリッド検索の最適化を拡張

[Search Relevance Workbench](https://docs.opensearch.org/latest/search-plugins/search-relevance/using-search-relevance-workbench/) のハイブリッドオプティマイザが、z_score 正規化と Reciprocal Rank Fusion (RRF) を新たに評価対象に加えました。従来はクエリあたり 66 バリアント(`min_max`/`l2` 正規化、3 種の平均ベース結合、11 ウェイトポイントの組み合わせ)でしたが、`z_score` + `arithmetic_mean` のペア(z_score は負値を生成するため唯一有効な組み合わせ)と、経験的に選んだ 5 つの `rank_constant` 値 `({1, 5, 10, 20, 60})` による RRF が加わり、合計 82 バリアントになりました。この定数リストは 100K ドキュメントのコーパスで 15 候補を試し、同じ検索結果を返すもの同士でグループ化して絞り込んだものです。40 以上の値はいずれも同一の top-10 を返すため、業界標準の k=60 で代表しています。フルスイープではなく特定手法のみを実験に指定することもでき、RRF だけ試したいチームは 5 バリアントのみのリクエストで済みます。

### ML コネクタで予測時に動的ヘッダーを送信

外部モデルサービスと統合する ML コネクタが、リクエストごとの[動的ヘッダー](https://docs.opensearch.org/latest/ml-commons-plugin/remote-models/connectors/#configuring-dynamic-headers)に対応しました。従来はヘッダーが作成時に固定されるため、トレース ID やデバッグフラグなどを個々の `_predict` リクエストに付与できませんでした。コネクタヘッダーで `${parameters.*}` プレースホルダーを使うことで、呼び出しごとにランタイム値を渡せるようになり、数百〜数千のモデル呼び出しを横断してリクエストを追跡できます。認証関連ヘッダーへの `${parameters.*}` はクレデンシャルインジェクション防止のためブロックされます。

### エージェントの長期記憶に簡易なセマンティック/ハイブリッド検索でアクセス

[エージェントメモリ](https://docs.opensearch.org/latest/ml-commons-plugin/agentic-memory/)に `_semantic_search` と `_hybrid_search` の専用エンドポイントが追加されました。プレーンテキストのクエリを受け取り、メモリコンテナに設定済みのモデルで自動的にエンベディングを生成します。従来は長期記憶の検索に、手動でのエンベディング生成、複雑な k-NN クエリの構築、キーワード検索とベクトル検索の手動組み合わせが必要でした。セマンティック検索はニューラルエンベディングによりキーワードが一致しなくても関連する記憶を取得でき、ハイブリッド検索は BM25 スコアとベクトル類似度を設定可能な重みで組み合わせます。ネームスペース、タグ、フィルタの組み込みサポートにより、カスタム DSL を書かずに正しいメモリスライスを取得でき、RAG パターンやマルチターン推論のワークフローが加速します。

### エージェントの一括登録とマルチモーダル会話が GA に

最近のリリースで実験的に導入された[統合エージェント登録](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/agents/index/#unified-registration-method) API と `conversational_v2` [エージェントタイプ](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/agents/conversational/)が GA となり、本番利用が可能になりました。統合登録 API は、コネクタ作成 → モデル登録 → エージェント設定 → パラメータマッピングという 4 ステップを、シンプルなモデルブロック 1 つの API 呼び出しに集約します。コネクタとモデルのリソースは自動生成されます。`conversational_v2` エージェントタイプは、テキスト、マルチモーダルコンテンツ(画像・動画・ドキュメント)、メッセージベースの会話履歴を統一インターフェースで受け付け、カスタムコネクタ設定は不要です。レスポンスには停止理由、アシスタントメッセージ、メモリセッション ID、トークン使用量が含まれ、一貫した出力形式を提供します。

## スケーラビリティとレジリエンシー

OpenSearch 3.7 では、ポリシー管理をより安全に、クエリ診断をより深く、ワークロード制御をより細かく行えるようになりました。

### ISM ポリシーを適用前にドライラン

[Index State Management](https://docs.opensearch.org/latest/im-plugin/ism/index/) (ISM) に Simulate API が追加されました。ポリシーがインデックスに与える影響を、クラスタ状態を一切変更せずにプレビューできます。`POST /_plugins/_ism/simulate` に保存済みポリシー ID またはインラインのポリシー本体とターゲットインデックスを渡すと、各インデックスの現在のライフサイクル状態の報告、すべての遷移条件のライブ評価、次の遷移先の提示が返ります。ISM ポリシーにはインデックス削除のような不可逆アクションが含まれ得るため、事前検証によって意図しない遷移を防げます。ワイルドカードパターン、管理/非管理インデックスの両方、インラインポリシーに対応しており、保存前の検証にも使えます。

### Query Insights から遅いクエリを直接プロファイル

[Query Insights](https://docs.opensearch.org/latest/observing-your-data/query-insights/index/) はレイテンシ・CPU・メモリ順で遅いクエリを一覧表示しますが、なぜ遅いのかを調べるには Profile API に切り替えて手動で突き合わせる必要がありました。OpenSearch 3.7 では Dashboards の Dev Tools にクエリプロファイラが追加されます。分割ペインエディタの左にクエリを入力すると、右側にプロファイリング結果が表示されます。色分けされた実行タイミング、シャード別の詳細、折りたたみ可能なクエリ階層を備え、保存済みクエリのインポートや結果エクスポートにも対応します。加えて Query Details ページに **Open in Profiler** オプションが加わり、ワンクリックでクエリをプロファイラに読み込めます。遅いクエリの発見から実行内訳の確認まで、Dashboards 内で完結するようになりました。

### Workload Management でグループ単位の検索設定が可能に

OpenSearch [Workload Management](https://docs.opensearch.org/latest/tuning-your-cluster/availability-and-recovery/workload-management/wlm-feature-overview/) (WLM) でグループごとの設定オーバーライドが可能になりました。従来は検索タイムアウトや最大バケット数などの設定はクラスタレベルかリクエスト単位でしか指定できませんでした。WLM グループを使えば、クラスタ管理者がグループ単位でこれらを制御でき、ルーティングされたリクエストに自動適用されます。マルチテナント環境ではテナントごとに細かく制御でき、過度に緩いリクエストパラメータからクラスタを守れます。

## セキュリティとインフラストラクチャ

OpenSearch 3.7 は、キー単位で権限を絞れる仕組みを導入し、アクセス制御を強化します。

### API キーに直接権限をスコープ

OpenSearch 3.7 で [API キー](https://docs.opensearch.org/latest/api-reference/security/api-keys/create/)が導入されました。クラスタ権限とインデックス権限をキーに直接紐づけます。既存の認証方式ではユーザーのロールからアクセス権が導出されますが、API キーならキーが実際に必要とする権限だけに絞った、期限付きのクレデンシャルを発行できます。キー作成時に許可するアクションとインデックスパターンを指定すれば、発行者のロールに依存しない最小権限のキーが得られます。有効期限の設定、クラスタ全体での即時無効化、システムインデックスの自動保護に対応しており、サービス間通信や CI/CD パイプラインに適しています。

## 入手方法

OpenSearch 3.7 は[各種ディストリビューション](https://opensearch.org/downloads/)で入手可能で、[OpenSearch Playground](https://playground.opensearch.org/app/home#/) でも試せます。詳細は[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-3.7.0.md)、[ドキュメントリリースノート](https://github.com/opensearch-project/documentation-website/blob/main/release-notes/opensearch-documentation-release-notes-3.7.0.md)、[ドキュメント](https://docs.opensearch.org/latest/)を参照してください。フィードバックは[コミュニティフォーラム](https://forum.opensearch.org/)やプロジェクトの [Slack](https://www.opensearch.org/slack.html) でお待ちしています。
