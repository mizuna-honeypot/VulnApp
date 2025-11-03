# VulnApp - Vulnerable Web Application for Security Testing

意図的に脆弱性を含むFlask製Webアプリケーション（教育・検証用）

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.1.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Educational%20Only-red)

## ⚠️ 重要な警告

このアプリケーションは**意図的に脆弱性を含んでいます**。

- **本番環境では絶対に使用しないでください**
- セキュリティスキャナーの評価・検証専用
- ローカル環境または隔離されたテスト環境でのみ使用してください
- 公開インターネットに露出させないでください

---

## 📋 実装済み脆弱性（11種類）

このアプリケーションは、OWASP Top 10とCWE脆弱性パターンに基づいた11種類の脆弱性を実装しています。

| # | 脆弱性 | OWASP分類 | エンドポイント | 説明 |
|---|--------|-----------|---------------|------|
| 1 | **SQL Injection** | A03:2021 | `/products?search=` | パラメータ化されていないクエリによるSQLi |
| 2 | **Reflected XSS** | A03:2021 | `/products?search=` | 検索結果への悪意あるスクリプト反映 |
| 3 | **Stored XSS** | A03:2021 | `/guestbook` (POST) | ゲストブックへのスクリプト保存・実行 |
| 4 | **Path Traversal** | A01:2021 | `/files?file=` | ディレクトリトラバーサルによるファイルアクセス |
| 5 | **Missing Security Headers** | A05:2021 | 全エンドポイント | X-Frame-Options、CSP、HSTS等の欠如 |
| 6 | **CSRF** | A01:2021 | `/guestbook` (POST) | CSRFトークン未実装 |
| 7 | **Command Injection** | A03:2021 | `/tools/ping` | OSコマンドインジェクション |
| 8 | **Vulnerable Components** | A06:2021 | `/vulnerable-components` | jQuery 2.2.4（4つのCVE） |
| 9 | **Open Redirect** | A01:2021 | `/open-redirect-demo` | 未検証の外部URLリダイレクト |
| 10 | **Directory Listing** | A01:2021 | `/uploads/`, `/static/downloads/` | ディレクトリ内容の一覧表示 |
| 11 | **Clickjacking** | A04:2021 | `/clickjacking-demo` | X-Frame-Options未設定 |

### 🚨 脆弱性ハイライト

#### Vulnerable Components (jQuery 2.2.4)

特に検出が困難な**Vulnerable Components**脆弱性を実装：

- **使用ライブラリ**: jQuery 2.2.4（2016年リリース、サポート終了）
- **検出CVE**: 4件
  - CVE-2019-11358 (Prototype Pollution)
  - CVE-2015-9251 (XSS via location.hash)
  - CVE-2020-11022 (XSS via htmlPrefilter)
  - CVE-2020-11023 (XSS via htmlPrefilter)
- **実装場所**: `/static/js/jquery-2.2.4.min.js`
- **詳細ページ**: `/vulnerable-components`

#### Stored XSS with Deep DOM Structure

Guestbook機能にStored XSSを実装。特徴：

- **DOM構造の深さ**: Depth 7（XSSペイロード実行箇所）
- **スキャナー設定の重要性**: DOM Depthの設定が検出成否に影響
  - Depth 3（デフォルト）: 検出失敗
  - Depth 10（推奨）: 検出成功
- **エンドポイント**: `/guestbook`

---

## 🚀 クイックスタート

### 必要要件

- Python 3.8以上
- pip
- (オプション) sudo権限（ポート80使用時）

### インストール手順

```bash
# 1. リポジトリをクローン
git clone https://github.com/your-username/VulnApp.git
cd VulnApp

# 2. 仮想環境を作成・有効化
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 依存パッケージをインストール
pip install -r requirements.txt

# 4. データベースを初期化
python3 init_db.py

# 5. アプリケーションを起動
python3 app.py
```

### アクセスURL

- **開発環境**: http://localhost:5000
- **本番相当検証（ポート80）**: http://localhost

---

## 🧪 脆弱性テスト例

### 1. SQL Injection

**基本的なSQLi:**
```bash
curl "http://localhost:5000/products?search=' OR 1=1--"
```

**Union-based SQLi:**
```bash
curl "http://localhost:5000/products?search=' UNION SELECT NULL,sqlite_version(),NULL--"
```

### 2. Reflected XSS

```bash
curl "http://localhost:5000/products?search=<script>alert('XSS')</script>"
```

### 3. Stored XSS (Guestbook)

```bash
curl -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "name=Attacker&comment=<img src=x onerror=alert('Stored XSS')>" \
  http://localhost:5000/guestbook
```

ブラウザで `/guestbook` にアクセスしてペイロード実行を確認。

### 4. Path Traversal

**相対パス:**
```bash
curl "http://localhost:5000/files?file=../../app.py"
```

**絶対パス:**
```bash
curl "http://localhost:5000/files?file=/etc/passwd"
```

