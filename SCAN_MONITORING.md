# ZAPスキャン監視ガイド

このガイドでは、OWASP ZAPスキャン中にアプリケーション側でリクエストを監視する方法を説明します。

## 📋 目次

1. [スキャン準備](#スキャン準備)
2. [リアルタイム監視](#リアルタイム監視)
3. [スキャン分析](#スキャン分析)
4. [トラブルシューティング](#トラブルシューティング)

---

## 🔧 スキャン準備

スキャンを開始する前に、ログファイルをクリアします。

```bash
cd ~/VulnApp
./prepare_scan.sh
```

**実行内容:**
- 既存のログをバックアップ（`flask.log.backup_YYYYMMDD_HHMMSS`）
- ログファイルをクリア
- 監視用ログファイルを初期化

---

## 👁️ リアルタイム監視

### 方法1: 監視スクリプト（推奨）

別のターミナルで以下を実行:

```bash
cd ~/VulnApp
./monitor_zap_scan.sh
```

**表示内容:**
- 全リクエストのリアルタイム表示
- リクエスト数のカウント
- エラーの即座な検出

**停止方法:** `Ctrl+C`

### 方法2: tail コマンド

シンプルな監視:

```bash
tail -f ~/VulnApp/flask.log
```

### 方法3: リクエスト数のみ監視

```bash
watch -n 1 'wc -l ~/VulnApp/flask.log'
```

---

## 📊 スキャン分析

スキャン完了後（または途中で停止した場合）に実行:

```bash
cd ~/VulnApp
./analyze_scan.sh
```

### 分析レポート内容

#### 1. 基本統計
- 総リクエスト数
- HTTPメソッド別のカウント（GET, POST等）

#### 2. ステータスコード
- 各ステータスコードの出現回数
- 例: 200 OK, 404 Not Found, 500 Internal Server Error

#### 3. アクセス頻度の高いエンドポイント
- 上位20のエンドポイント
- どのページが最も多くテストされたか

#### 4. エラー・警告
- エラー/例外の総数
- 最近のエラーメッセージ（最新10件）

#### 5. 脆弱性テストのパターン検出
- SQLインジェクション試行回数
- XSSテスト試行回数
- パストラバーサル試行回数
- コマンドインジェクション試行回数

#### 6. スキャンタイムライン
- 開始時刻
- 最終時刻
- スキャン期間の推定

### サンプル出力

```
========================================
ZAPスキャン分析レポート
生成時刻: Sat Nov  1 02:00:00 JST 2025
========================================

【基本統計】
---
総リクエスト数: 1523
  - GET:  1450
  - POST: 73

【ステータスコード】
---
  200: 1320 回
  404: 150 回
  500: 53 回

【アクセス頻度の高いエンドポイント（上位20）】
---
    250 回: /products
    180 回: /product/1
    150 回: /product/search
    120 回: /files
     90 回: /api/info
    ...

【脆弱性テストのパターン検出】
---
  SQLインジェクション試行: 156 回
  XSSテスト試行: 89 回
  パストラバーサル試行: 45 回
  コマンドインジェクション試行: 23 回

【スキャンタイムライン】
---
開始時刻: 01/Nov/2025:01:30:00 +0900
最終時刻: 01/Nov/2025:01:58:45 +0900
```

---

## 🔍 トラブルシューティング

### スキャンが途中で停止した場合

1. **最後のリクエストを確認**
   ```bash
   tail -20 ~/VulnApp/flask.log
   ```

2. **エラーログを検索**
   ```bash
   grep -i error ~/VulnApp/flask.log | tail -10
   ```

3. **特定のエンドポイントでのエラー**
   ```bash
   grep '500' ~/VulnApp/flask.log | tail -20
   ```

4. **分析レポートを実行**
   ```bash
   ./analyze_scan.sh > scan_report_$(date +%Y%m%d_%H%M%S).txt
   ```

### よくある問題

#### 問題1: アプリケーションが応答しない

**確認方法:**
```bash
ps aux | grep 'python.*app.py'
curl -I http://localhost/
```

**解決策:**
```bash
# アプリケーション再起動
sudo pkill -f 'python.*app.py'
cd ~/VulnApp
sudo nohup /home/ubuntu/VulnApp/venv/bin/python3 app.py > flask.log 2>&1 &
```

#### 問題2: 大量のエラーが発生

**確認方法:**
```bash
grep -c 'error\|exception' flask.log
```

**調査:**
```bash
# エラーの種類を集計
grep -i error flask.log | cut -d':' -f3 | sort | uniq -c | sort -rn
```

#### 問題3: ログファイルが大きくなりすぎた

**サイズ確認:**
```bash
du -h flask.log
```

**ローテーション:**
```bash
# 現在のログをバックアップして圧縮
gzip -c flask.log > flask.log.$(date +%Y%m%d_%H%M%S).gz
> flask.log  # クリア
```

---

## 📈 スキャン後のベストプラクティス

1. **レポート保存**
   ```bash
   ./analyze_scan.sh > reports/zap_scan_$(date +%Y%m%d_%H%M%S).txt
   ```

2. **ログのアーカイブ**
   ```bash
   tar -czf logs_$(date +%Y%m%d_%H%M%S).tar.gz flask.log* zap_scan_monitor.log
   ```

3. **比較分析**
   - 複数のスキャン結果を比較
   - どのエンドポイントで問題が多いか特定
   - スキャナー間の検出率を比較

---

## 🛠️ カスタマイズ

### ログフォーマットの変更

`analyze_scan.sh`を編集して、必要な情報を追加:

```bash
# 例: 特定のペイロードを検索
grep -i 'your_pattern' flask.log | wc -l
```

### アラート設定

リアルタイムでエラーを通知:

```bash
tail -f flask.log | grep --line-buffered 'error' | while read line; do
    echo "⚠️ ERROR: $line"
    # メール通知やSlack通知をここに追加可能
done
```

---

## 📝 まとめ

| タイミング | コマンド | 目的 |
|----------|---------|------|
| **スキャン前** | `./prepare_scan.sh` | ログクリアとバックアップ |
| **スキャン中** | `./monitor_zap_scan.sh` | リアルタイム監視 |
| **スキャン後** | `./analyze_scan.sh` | 詳細分析レポート |

---

**注意事項:**
- スキャン監視は別のSSHセッションで実行することを推奨
- 大規模スキャンではログファイルのサイズに注意
- 問題が発生したら即座に `analyze_scan.sh` で状況を確認
