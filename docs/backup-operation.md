# Linuxバックアップ自動化・運用手順

作成者：YUNOSUKE

## 1. プロジェクト概要

BashスクリプトとWindowsタスクスケジューラを使用して、Linux環境のファイルを自動バックアップする仕組みを構築した。

## 2. 使用技術

- Ubuntu / WSL2
- Bash
- tar / gzip
- find / chmod
- Windows PowerShell
- Windowsタスクスケジューラ

## 3. 実装内容

- Bashスクリプトによるバックアップ作成
- 日時付きファイル名での世代管理
- tar.gz形式での圧縮保存
- バックアップファイルの検査
- 7日以上経過したバックアップの自動削除
- Windowsタスクスケジューラによる定期実行設定
- バックアップからの復元テスト

## 4. バックアップ対象

- README.md
- docs/
- scripts/
- site/

## 5. バックアップ保存先

`~/backups/linux-portfolio/`

保存形式：`portfolio_YYYYMMDD_HHMMSS.tar.gz`

## 6. 実行方法

```bash
./scripts/backup_portfolio.sh
```

## 7. 復元方法

```bash
mkdir -p ~/restore-test
tar -xzf <バックアップファイルのパス> -C ~/restore-test
```

復元後、cmpやdiffを使用して元ファイルとの一致を確認する。

## 8. 動作検証

### バックアップ作成

結果：成功

`OK: Backup completed`

### 復元テスト

結果：成功

`OK: 復元ファイル一致`

### 古いバックアップの削除テスト

更新日時を8日前に設定したテストファイルを用意し、削除処理を検証した。

結果：成功

`OK: 古いバックアップの削除成功`

### Windowsからの実行

PowerShellからWSLのバックアップスクリプトを実行し、正常終了を確認した。

Windowsタスクスケジューラに定期実行タスクを登録した。

## 9. 今後の改善点

- 別ディスクやクラウドへのバックアップ
- バックアップ失敗時の通知
- 定期実行履歴の継続的な確認
- バックアップの整合性検証の強化
- ディスク使用量の監視

## 10. 制約事項

今回の検証はWindows 11上のWSL2環境で実施した。

バックアップ保存先は元データと同じWSL環境内のため、WSL環境全体の破損には対応できない。