### 5. Command Injection

```bash
# 基本的なコマンド実行
curl "http://localhost:5000/tools/ping?host=127.0.0.1;id"

# バックティック使用
curl "http://localhost:5000/tools/ping?host=\`whoami\`"
```

### 6. CSRF (Cross-Site Request Forgery)

CSRFトークンなしでGuestbookにPOST可能：

```html
<!-- 攻撃者のサイトに配置 -->
<form action="http://victim-site/guestbook" method="POST">
  <input type="hidden" name="name" value="CSRF Attack">
  <input type="hidden" name="comment" value="This was posted via CSRF">
</form>
<script>document.forms[0].submit();</script>
```

### 7. Vulnerable Components (jQuery)

**バージョン確認API:**
```bash
curl http://localhost:5000/component-versions
```

**レスポンス例:**
```json
{
  "cves": [
    "CVE-2019-11358",
    "CVE-2015-9251",
    "CVE-2020-11022",
    "CVE-2020-11023"
  ],
  "library": {
    "jQuery": "2.2.4"
  },
  "warning": "This jQuery version contains known security vulnerabilities. DO NOT use in production!"
}
```

**HTTPヘッダーでの検出:**
```bash
curl -I http://localhost:5000/ | grep -i jquery
# X-Powered-By: jQuery/2.2.4
# X-jQuery-Version: 2.2.4
```

### 8. Open Redirect

```bash
curl -I "http://localhost:5000/open-redirect-demo?url=https://evil.com"
# Location: https://evil.com
```

### 9. Directory Listing

```bash
curl http://localhost:5000/uploads/
curl http://localhost:5000/static/downloads/
```

### 10. Clickjacking

ブラウザでアクセス：
- デモページ: http://localhost:5000/clickjacking-demo
- 攻撃例: http://localhost:5000/clickjacking-attack-demo

---

## 🔍 セキュリティスキャナーでの検証

このアプリケーションは、主要なWebアプリケーションスキャナーで検証できます。

### 推奨スキャン設定

| 設定項目 | 推奨値 | 理由 |
|---------|--------|------|
| **ターゲットURL** | `http://your-ip:5000/` | - |
| **クロール深度** | Medium以上 | 全エンドポイントを網羅 |
| **DOM Depth** | **10以上** | Stored XSS検出に必須 |
| **認証** | なし | 匿名アクセス可能 |
| **スキャンプロファイル** | Full Scan | 全脆弱性タイプを検出 |
| **JavaScript解析** | 有効 | jQuery脆弱性検出に必要 |

### ⚠️ 重要: DOM Depth設定

Stored XSS（Guestbook）の検出には、**DOM Depth=10以上**が必須です。

**Guestbookの DOM構造:**
```
Depth 0: <html>
  Depth 1: <body>
    Depth 2: <main>
      Depth 3: <div class="container">
        Depth 4: <div class="guestbook-container">
          Depth 5: <div class="message-card">
            Depth 6: <div class="message-body">
              Depth 7: [XSSペイロード実行箇所] ← ここで発火
```

- **DOM Depth = 3（デフォルト）**: Depth 3で停止 → **検出失敗**
- **DOM Depth = 10**: Depth 7まで到達 → **検出成功** ✅

---

## 📁 プロジェクト構造

```
VulnApp/
├── app.py                      # メインアプリケーション
├── init_db.py                  # データベース初期化スクリプト
├── requirements.txt            # Python依存パッケージ
├── README.md                   # このファイル
├── .gitignore                  # Git除外設定
│
├── vulnapp.db                  # SQLiteデータベース（自動生成）
├── guestbook.db                # Guestbook用データベース（自動生成）
│
├── templates/                  # Jinjaテンプレート
│   ├── base.html              # ベーステンプレート（jQuery読み込み）
│   ├── index.html             # トップページ（脆弱性一覧）
│   ├── products.html          # 商品検索（SQLi, Reflected XSS）
│   ├── guestbook.html         # ゲストブック（Stored XSS, CSRF）
│   ├── file_view.html         # ファイルビューア（Path Traversal）
│   ├── tools.html             # ツールページ（Command Injection）
│   ├── vulnerable_components.html  # 脆弱コンポーネント詳細
│   ├── open_redirect_demo.html     # オープンリダイレクトデモ
│   └── clickjacking_*.html    # クリックジャッキングデモ
│
├── static/                     # 静的ファイル
│   ├── css/
│   │   └── style.css          # メインスタイルシート
│   ├── js/
│   │   └── jquery-2.2.4.min.js # 脆弱なjQueryライブラリ（CVE-2019-11358等）
│   ├── files/
│   │   ├── public.txt         # 公開ファイル
│   │   └── secret.txt         # 機密ファイル（Path Traversal対象）
│   └── downloads/             # Directory Listing用
│
├── uploads/                    # アップロードディレクトリ（Directory Listing）
│   ├── sample1.txt
│   ├── sample2.txt
│   └── confidential.txt       # 機密ファイル
│
└── venv/                       # Python仮想環境（.gitignoreで除外）
```

