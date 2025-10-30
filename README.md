VulnApp-Simple
意図的に脆弱性を含むFlask製Webアプリケーション（教育・検証用）

⚠️ 警告
このアプリケーションは意図的に脆弱性を含んでいます。

本番環境では絶対に使用しないでください
セキュリティスキャナー（Tenable WAS、OWASP ZAP等）の評価・検証専用
ローカル環境または隔離されたテスト環境でのみ使用してください
📋 実装済み脆弱性

### Phase 1: 基本的な脆弱性（9種類）

| # | 脆弱性 | エンドポイント | 説明 |
|---|--------|---------------|------|
| 1 | SQL Injection (Union-based) | `/search` | UNION句を使ったデータ抽出 |
| 2 | SQL Injection (Error-based) | `/search` | エラーメッセージからの情報漏洩 |
| 3 | SQL Injection (Boolean-based) | `/search` | 真偽値による情報抽出 |
| 4 | Reflected XSS | `/search` | 検索結果にスクリプト挿入 |
| 5 | Stored XSS | `/comments` | データベースに保存されたスクリプト実行 |
| 6 | Path Traversal | `/file` | ディレクトリトラバーサル攻撃 |
| 7 | CSRF | `/transfer` | クロスサイトリクエストフォージェリ |
| 8 | Command Injection | `/ping` | OSコマンド実行 |
| 9 | Missing Security Headers | 全ページ | セキュリティヘッダー不足 |

### Phase 2: 追加脆弱性（4種類）

| # | 脆弱性 | エンドポイント | 説明 |
|---|--------|---------------|------|
| 10 | Open Redirect | `/redirect` | 任意のURLへのリダイレクト |
| 11 | Directory Listing | `/uploads`, `/static/downloads` | ディレクトリ一覧表示 |
| 12 | Path Traversal (Download) | `/download/<path>` | ファイルダウンロードでのパストラバーサル |
| 13 | Clickjacking | 全ページ | X-Frame-Options未設定 |

🚀 セットアップ
必要要件
Python 3.8以上
pip
インストール手順
リポジトリをクローン
git clone https://github.com/mizuna-honeypot/VulnApp.git cd VulnApp

仮想環境を作成
python3 -m venv venv source venv/bin/activate

Windowsの場合: venv\Scripts\activate

依存パッケージをインストール
pip install -r requirements.txt

データベースを初期化
python3 init_db.py

アプリケーションを起動
python3 app.py

cd ~/VulnApp-Simple

# すべてのPythonプロセスを停止
pkill -9 -f python3
sleep 2

# データベースロックファイルを削除
rm -f vulnapp.db-journal vulnapp.db-wal vulnapp.db-shm

# ポート5000を解放
sudo fuser -k 5000/tcp
sleep 2

# 再起動
nohup python3 app.py > flask.log 2>&1 &
sleep 3

# プロセス確認
ps aux | grep "python3 app.py" | grep -v grep

# ログ確認
echo "=== Flask起動ログ ==="
tail -10 flask.log


アプリケーションは http://localhost:5000 で起動します。

🧪 脆弱性テスト例
SQL Injection
Union-based SQLi:

curl "http://localhost:5000/search?q=test'+UNION+SELECT+1,username,password,4+FROM+users--"

Boolean-based SQLi:

curl "http://localhost:5000/search?q=test'+AND+'1'='1'--"

Path Traversal
--path-as-is オプションで正規化を無効化:

curl --path-as-is "http://localhost:5000/download/../app.py"

URLエンコード版:

curl "http://localhost:5000/download/..%2Fapp.py"

XSS
Reflected XSS:

curl "http://localhost:5000/search?q="

Stored XSS:

curl -X POST -d "name=Hacker&comment=" http://localhost:5000/comments

Command Injection
curl "http://localhost:5000/ping?host=127.0.0.1;cat /etc/passwd"

Directory Listing
curl http://localhost:5000/uploads curl http://localhost:5000/static/downloads

📁 プロジェクト構造
   ```bash
VulnApp-Simple/
├── app.py # メインアプリケーション 
├── init_db.py # データベース初期化スクリプト 
├── requirements.txt # Python依存パッケージ 
├── templates/ # HTMLテンプレート
│ ├── base.html
│ ├── index.html
│ ├── search.html
│ ├── comments.html
│ ├── file.html
│ ├── transfer.html
│ ├── ping.html
│ └── clickjacking_demo.html
├── static/ # 静的ファイル
│ └── downloads/ # Directory Listing用
└── uploads/ # Directory Listing用
   ```

🔍 スキャナー検証
このアプリケーションは以下のスキャナーで検証できます：

Tenable WAS (Web Application Scanning)
OWASP ZAP (Zed Attack Proxy)
Burp Suite
Nikto
Acunetix
推奨スキャン設定
スキャン対象URL: http://your-ip:5000/
クロール深度: Medium以上
認証: なし（匿名アクセス可能）
スキャンプロファイル: Full Scan
📝 ライセンス
MIT License - 教育・検証目的でのみ使用してください。

🤝 貢献
Pull Requestを歓迎します！新しい脆弱性パターンの追加や改善提案をお待ちしています。
