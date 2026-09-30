---
title: "[翻訳] OpenSearch 3.9 リリース紹介"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "observability", "prometheus", "vectorsearch", "security"]
publication_name: "opensearch"
published: true
published_at: 2026-09-29
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/get-to-know-opensearch-3-9/

## ベクトル検索の高速化、オブザーバビリティの拡充、大規模クラスタの保護

OpenSearch 3.9 は、検索・オブザーバビリティ・クラスタの耐障害性の各領域でプロジェクトを前進させます。特に、ベクトル検索の効率化、オブザーバビリティとアプリケーションモニタリングの体験拡張、ワークロード効率を高める新機能に力を入れました。主な新機能は以下の通りです。

- 新しいネイティブエンジンによるニューラルスパース近似最近傍 (ANN) 検索の高速化。スループット向上、インデックス構築の高速化、ヒープ使用量の削減を実現
- ネイティブ 16-bit の `half_float` 型、`bf16` スカラー量子化エンコーダー、2-bit / 4-bit スカラー量子化の追加によるベクトルストレージと圧縮の拡張
- 動的マッピングによる、明示的なマッピング定義なしでのベクトルフィールドのインデックス作成
- 複数データソースにまたがるアラート・異常・予測を一元ビューでトリアージ
- OpenSearch Observability Stack によるアプリケーションパフォーマンス調査の高速化。刷新されたトレース詳細画面、再利用可能な Prometheus Query Language (PromQL) ダッシュボード、ノーコードのアラートルール、ガイド付き APM (Application Performance Monitoring) セットアップウィザード、Piped Processing Language (PPL) クエリプロファイリングを追加
- アクション単位のアダプティブ同時実行数制限とインデックスレベル検索プルーニングによるクラスタ保護
- リソース共有・アクセス制御フレームワークの一般提供 (GA) 開始