---

## 🛠️ トラブルシューティング

### ポート80で起動できない

```bash
# ポート使用状況を確認
sudo lsof -i :80

# 既存プロセスを停止
sudo fuser -k 80/tcp

# アプリを再起動
sudo venv/bin/python3 app.py
```

### データベースエラー

```bash
# データベースを再初期化
rm -f vulnapp.db guestbook.db
python3 init_db.py
```

### プロセスが残っている

```bash
# Flaskプロセスを停止
pkill -f "python3 app.py"

# 確認
ps aux | grep "python3 app.py"
```

### Stored XSSが検出されない

スキャナーの**DOM Depth設定を10以上**に変更してください。デフォルト値（通常3）では、Guestbookの深い階層まで到達できません。

---

## 📊 検証結果例

### 検出された脆弱性サマリー

典型的なスキャン結果（DOM Depth=10の場合）：

| 深刻度 | 検出数 | 主な脆弱性 |
|--------|--------|-----------|
| **Critical** | 2 | Command Injection, Path Traversal |
| **High** | 5 | SQL Injection, Stored XSS等 |
| **Medium** | 11 | Reflected XSS, CSRF, jQuery CVE等 |
| **Low** | 42 | Missing Headers, Directory Listing等 |
| **Info** | 73 | Version Disclosure等 |

### jQuery脆弱性の検出

jQuery 2.2.4の4つのCVEが正常に検出されます：

- ✅ CVE-2019-11358 (Prototype Pollution) - Medium
- ✅ CVE-2015-9251 (XSS via location.hash) - Medium
- ✅ CVE-2020-11022 (XSS via htmlPrefilter) - Medium
- ✅ CVE-2020-11023 (XSS via htmlPrefilter) - Medium

---

## 🔐 修正方法（学習用）

このアプリケーションは教育目的のため、意図的に脆弱性を残しています。実際のアプリケーションでは以下の対策が必要です：

### 1. SQL Injection対策
```python
# 悪い例（現在の実装）
query = f"SELECT * FROM products WHERE name LIKE '%{search}%'"

# 良い例
query = "SELECT * FROM products WHERE name LIKE ?"
cursor.execute(query, (f"%{search}%",))
```

### 2. XSS対策
```html
<!-- 悪い例（現在の実装） -->
{{ comment | safe }}

<!-- 良い例 -->
{{ comment | escape }}
または
{{ comment }}  # デフォルトでエスケープ
```

### 3. CSRF対策
```python
# Flask-WTFを使用
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

### 4. セキュリティヘッダー追加
```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

### 5. jQuery更新
```bash
# 脆弱なバージョンを削除
rm static/js/jquery-2.2.4.min.js

# 最新版をダウンロード
wget https://code.jquery.com/jquery-3.7.1.min.js -O static/js/jquery-3.7.1.min.js
```

---

## 📝 ライセンス

MIT License

このソフトウェアは教育・検証目的でのみ使用してください。悪意ある目的での使用は禁止します。

---

## 🤝 貢献

Pull Requestを歓迎します！新しい脆弱性パターンの追加や改善提案をお待ちしています。

### 貢献ガイドライン

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/new-vulnerability`)
3. 変更をコミット (`git commit -am "Add: XXX vulnerability"`)
4. ブランチにプッシュ (`git push origin feature/new-vulnerability`)
5. Pull Requestを作成

### 追加したい脆弱性の例

- [ ] LDAP Injection
- [ ] XML External Entity (XXE)
- [ ] Server-Side Request Forgery (SSRF)
- [ ] Insecure Deserialization
- [ ] Authentication Bypass
- [ ] JWT Vulnerabilities
- [ ] GraphQL Injection

---

## 📚 参考資料

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)
- [OWASP Web Security Testing Guide](https://github.com/OWASP/wstg)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)

---

## ⚖️ 免責事項

このアプリケーションは、セキュリティ教育と脆弱性スキャナーの検証を目的としています。

- 本番環境での使用は厳禁です
- 不正アクセス行為に使用しないでください
- このツールの使用によって生じた損害について、作者は一切の責任を負いません
- 合法的な範囲内でのみ使用してください

---

**作成者**: Your Name  
**リポジトリ**: https://github.com/your-username/VulnApp  
**最終更新**: 2025年11月

---

## 🎯 学習目標

このアプリケーションを通じて以下を学べます：

✅ OWASP Top 10の主要な脆弱性パターン  
✅ セキュリティスキャナーの動作原理  
✅ DOM構造がXSS検出に与える影響  
✅ 脆弱なコンポーネント検出の仕組み  
✅ 安全なコーディング手法  
✅ 防御的プログラミングの重要性

**Happy Hacking!** 🔒
