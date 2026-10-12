# Minecraft Server Infrastructure Portfolio

Minecraft Java Edition (Paper) サーバーを Linux / Docker Compose で構築し、構成管理、ログ確認、自動バックアップ、障害復旧を行う個人インフラ学習プロジェクトです。

## 目的と習得スキル
- Linux / WSL2 でのサーバー運用
- Docker / Docker Compose による再現可能な構成管理
- TCP 25565 のポート管理・ローカル接続
- ワールドデータの永続化とバックアップ運用
- RCON による管理、ホワイトリストとオンライン認証
- Git / GitHub による設定のバージョン管理
- GitHub Actions による Compose ファイルの構文検証

## 構成

```text
Minecraft Java Edition (Windows)
  | localhost:25565
Windows 11 + WSL2 (Ubuntu)
  | Docker Desktop / Docker Compose
  +-- minecraft (Paper)
  |      +-- ./data/ (world / settings / logs: Git管理対象外)
  +-- backups (itzg/mc-backup)
         +-- ./backups/ (Git管理対象外)
  +-- ./secrets/rcon_password.txt (Git管理対象外)
```

## 前提
- Windows 11、WSL2、Ubuntu、Docker Desktop (Ubuntu を WSL Integration で有効化)
- Ubuntu ターミナルで `docker version` と `docker compose version` が成功
- Java版Minecraftクライアント（Bedrock版専用ではありません）
- Minecraft EULA を確認し、同意していること (`EULA: "TRUE"`)
- Docker に十分なメモリを割り当ててあること（本例では Java heap 2 GB、全体はより多く必要）

## 初回セットアップ（Ubuntuターミナル）

```bash
cd ~/linux-infrastructure-portfolio/minecraft-server
mkdir -p secrets data backups
openssl rand -hex 24 > secrets/rcon_password.txt
chmod 600 secrets/rcon_password.txt
docker compose config -q
docker compose up -d
docker compose ps
docker compose logs -f minecraft
```

最後のログ追跡を終了するときは `Ctrl+C`。Composeで起動したサーバーは止まりません。

> このテンプレートは既存の `linux-infrastructure-portfolio` リポジトリ直下に `minecraft-server/` を置く想定です。別の場所で利用する場合は上記 `cd` のパスを変更してください。

## 接続

1. `docker compose ps` で Minecraft が `healthy` になることを確認。
2. Ubuntu ターミナルで Java版Minecraftのユーザー名を許可登録する。例: `docker compose exec minecraft rcon-cli whitelist add YourMinecraftJavaName`
3. Minecraft Java Edition のマルチプレイ画面で「サーバーを追加」。サーバーアドレスは `localhost:25565`。
4. Paperが対応するバージョンとクライアントのゲームバージョンを一致させる。

## 日々の運用コマンド

```bash
cd ~/linux-infrastructure-portfolio/minecraft-server
docker compose ps
docker compose logs --tail=80 minecraft
docker compose exec minecraft rcon-cli list
bash scripts/healthcheck.sh
docker compose exec backups backup now
ls -lh backups/
docker compose stop
docker compose up -d
```

バックアップの中身と復元については [operations.md](docs/operations.md) を参照。

## 安全性
- 接続口は `127.0.0.1:25565` に制限。初期状態でインターネットに公開しない。
- `ONLINE_MODE=TRUE`、ホワイトリスト有効。
- RCON用TCP 25575は外部に公開しない。
- パスワードは Compose secrets を使い別ファイル管理。`secrets/` を Git 管理対象外にする。
- ワールド・ログ・個人情報・バックアップは GitHub にアップロードしない。
- Dockerイメージの `latest` と Paperバージョンの未固定は、学習用の導入を容易にするため。安定運用段階では検証した版へ固定する。

## ドキュメント
- [アーキテクチャ](docs/architecture.md)
- [運用・復元手順](docs/operations.md)
- [障害報告テンプレート](docs/incident-template.md)

## 実施記録（自分で埋める）
- [ ] ローカルでサーバーの起動を確認した
- [ ] Java版クライアントから接続した
- [ ] ログで接続を確認した
- [ ] ホワイトリスト登録を実施した
- [ ] バックアップの作成を確認した
- [ ] 復元テストを実施した
- [ ] 意図的な設定ミスからの復旧を記録した
- [ ] クラウド移行の設計を作った

## 参考資料
- [Docker Desktop と WSL2](https://docs.docker.com/desktop/features/wsl/)
- [itzg/docker-minecraft-server](https://github.com/itzg/docker-minecraft-server)
- [itzg/docker-mc-backup](https://github.com/itzg/docker-mc-backup)
- [Minecraft サーバーダウンロード](https://www.minecraft.net/ja-jp/download/server)
