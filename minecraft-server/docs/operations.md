# 運用・障害復旧 Runbook

すべて `minecraft-server/` ディレクトリ内で実行する。

## 正常性確認

```bash
docker compose ps
bash scripts/healthcheck.sh
docker compose logs --tail=100 minecraft
```

確認ポイント: `minecraft` が Up (healthy)、`rcon-cli list` に応答、重大なERRORの連発がない。

## 起動と停止

```bash
docker compose up -d
docker compose stop
docker compose down
```

`down` も bind mount の `data/` を削除しないが、`rm -rf data` などは絶対に実行しないこと。

## プレイヤーのアクセス制御

```bash
docker compose exec minecraft rcon-cli whitelist add YourMinecraftJavaName
docker compose exec minecraft rcon-cli whitelist list
docker compose exec minecraft rcon-cli whitelist remove YourMinecraftJavaName
```

## 手動バックアップ

```bash
docker compose exec backups backup now
ls -lah backups/
```

バックアップは 24時間間隔で自動実行。成功したログを `docker compose logs --tail=100 backups` で確認する。

## 復元テスト

1. プレイヤーがオフラインのときに実施し、対象ワールドを明確にする。
2. `ls -lh backups/` でアーカイブを確認。
3. `tar -tzf backups/実際のファイル名.tgz | head` で内容を確認。
4. `bash scripts/restore.sh backups/実際のファイル名.tgz` を実行。`restore` と入力して確定。
5. 起動後 `docker compose ps` とログを確認し、ワールドデータが復元されたことをゲームで検証。
6. 以前のデータは `data.before-restore-YYYYMMDD-HHMMSS` として退避される。内容確認まで消さない。

**注意:** 復元によって現在のワールド状態を置き換えます。GitHubにはバックアップをアップロードしません。また、このローカルバックアップのみではPC故障に対処できないため、実運用時は外部にも複製してください。

## トラブルシュート例

| 症状 | 確認項目 | 対応例 |
|---|---|---|
| `docker: command not found` | Docker Desktop / WSL Integration | Docker Desktopを起動しUbuntu統合を有効化 |
| コンテナがすぐ停止 | `docker compose logs minecraft` | EULA、設定誤記、メモリ等を確認 |
| `Connection refused` | 起動状態、TCP 25565、バージョン | `docker compose ps`、接続先 `localhost` を再確認 |
| ホワイトリスト拒否 | `rcon-cli whitelist list` | Java版ユーザー名を登録 |
| 重い / ラグ | `docker stats`、CPU・メモリ使用量 | 同時接続やシミュレーション距離を見直す |
| Backupに失敗 | `docker compose logs backups` | Paper healthy、RCON secret、空き容量を確認 |

## セキュリティ
- 検証段階ではルーターのポート転送や公网公開をしない。
- GitHubに `secrets/` `data/` `backups/` を含めない。
- 接続元を限定し、オンライン認証を無効化しない。
- Docker の管理APIや RCON を無認証で外部公開しない。
- Docker Desktopが停止するとサーバーも利用できない場合がある。常時稼働には専用Linuxサーバー/クラウドを用いる。
