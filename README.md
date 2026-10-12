# Linux Web Server Portfolio

## 概要
WSL2のUbuntu上にNginx Webサーバーを構築しました。

## 使用技術
- Ubuntu / WSL2
- Nginx 1.28.3
- Bash
- curl / systemctl / journalctl

## 実装内容
- Webサーバーの構築
- HTMLページの公開
- BashによるHTTP監視
- 障害検知と復旧テスト

## 動作確認
- HTTP 200 OKを確認
- Nginx停止時の異常を検知
- Nginx再起動後の正常応答を確認

## 備考
学習用のローカル環境です。監視は手動実行です。

## SSHサーバー構築・セキュリティ強化

Windows 11とWSL2 Ubuntuを使用し、
SSHによるリモート接続環境を構築しました。

### 実装内容

- OpenSSH Serverのインストール・起動
- Windows PowerShellからのSSH接続
- Ed25519公開鍵認証
- SSHパスワード認証の無効化
- rootのSSHログイン禁止
- journalctlによるSSH認証ログの調査
- 認証方式の動作テスト

### 検証結果

- 公開鍵認証によるログイン成功
- パスワード認証によるログイン拒否を確認
- SSHサービスの正常稼働を確認

### 技術資料

[SSH構築・セキュリティ設定の詳細](docs/ssh-security.md)

※ 同一PC内のWSL2環境で検証。

## Linuxバックアップ自動化

Bashを使用してバックアップ運用を自動化しました。

### 実装機能

- tar.gz形式でのバックアップ作成
- 日時付きファイルによる世代管理
- 古いバックアップの自動削除
- バックアップの復元テスト
- Windowsタスクスケジューラとの連携

### 検証結果

- バックアップ作成：成功
- 復元ファイル比較：成功
- 古いバックアップの削除：成功
- PowerShellからの実行：成功

[バックアップ運用の技術資料](docs/backup-operation.md)






## Alertmanager Gmail Notifications

Implemented automated failure and recovery notifications using
Prometheus, Alertmanager, and Gmail SMTP.

**Validated:**
- Minecraft server failure detection
- FIRING email notification
- Server recovery
- RESOLVED email notification
- SMTP authentication troubleshooting
- Local credential protection

[View the notification validation report](minecraft-server/docs/alertmanager-gmail-validation.md)
