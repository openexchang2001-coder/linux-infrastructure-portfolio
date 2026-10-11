# 障害対応・トラブルシューティング記録

## 環境
- OS：Ubuntu（WSL2）
- Webサーバー：Nginx 1.28.3
- 監視：Bash / curl

## 事例1：Nginxのサービス停止

### 発生した問題
Nginxを意図的に停止させたところ、
WebサーバーへのHTTP接続が失敗した。

### 調査方法
以下のコマンドでサービスの状態を確認した。

systemctl is-active nginx

結果：inactive

続いて自作の監視スクリプトを実行。

bash scripts/check_nginx.sh

結果：NG: Web server check failed

### 復旧方法
以下のコマンドでNginxを起動。

sudo systemctl start nginx

### 復旧確認
監視スクリプトを再度実行した。

結果：OK: Web server is working

### 学んだこと
- サービスの稼働状態を確認する方法
- BashによるHTTP監視
- 障害検知から復旧までの流れ

---

## 事例2：404 Not Found

### 発生した問題
存在しないページにアクセスしたところ、
HTTP 404が返された。

### 調査方法
curl -I http://localhost/notfound.html

結果：HTTP/1.1 404 Not Found

Nginxのアクセスログも確認。

sudo tail -n 5 /var/log/nginx/access.log

結果：HEAD /notfound.html HTTP/1.1 404

### 原因の考察
指定したWebページが存在しないことが
原因と考えられる。

### 学んだこと
- HTTPステータスコードの理解
- アクセスログによる障害調査
- 正常応答と異常応答の区別

---

## 今後の改善点
- 定期的な自動監視
- 異常発生時の通知
- エラーログの自動収集
- 監視結果の履歴保存
