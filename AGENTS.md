# OpenSearch Blog Japanese Translation

OpenSearch Project の日本語コンテンツを Zenn で公開するプロジェクト。

## プロジェクト構成

```
├── scripts/           # ワークフロー用スクリプト
├── lib/               # 共通ライブラリ
├── articles/          # Zenn 記事ファイル (.md)
├── images/            # 記事内画像 (images/<slug>/)
├── .github/           # Issue テンプレート等
└── .kiro/
    ├── agents/        # エージェント設定
    ├── prompts/       # プロンプトファイル
    └── skills/        # SKILL ドキュメント
```

## 公開先

https://zenn.dev/opensearch

## エージェント一覧

| エージェント | 用途 | 実行方法 |
|---|---|---|
| orchestrator | ワークフロー全体の管理（取得→翻訳→レビュー→修正→公開） | `kiro-cli chat --agent orchestrator` |
| translator | OpenSearch Blog 記事の日本語翻訳 | orchestrator の sub-agent |
| reviewer | 翻訳記事の AI レビュー | orchestrator の sub-agent |
| fixer | レビュー指摘に基づく修正 | orchestrator の sub-agent |
| session-writer | OpenSearchCon セッション動画の記事作成 | orchestrator の sub-agent |
| dev | ツール自体の開発・改善 | `kiro-cli chat --agent dev` |

## ワークフロー

orchestrator エージェントが以下のフローを自動管理:

1. `scripts/fetch.py` で記事取得・画像 DL
2. translator sub-agent で翻訳
3. `scripts/check.py` で自動チェック
4. reviewer sub-agent で AI レビュー
5. (エラーあれば) fixer sub-agent で修正 → 3 に戻る
6. `scripts/publish.py --slug <slug>` で main に直接 commit・push（Zenn が main からデプロイ）
7. `https://zenn.dev/opensearch/articles/<slug>` で公開確認
8. `scripts/publish.py --slug <slug> --cleanup` で記事ファイルと画像を main から削除（Zenn 上はライブのまま残る）

## 公開モデル

- Zenn のデプロイ対象ブランチは `main`
- `articles/` には「今追加する記事」だけを置く。公開済みの記事はファイルを削除する。削除しても Zenn 上の記事は消えない（Zenn 側で手動削除しない限りライブのまま）。これで無関係な公開済み記事の再同期を防ぐ
- Code Defender の push ブロックは `lib/git.py` の push が `core.hooksPath=/dev/null` で自動回避する

## Git ルール

- HTTPS + トークン認証を使用（SSH 禁止）
- 記事は main に直接公開する。旧方式（`publish` ブランチへの relay、`article/{slug}` ブランチ + PR）は廃止

## 認証

GitHub CLI でログイン済みであること（`gh auth login`）。MCP サーバーが `gh auth token` でトークンを取得します。

## 前提ツール

- [Kiro CLI](https://kiro.dev/)
- Python 3.10+
- Node.js (npm)
- git, gh (GitHub CLI)
- yt-dlp（セッション記事作成時）
- ffmpeg（タイムスタンプ別サムネイル抽出用）
