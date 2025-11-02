
### 脆弱なコンポーネント（Vulnerable Components - A06:2021）

このアプリケーションは、以下の**既知の脆弱性を含む古いバージョンのコンポーネント**を意図的に使用しています：

| コンポーネント | バージョン | CVE | 深刻度 | 脆弱性の内容 |
|---------------|-----------|-----|--------|------------|
| **Flask** | 1.1.2 | CVE-2023-30861 | Medium | Possible disclosure of permanent session cookie |
| **Werkzeug** | 1.0.1 | CVE-2022-29361, CVE-2023-25577 | High | Path Traversal, Debug mode password hash disclosure |
| **Jinja2** | 2.11.3 | CVE-2020-28493 | Medium | Regular Expression Denial of Service (ReDoS) |
| **PyYAML** | 5.3.1 | CVE-2020-14343 | High | Arbitrary Code Execution via unsafe yaml.load() |

#### 検出方法

Webアプリケーションスキャナー（TenableWAS、OWASP ZAP等）は以下の方法でこれらの脆弱なコンポーネントを検出します：

1. **HTTPレスポンスヘッダー分析**
   - 
   - バージョン情報の露出

2. **エラーページ分析**
   - Flask/Werkzeugのデバッグページに含まれるバージョン情報
   - スタックトレースからのライブラリバージョン特定

3. **既知の脆弱性データベース照合**
   - National Vulnerability Database (NVD)
   - CVE（Common Vulnerabilities and Exposures）
   - OWASP Dependency-Check

#### requirements.txt



⚠️ **警告**: これらの脆弱なバージョンは、実際のアプリケーションでは**絶対に使用しないでください**。本番環境では常に最新の安定版を使用してください。

