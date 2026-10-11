# システム構成図

## 概要
Windows 11のWSL2上にUbuntuを構築し、
NginxでWebページを配信しています。

## システム構成

Windows 11（Chrome）
        |
        | HTTP / localhost:80
        v
WSL2（Ubuntu）
        |
        v
Nginx Webサーバー
        |
        v
/var/www/html/practice.html

## 監視機能
- BashスクリプトでHTTP応答を確認
- 正常時はOKを表示
- 異常時はNGを表示
- 手動実行による監視

## 使用技術
- Windows 11
- WSL2 / Ubuntu
- Nginx
- Bash
- HTTP / TCP 80

## セキュリティ
- 学習用のローカル環境
- 管理操作にはsudoを使用
- 設定ファイルをバックアップ
- インターネットへの公開は行っていない
