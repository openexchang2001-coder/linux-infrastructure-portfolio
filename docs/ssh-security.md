# SSHサーバー構築・セキュリティ設定

作成者: YUNOSUKE

## 1. 構築環境

- Windows 11
- WSL2 / Ubuntu
- OpenSSH Server
- OpenSSH Client (Windows PowerShell)

## 2. 構築内容

- OpenSSH Serverの導入
- SSHサービスの起動
- WindowsからUbuntuへのSSH接続
- Ed25519鍵ペアの作成
- 公開鍵のauthorized_keysへの登録
- SSH公開鍵認証の設定

## 3. セキュリティ対策

以下のSSH設定を適用した。

- PubkeyAuthentication yes
- PasswordAuthentication no
- KbdInteractiveAuthentication no
- PermitRootLogin no

## 4. 動作確認

### 公開鍵認証

WindowsからUbuntuへSSH接続し、
公開鍵認証によるログインに成功。

確認ログ:
Accepted publickey for kaito

### パスワード認証の拒否

公開鍵認証を無効にして接続テストを実施。

結果:
Permission denied (publickey).

パスワード認証が拒否されることを確認。

## 5. ログ調査

journalctlを使用して以下を確認。

- SSHサービスの起動
- パスワード認証失敗
- 公開鍵認証成功
- SSHセッション開始

## 6. 補足

今回の検証は同一PC上のWindowsとWSL2で実施。
外部ネットワークからの接続検証は未実施。

秘密鍵・パスフレーズはGitHubに公開しない。