OpenSearch 3.9 は[ダウンロード可能](https://opensearch.org/downloads/)です。以下で新機能を詳しく紹介します。変更点の全リストは[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-3.9.0.md)を参照してください。

## 検索の高度化

AI 駆動の検索アプリケーションには、効率的なベクトルストレージ、摩擦の少ないオンボーディング、高速な実行が求められます。OpenSearch 3.9 はこの 3 点すべてを前進させました。ニューラルスパース検索向けの新しいネイティブエンジン、より幅広いベクトルストレージと圧縮の選択肢、そしてマッピングを事前に定義しなくてもベクトルをインデックスできる動的マッピングです。

### ニューラルスパースベクトル検索を高速・軽量な新ネイティブエンジンで実行

OpenSearch 3.9 は、ニューラルスパース ANN 検索を Java 仮想マシン (JVM) から専用の C++ エンジンに移し、クエリ実行の高速化、インデックス構築の高速化、ヒープ使用量の大幅な削減を実現しました。新エンジンはオープンソースの C++ ライブラリで SEISMIC アルゴリズムを動作させ、Neural Search プラグインは Java Native Interface (JNI) を介してこれを呼び出します。これは k-NN プラグインが Faiss で採用しているのと同じ統合パターンです。クエリ実行時にはインデックスデータを Java ヒープに保持せずメモリマップするため、OS がページキャッシュを介してメモリの滞在を管理でき、メモリ逼迫時にはアプリケーションレベルの追い出し処理を挟まずに回収できます。880 万ドキュメントのコーパスでのテストでは、ネイティブエンジンはスループット 39% 向上、インデックス構築 3.3 倍の高速化、JVM ヒープ使用量 1/8 という結果になりました。ネイティブエンジンを使うには、既存の SEISMIC method 設定と併せて `sparse_vector` フィールドマッピングに `"engine": "native"` を指定します。デフォルトは引き続き Lucene エンジンです。詳細は [Native engine](https://docs.opensearch.org/latest/vector-search/ai-search/neural-sparse-ann/#native-engine) を参照してください。

### マッピング定義なしでベクトルデータをインデックス

OpenSearch 3.9 では、`knn_vector` フィールド向けの動的マッピングがオプトインで導入されました。これにより、ベクトルデータをインデックスする前に明示的なフィールドマッピングを定義する必要がなくなります。動的マッピングには相補的な 2 つの機能があります。

- **動的テンプレート**: `match_mapping_type: "knn_vector"` を指定した動的テンプレートで、ベクトル値を持つ未マッピングフィールドにマッチし、最初のドキュメントから次元数を推論します
- **自動推論**: 設定不要のモードで、条件を満たす数値配列を自動的にベクトルフィールドとして認識します

どちらの機能も、任意のマッパープラグインが実装して動的マッピングに参加できる新しい汎用の SPI (Service Provider Interface) の上に構築されています。明示的なマッピングが常に優先され、フィールドに最初にインデックスされたドキュメントがそのフィールドの次元数を決定します。詳細は[動的マッピング](https://docs.opensearch.org/latest/mappings/supported-field-types/knn-vector/#dynamic-mapping)のドキュメントを参照してください。

### ネイティブ half-float ベクトルでベクトルメモリを半分に

OpenSearch 3.9 では、k-NN ベクトルを 16-bit 浮動小数点 (FP16) 形式でネイティブに保存する `half_float` ベクトルデータ型が追加されました。各次元が 4 バイトではなく 2 バイトを占めるため、`half_float` で構築したインデックスは同等の `float` インデックスと比べてメモリとストレージの使用量が約半分になり、大規模ベクトルワークロードでコスト削減とキャッシュ効率の向上につながります。このデータ型は Faiss / Lucene の両エンジンで利用可能で、flat と HNSW (Hierarchical Navigable Small World) のインデックス構造をサポートするため、エンジンや method を変更せずに半精度ストレージを利用できます。詳細は [Half-float vectors](https://docs.opensearch.org/latest/mappings/supported-field-types/knn-memory-optimized/#half-float-vectors) を参照してください。

### bfloat16 量子化でフルレンジのベクトルを保存

OpenSearch 3.9 では、Faiss スカラー量子化に `bf16` エンコーダーが追加され、既存の `fp16` エンコーダーに続く 2 つ目の 16-bit ストレージオプションとして利用できます。bfloat16 形式は 32-bit float と同じ 8 ビットの指数部を持つため、浮動小数点の全表現範囲をカバーでき、`fp16` で必要になる範囲外値の拒否やクリッピングなしで任意の有限値をインデックスできます。どちらのエンコーダーも次元あたり 2 バイトを使用しメモリ削減効果は同程度ですが、`bf16` は精度をわずかに犠牲にして表現範囲を広げているため、データセットによっては recall がやや大きく低下する可能性があります。Intel Sapphire Rapids 以降のプロセッサでは、AVX-512 BF16 命令を用いて距離計算を高速化します。詳細は[ドキュメント](https://docs.opensearch.org/latest/vector-search/optimizing-storage/faiss-scalar-quantization/#the-bf16-encoder)を参照してください。

### 2-bit / 4-bit スカラー量子化でベクトル圧縮率を調整

OpenSearch 3.9 では、ベクトル検索向けスカラー量子化を既存の 1-bit (`32x`) エンコーディングに加えて 2-bit (`16x`) と 4-bit (`8x`) エンコーディングまで拡張しました。圧縮率と recall のバランスを取る際の選択肢が増えます。3 つのレベルはいずれも、Faiss / Lucene 両エンジンの HNSW と flat インデックスタイプで利用できます。エンコーダー設定で量子化レベルを明示的に指定するか、`on_disk` モードの `compression_level` パラメータで暗黙的に指定できるため、インデックス構造を変更せずに異なるトレードオフを評価できます。新しい `half_float` データ型と `bf16` エンコーダーと合わせて、今回のリリースだけでベクトルワークロード向けのストレージと recall の選択肢が大きく広がりました。詳細は [1-bit, 2-bit, and 4-bit quantization](https://docs.opensearch.org/latest/vector-search/optimizing-storage/faiss-scalar-quantization/#1-bit-2-bit-and-4-bit-quantization) を参照してください。

### missing_as_zero フラグで XGBoost のランキング挙動を維持

OpenSearch 3.9 では、Learning to Rank プラグインに、モデル単位でオプトイン設定できる `missing_as_zero` フラグが追加されました。これは、欠損した特徴量を 0 として学習させた XGBoost モデル向けの機能です。以前のリリースで、ネイティブ XGBoost のセマンティクスに合わせて欠損特徴量を `NaN` として渡すようになった結果、こうしたモデルのランキングが変わってしまっていました。新しいフラグを有効にすると欠損特徴量を再び 0 として扱うため、再学習なしで従来のスコアリングを維持できます。デフォルトは無効なので、他のモデルには影響しません。

## オブザーバビリティとアナリティクス

OpenSearch 3.9 では、統合アラートビューに異常検知と予測が加わり、このビューが一般提供 (GA) となりました。ツールを行き来せずに、データソースをまたいでシグナルをトリアージできます。OpenSearch 本体だけでなく、アプリケーション監視向けに OpenTelemetry と Prometheus を基盤として別途デプロイする [OpenSearch Observability Stack](https://opensearch.org/platform/observability-stack/) でも、トレース調査、ダッシュボード、アラート、PPL の各領域で強化が入りました。

### アラート・異常・予測を 1 つの統合ビューでトリアージ

OpenSearch 3.9 では、統合アラートビューに異常検知と予測のリソースが加わり、このビューが GA になりました。OpenSearch のログアラート、Prometheus のメトリクスアラート、異常検知結果を 1 か所でトリアージしながら、アラートルールと一緒に検知器や予測器を管理できます。異常検知の結果は **Alerts** タブに表示され、発生箇所がグループ化されて、詳細情報のフライアウトから確認できます。検知器と予測器は **Rules** タブに表示され、プラグイン間のダッシュボードを切り替えることなく、設定と状態の確認、ライフサイクル管理ができます。詳細は [Unified alerts view](https://docs.opensearch.org/latest/observing-your-data/alerting/unified-alerts-view/) を参照してください。

### OpenSearch Observability Stack でアプリケーション監視を強化

[**OpenSearch Observability Stack**](https://opensearch.org/platform/observability-stack/) は、サービスとアプリケーションを監視するための、OpenTelemetry、OpenSearch、Prometheus をベースにした事前設定済みのディストリビューションで、本体とは別にデプロイします。OpenSearch 本体ディストリビューションとは独立してリリース・バージョニングされます。3.9 リリースサイクルでは、調査フロー全体を通してつながる形で改善が入りました。刷新されたトレース詳細画面と再利用可能な PromQL ダッシュボードから、ノーコードのアラートルール、ガイド付き APM セットアップウィザード、PPL クエリの記述・プロファイリング・大規模実行を容易にする一連のアップデートまでが含まれます。これらを含む機能は、OpenSearch [observability playground](https://observability.playground.opensearch.org/) で試すことができます。

#### 刷新されたトレース詳細画面で遅い・失敗したスパンを特定

OpenSearch 3.9 では、大規模なマルチサービストレースに対応するため、**Discover Traces** のトレース詳細ページが以下の図のように刷新されました。タイムラインのウォーターフォールはサービスごとに色分けされ、各スパンの所要時間がバーの末尾にラベル表示されて、エラースパンは赤い枠線で囲まれます。ズームスライダーでトレースの一部だけに表示を絞り込め、新しいツールバーコントロールで行の密度調整や、スパンツリーの階層ごとの展開・折りたたみが可能です。

新しいフィルターバーでは、**Status**、最小 **Duration** (値を直接入力するか、トレースから計算された p90 / p99 プリセットを選択)、任意のスパン属性でスパンを絞り込めます。フィルターは編集可能なピル (タグ) 状で表示され、Status と Duration のフィルターはクラスタへ再クエリせずに即座に適用されます。新しい **Trace map** タブでは、トレースに含まれるサービス同士の呼び出し関係を可視化できます。各サービスカードにはリクエスト数、エラー数、所要時間が表示され、サービスを選択するとビュー全体がそのサービスに絞り込まれます。詳細は [Discover Traces](https://observability.opensearch.org/docs/investigate/discover-traces/) を参照してください。

![刷新されたトレース詳細ページ。タイムラインウォーターフォールでスパンをサービス別に色分けし、所要時間を表示。エラースパンは赤枠と警告アイコンで示され、右側の Span details パネルで選択したスパンのステータス、所要時間、リクエストコードを確認できる](/images/get-to-know-opensearch-3-9/b0d13fbfe95a.png)
*刷新された **Discover Traces** のトレースタイムラインで、遅いスパンや失敗したスパンを特定する*

#### PromQL 変数と同期クロスヘアでダッシュボードをサービス間で再利用

OpenSearch 3.9 では、3.7 で導入されたダッシュボード変数が Prometheus にも拡張されました。Prometheus データソースをバックエンドとするクエリ変数では、ラベル名、ラベル値、メトリクス名、シリーズを列挙できます。1 つの `$service` 変数で、パネルのタイトルや説明を含むダッシュボード上のすべてのパネルを駆動できます。変数には **Text** 型、**Allow custom values** オプション、値やラベルを抽出する正規表現のキャプチャグループも追加されました。

相関の把握を容易にするため、ダッシュボードのオプションで **Sync crosshair across panels** を有効にできます。1 つの時系列パネルにカーソルを合わせると、他のすべてのパネルで同じ時刻にマーカーが表示されます。パネルは名前付きで折りたたみ可能なセクションにまとめたり、ドラッグで並べ替えたりもできます。セクションを有効にするには、`dashboard.allowDashboardSections` を `true` に設定します。詳細は [Dashboard sections](https://docs.opensearch.org/latest/dashboards/dashboard/dashboard-sections/) を参照してください。

**Discover** と visualization editor の可視化には、積み上げ棒グラフとエリアチャート、min / max 軸境界と小数精度を指定できる単位フォーマット、カスタムシリーズ名、シリーズ全体のホバーハイライト、凡例クリックでのフォーカス機能が追加されました。PromQL クエリ向けに、**Discover Metrics** ではクエリごとの **Series name** テンプレート、**Min step** 設定、`$__interval` / `$__rate_interval` / `$__range` の interval マクロが追加されました。詳細は [Dashboard variables](https://observability.opensearch.org/docs/dashboards/variables/) と [Discover Metrics](https://observability.opensearch.org/docs/investigate/discover-metrics/) を参照してください。

![Service RED メトリクスダッシュボード。Service 変数で 4 つのサービスを選択し、リクエストレート、フォールトレート、p95 レイテンシ、p50 レイテンシの 4 つの時系列パネルを Traffic & errors と Latency のセクションに分けて配置。クロスヘアとツールチップが全パネルで同じ時刻を示す](/images/get-to-know-opensearch-3-9/7ba59608bc6d.png)
*1 つの PromQL `service` 変数でダッシュボード全体を駆動し、パネル間でクロスヘアを同期させる*

#### PromQL を書かずに Prometheus のアラートルールを作成

OpenSearch 3.8 で **Create alert rule** アクションが追加されました。3.9 では、メトリクスルールのフライアウトにポイント & クリックの条件ビルダーも加わりました。ルールは 4 ステップで組み立てます。

1. メトリクスと、必要に応じてラベルフィルターを選択
2. 時間ウィンドウ上に `rate`、`increase`、`_over_time` 系集約などの関数を適用
3. 必要に応じて、ラベルによる集約 / ラベルなしの集約を指定
4. **IS ABOVE**、**IS OUTSIDE RANGE**、**IS WITHIN RANGE** といった条件を設定

ビルダーは操作しながら生成中の PromQL を表示し、変更を失わずに **Code** モードと切り替えられ、保存前にライブデータに対してルールをプレビューできます。ルールグループもフライアウトから直接設定できます。

検知器と予測器の管理機能に加えて、**Rules** タブから log、異常検知、予測のルールを作成でき、ページを離れずに検知器や予測器を編集・削除できます。詳細は [Creating alert rules](https://observability.opensearch.org/docs/alerting/unified-alerts/create-rules/) を参照してください。

#### 数クリックで Application Performance Monitoring を設定

新しい **Set up Application Monitoring** ウィザードにより、これまでの手作業による APM 設定が不要になります。ウィザードは、APM が必要とする 3 つのコンポーネント (トレースデータセット、サービスマップデータセット、レート・エラー・所要時間 (RED) メトリクスを提供する Prometheus データソース) の設定を順にガイドします。各ステップで既存データを自動検出し、既存のデータセットを再利用できます。データが OpenTelemetry のインデックス規約に沿っていれば、不足しているデータセットをワンクリックで作成できます。必須フィールドの検証も行うため、壊れた設定のまま完了することはありません。多数のサービスが存在する環境において、APM の **Services** ページと **Application Map** ページのレスポンスも改善されました。実験的機能として、任意のサービスやマップノードから関連するダッシュボードの一覧を開けます。詳細は [Configuring APM](https://observability.opensearch.org/docs/apm/configuring-apm/) を参照してください。

#### PPL クエリを書き、プロファイルし、大規模に実行

OpenSearch 3.9 では PPL と SQL に複数のアップデートが加わりました。詳細は [PPL commands](https://observability.opensearch.org/docs/ppl/commands/) と [Inspect Query](https://observability.opensearch.org/docs/ppl/inspect-query/) を参照してください。

- **クエリプロファイリング**: PPL リクエストに `"analyze": true` を指定すると、行数の見積もりと実測値、オペレーターごとの所要時間、ルールベースの最適化推奨を含むオペレーターツリーが返ります。**Discover Logs** の新しい **Inspect Query** パネルでは、同じ内訳をフェーズタイムラインとオペレーターウォーターフォールで表示できます。パネルを有効にするには `explore.pplAnalyze.enabled` を `true` に設定します
- **新コマンドとオプション**: `rest` コマンドはクラスタ管理エンドポイント (`/_cluster/health` など) の結果を行として返し、フィルターや集約が可能で、プラグインは追加のエンドポイントを登録できます。`include_metadata` パラメータは `_id`、`_index`、`_score` を返し、`top` と `rare` コマンドにはパーセンテージ列が追加されました
- **大規模環境での耐障害性**: 重いクエリは専用のスレッドプールで実行されるため、インタラクティブなクエリのレスポンスは保たれます。クエリの時間範囲外のインデックスは point-in-time コンテキストを開く前にスキップされ、幅広いインデックスパターンでの `search.max_open_pit_context` の枯渇を防ぎます。オプトイン設定の部分結果モードでは、あるインデックスで `text`、別のインデックスで `keyword` としてマッピングされているフィールドがあっても、注釈付きの結果を高速に返します
- **リンティング**: 新しいルールで `text` フィールドに対する集約、型の不一致、プッシュダウンできないコマンドを検出します。ヘッドレスの lint API により、同じルールを CI パイプラインで実行できます
- **SQL**: SQL に `histogram` / `date_histogram` 関数、`RANK()` / `DENSE_RANK()` 関数、`UNION` が追加されました。**Discover Logs** の SQL クエリで **Patterns** タブとヒストグラムがサポートされます
- **トレーシング**: PPL はクエリフェーズごとに OpenTelemetry スパンを発行します

## スケーラビリティと耐障害性

クラスタは負荷下でも応答性を保つ必要があり、インデックスライフサイクルは手動介入なしにスケールできる必要があります。OpenSearch 3.9 は、クラスタが負荷を扱う方法をより細かく制御できるようにし、大規模インデックス管理の基盤機能を追加し、モデル推論リクエストをサーバー側でバッチ処理してスループットを向上させます。

### アクション単位のアダプティブ同時実行数制限でクラスタを保護

OpenSearch 3.9 では、静的な閾値ではなく実測のリクエストレイテンシに基づいて、アクションごとの同時実行数の上限を動的に調整するモジュールとして、アダプティブ同時実行数制限が導入されました。検索やバルクインデックスなど任意の transport action にリミッターを設定でき、状況の変化に応じて上限を継続的に再調整する 3 種類のアダプティブアルゴリズムから選択できます。このモジュールには、リクエストを一切拒否せずリミッターの動作を追跡する監視のみモードと、上限に達したら実際に超過分を拒否する適用モードがあります。一時的なスパイクを吸収するバースト容量、名前付きサブプール間でリクエストを分割してトラフィッククラスを区別する機能、設定変更後のウォームアップ猶予期間もサポートします。リミッターの全状態は Nodes Stats API とテレメトリゲージから確認でき、すべての設定を再起動なしで動的に更新できます。詳細は [Concurrency limits](https://docs.opensearch.org/latest/tuning-your-cluster/availability-and-recovery/concurrency-limits/) を参照してください。

### インデックスレベルの検索プルーニングで時間範囲クエリを高速化

OpenSearch 3.9 では、コーディネーターノード上で動作する最適化として、インデックスレベルの検索プルーニングが導入されました。時系列やオブザーバビリティのワークロードで検索レイテンシを大幅に削減できます。従来は、ワイルドカードパターンを対象とする検索では、クエリの時間範囲フィルターが最新のインデックスにしかマッチしない場合でも、`can_match` フェーズでマッチした全インデックスに対してシャードレベルのリクエストを送っていました。新しい仕組みでは、コーディネーターノードが軽量な field-domain メタデータ (設定した date フィールドの最小値と最大値を各インデックスに記録するもの) を評価し、クエリ範囲外のインデックスをシャードレベルの処理に入る前にまるごとスキップします。日次インデックス 90 個を使ったローカルベンチマークでは、インデックスレベルの検索プルーニングによりテールレイテンシは 80% 以上削減され、`can_match` の transport リクエスト数はほぼ 98% 削減されました。分散クラスタではさらに大きな効果が見込まれます。オプトインの機能で、動的クラスタ設定から有効化できます。詳細は [Index-level search pruning](https://docs.opensearch.org/latest/search-plugins/index-level-search-pruning/) を参照してください。

### ルーティング付き delete のリプレイでゼロダウンタイムのインデックス再構成を実現

OpenSearch 3.9 では、translog に記録され `LuceneChangesSnapshot` API から公開される delete 操作でも、ドキュメントのルーティング情報が保持されるようになりました。index 操作にはすでにルーティング情報が付いていましたが delete 操作には付いておらず、translog 操作を異なるシャード数のインデックスにリプレイするツールでは、カスタムルーティング使用時に delete を正しくルーティングできませんでした。このギャップのため、CDC やスキーマ変更のプラグインはワークアラウンドを迫られ、対応可能なユースケースが制限されていました。今回、OpenSearch は delete 経路でもルーティング値を伝搬させるようになり、リプレイされた delete が正しいターゲットシャードにルーティングされます。ルーティングを保持することで、稼働中のインデックスをトラフィックを止めずに再構成する、ゼロダウンタイムのオンラインスキーマ変更ツールの基盤ができます。本アップデートに貢献してくださった Atlassian のコントリビューターの皆様に深く感謝します。[Automated Online Schema Change](https://atlassian-labs.github.io/opensearch-aosc/develop/) (AOSC) の詳細と実動作については、[Online index migration and shard scaling in OpenSearch with the AOSC plugin](https://opensearch.org/blog/online-index-migration-and-shard-scaling-in-opensearch-with-the-aosc-plugin/) を参照してください。

### サーバー側での推論バッチングでモデルスループットを向上

OpenSearch 3.9 では、ML Commons プラグインにモデル単位のリクエストバッチングが導入されました。推論呼び出しのサイズをモデルエンドポイントに合わせて調整する必要がなくなります。OpenSearch は大きな取り込みリクエストをエンドポイントの上限に収まる呼び出しに分割し、同時実行される小さな検索リクエストは 1 回の呼び出しにまとめます。これによりスループットが向上し、モデルサービングリソースをより効率的に活用できます。バッチングは OpenSearch 内部で行われるため、ingest プロセッサやプラグイン、API を直接呼び出すクライアントを含むすべての呼び出し元がクライアント側の変更なしで恩恵を受けられます。バッチングは登録済みモデルのメタデータで設定します。ワークロードに合わせてリクエストの上限を指定し、動的バッチングの設定を調整します。詳細は [Batching requests to externally hosted models](https://docs.opensearch.org/latest/ml-commons-plugin/remote-models/batching-requests/) を参照してください。

## セキュリティとインフラストラクチャ

OpenSearch 3.9 のセキュリティは、リソース共有フレームワークの大きなマイルストーンと、いくつかのアクセス制御の改善を含みます。

### リソース共有・アクセス制御フレームワークが GA、リソースアクセスを管理

OpenSearch 3.9 で、リソース共有・アクセス制御フレームワークが GA となりました。プラグインはこのフレームワークを利用して、異常検知の detector、アラート monitor、機械学習 (ML) のモデルグループといったリソースを、特定のユーザー、ロール、バックエンドロールと共有できます。本リリースでは、7 つのプラグインのリソース一覧テーブル上に一元的な **Share** ボタンがインラインで表示されるようになりました。詳細は [Resource sharing and access control](https://docs.opensearch.org/latest/security/access-control/resources/) を参照してください。

### Security プラグイン全体でアクセス制御を細かく調整

OpenSearch 3.9 では以下の追加のアクセス制御改善が含まれます。

- REST API リクエストボディの文字列長制限を設定可能にする `plugins.security.restapi.max_string_length`。大きなドキュメントレベルセキュリティ (DLS) クエリの互換性を回復します。詳細は [Security settings](https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/security-settings/) を参照してください
- 新しいクロスクラスタ検索設定 `plugins.security.ccs.ignore_source_security_roles`。移行元クラスタから伝搬されるセキュリティロールを無視します。詳細は [Remote cluster role evaluation](https://docs.opensearch.org/latest/search-plugins/cross-cluster-search/#remote-cluster-role-evaluation) を参照してください
- workload management ルールの principal に対する末尾ワイルドカードによる前方一致マッチのサポート。詳細は [Workload group rules](https://docs.opensearch.org/latest/tuning-your-cluster/availability-and-recovery/workload-management/workload-group-rules/) を参照してください

### OpenSearch における Amazon Linux 2 サポートの非推奨化

OpenSearch 3.9.0 では、Amazon Linux 2 のサポートを CI ビルドイメージおよびサポート対象 OS の両面で非推奨としました。Amazon Linux 2 は 2026 年 6 月 30 日でサポート終了を迎えています。詳細は AWS の [FAQ ドキュメント](https://aws.amazon.com/amazon-linux-2/faqs/)を参照してください。対応 OS の一覧は [Supported operating systems](https://docs.opensearch.org/latest/install-and-configure/os-comp/#supported-operating-systems) を参照してください。

## はじめかた

OpenSearch 3.9 はサポート対象の各ディストリビューションで[ダウンロード可能](https://opensearch.org/downloads/)で、[OpenSearch Playground](https://playground.opensearch.org/) でも試すことができます。変更点の全リストは[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-3.9.0.md)と[ドキュメントリリースノート](https://github.com/opensearch-project/documentation-website/blob/main/release-notes/opensearch-documentation-release-notes-3.9.0.md)、および更新された[ドキュメント](https://docs.opensearch.org/latest/)を参照してください。本リリースも例に漏れず、多くの組織のコントリビューターからなるコミュニティによる成果物です。皆様の使用感をぜひお聞かせください。[コミュニティフォーラム](https://forum.opensearch.org/)、[GitHub 上のプロジェクト](https://github.com/opensearch-project)、[OpenSearch Slack](https://opensearch.org/slack.html) を通じてフィードバックの共有やコミュニティへの参加をお願いします。

---

**TL;DR**: OpenSearch 3.9 は、ベクトル検索、オブザーバビリティ、クラスタの耐障害性を前進させます。検索面では、新しいネイティブエンジンによりニューラルスパース検索のスループットが向上しヒープ使用量が削減され、拡充されたストレージオプションで圧縮率と recall のトレードオフを調整できます。オブザーバビリティ面では、統合アラートビューに異常検知と予測が加わって GA となり、OpenSearch Observability Stack ではトレース調査・ダッシュボード・アラート・PPL が前進しました。耐障害性の面では、アクション単位のアダプティブ同時実行数制限とインデックスレベルの検索プルーニングにより、高負荷下でも安定したパフォーマンスを維持できます。さらに、リソース共有・アクセス制御フレームワークが GA となりました。まずは [OpenSearch 3.9 をダウンロード](https://opensearch.org/downloads/)して始めてください。
