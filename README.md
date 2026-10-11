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
