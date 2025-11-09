from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, Response
import sqlite3
import os
import subprocess
import platform
import sys
from collections import defaultdict
from datetime import datetime, timedelta
import time 


# カスタムResponseクラス: ヘッダーバリデーションを無効化
from werkzeug.wrappers import Response as BaseResponse
from werkzeug.datastructures import Headers

class NoValidationResponse(BaseResponse):
    """ヘッダーバリデーションをスキップするカスタムResponse"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # バリデーションをスキップするため、独自のヘッダーリストを使用
        self._no_validation_headers = []
    
    def get_wsgi_headers(self, environ):
        """WSGIヘッダーを取得（バリデーションなし）"""
        headers = Headers()
        
        # 通常のヘッダーを追加
        for key, value in super().get_wsgi_headers(environ):
            if key.lower() != 'location':  # Locationは別処理
                headers.add(key, value)
        
        # バリデーションなしのヘッダーを追加
        for key, value in self._no_validation_headers:
            headers._list.append((key, value))
        
        return headers


app = Flask(__name__)
app.url_map.strict_slashes = False

def get_db_connection():
    """データベース接続を取得"""
    conn = sqlite3.connect('vulnapp.db', timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    # Time-based SQLi 用のカスタム関数を追加
    def sleep_func(seconds):
        """SQLite用のSLEEP関数"""
        import time
        time.sleep(seconds)
        return seconds
    
    conn.create_function("SLEEP", 1, sleep_func)
    
    return conn


@app.route('/')
def index():
    """トップページ"""
    return render_template('index.html')


@app.route('/products')
def products():
    """商品一覧ページ（検索機能付き）

    脆弱性1: SQLインジェクション
    脆弱性2: XSS (Reflected)
    """

    search_query = request.args.get('search', '')
    error_message = None
    products_list = []

    conn = get_db_connection()
    try:
        if search_query:
            try:
                # 🚨 脆弱性1: SQLインジェクション
                query = f"SELECT * FROM products WHERE name LIKE '%{search_query}%' OR description LIKE '%{search_query}%'"
                products_list = conn.execute(query).fetchall()
            except sqlite3.Error as e:
                # 🚨 脆弱性: SQLエラーメッセージを表示
                error_message = f"Database Error: {str(e)}\n\nExecuted Query: {query}"
        else:
            products_list = conn.execute('SELECT * FROM products').fetchall()
    finally:
        conn.close()


    # 🚨 脆弱性2: XSS (Reflected)
    return render_template('products.html',
                          products=products_list,
                          search_query=search_query,
                          error_message=error_message)



@app.route('/product/search')
def product_search():
    """商品検索API（より検出されやすいSQLi）

    脆弱性: SQL Injection (シンプルな実装)
    例: /product/search?id=1 OR 1=1--
    """
    product_id = request.args.get('id', '')
    error_message = None
    products = []

    conn = get_db_connection()
    try:
        if product_id:
            try:
                # 🚨 脆弱性: パラメータ化されていないクエリ
                query = f"SELECT * FROM products WHERE id = {product_id}"
                products = conn.execute(query).fetchall()
            except sqlite3.Error as e:
                error_message = f"SQL Error: {str(e)}\nQuery: {query}"
    finally:
        conn.close()

    # テンプレートを使用してレンダリング
    return render_template('sqli_search.html',
                         product_id=product_id,
                         error_message=error_message,
                         products=products)




@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """商品詳細ページ
    
    修正済み: SQLインジェクション対策（パラメータ化クエリ使用）
    修正済み: XSS対策（テンプレートで自動エスケープ）
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # パラメータ化クエリでSQLインジェクション対策
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()

        if not product:
            return "商品が見つかりません", 404

    finally:
        conn.close()

    return render_template('product_detail.html', product=product)

def account_settings():
    """CSRF Vulnerable - No CSRF token validation"""
    if request.method == 'POST':
        # No CSRF token check (intentional vulnerability)
        email = request.form.get('email', '')
        username = request.form.get('username', '')
        
        # Not actually saving to DB (for simplicity)
        message = f"Settings updated! Email: {email}, Username: {username}"
        return render_template('account_settings.html',
                             message=message,
                             current_email=email,
                             current_username=username)
    
    # Default values
    return render_template('account_settings.html',
                         current_email='user@example.com',
                         current_username='testuser')
@app.route('/account/delete', methods=['GET', 'POST'])
def delete_account():
    """CSRF Vulnerable - Dangerous action without CSRF protection"""
    
    # GETメソッドの場合はエンドポイント情報を返す
    if request.method == 'GET':
        return jsonify({
            "endpoint": "/account/delete",
            "method": "POST",
            "description": "Delete user account (CSRF Vulnerable)",
            "required_parameters": {
                "username": "string",
                "confirm": "boolean"
            },
            "warning": "This endpoint is intentionally vulnerable to CSRF attacks",
            "example": {
                "username": "testuser",
                "confirm": "true"
            }
        }), 200
    # CSRFトークンチェックなし（意図的な脆弱性）
    username = request.form.get('username', 'unknown')
    return f"Account deleted for user: {username} (Simulated)"


# ==========================================
# Command Injection Vulnerability
# ==========================================
@app.route('/tools')
def tools_page():
    """Network tools page"""
    return render_template('tools.html')


@app.route('/tools/ping', methods=['GET', 'POST'])
def ping_tool():
    """Command Injection Vulnerable - Ping tool"""
    output = ""
    host = ""
    
    if request.method == 'POST':
        host = request.form.get('host', '')
    elif request.method == 'GET':
        host = request.args.get('host', '')
    
    if host:
        try:
            # 意図的な脆弱性: サニタイズなし
            if platform.system().lower() == 'windows':
                cmd = f'ping -n 2 {host}'
            else:
                cmd = f'ping -c 2 {host}'
            
            # シェル経由で実行（危険）
            result = subprocess.run(cmd, shell=True, capture_output=True,
                                  text=True, timeout=5)
            output = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            output = "Command timed out"
        except Exception as e:
            output = f"Error: {str(e)}"
    
    return render_template('tools.html', ping_output=output, ping_host=host)


@app.route('/tools/nslookup', methods=['GET', 'POST'])
def nslookup_tool():
    """Command Injection Vulnerable - DNS lookup tool"""
    output = ""
    domain = ""
    
    if request.method == 'POST':
        domain = request.form.get('domain', '')
    elif request.method == 'GET':
        domain = request.args.get('domain', '')
    
    if domain:
        try:
            # 意図的な脆弱性: サニタイズなし
            if platform.system().lower() == 'windows':
                cmd = f'nslookup {domain}'
            else:
                cmd = f'host {domain}'
            
            # シェル経由で実行（危険）
            result = subprocess.run(cmd, shell=True, capture_output=True,
                                  text=True, timeout=5)
            output = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            output = "Command timed out"
        except Exception as e:
            output = f"Error: {str(e)}"
    
    return render_template('tools.html', nslookup_output=output, nslookup_domain=domain)


# レート制限のための簡易実装（メモリベース）
review_timestamps = defaultdict(list)

def is_rate_limited(ip_address, max_requests=10, time_window=60):
    """レート制限チェック（簡易版）"""
    now = datetime.now()
    cutoff = now - timedelta(seconds=time_window)
    
    review_timestamps[ip_address] = [
        ts for ts in review_timestamps[ip_address] if ts > cutoff
    ]
    
    if len(review_timestamps[ip_address]) >= max_requests:
        return True
    
    review_timestamps[ip_address].append(now)
    return False

# ==========================================
# Phase 2: 追加の脆弱性
# ==========================================

# ==========================================
# Open Redirect Vulnerability
# ==========================================
@app.route('/redirect')
def open_redirect():
    """Open Redirect Vulnerable - 任意URLへの無制限リダイレクト
    
    🚨 脆弱性: URLの検証を一切行わずに、パラメータの値を
    Locationヘッダーにそのまま設定してリダイレクト
    """
    url = request.args.get('url', '/')
    
    # 🚨 脆弱性ポイント: URL検証なし
    # どんなURLでも受け入れてリダイレクト
    # - 外部URL: http://evil.com
    # - 相対パス: ../admin
    # - プロトコル相対: //evil.com
    # - JavaScript: javascript:alert('XSS')
    
    # Flaskのredirect()を使用すると検証が入るため、
    # 直接Responseを返す
    from flask import Response
    response = Response("", status=302)
    response.headers['Location'] = url  # 検証なしで直接設定
    return response



@app.route('/fake-external')
def fake_external_site():
    """偽の外部サイト（Open Redirect のテスト用）"""
    target = request.args.get('target', 'unknown')
    return f'''
    <html>
    <head><meta charset="UTF-8"><title>Redirected</title></head>
    <body>
        <h2>🔀 Open Redirect 検証ページ</h2>
        <p>このページは Open Redirect の脆弱性を検証するための偽の外部サイトです。</p>
        <hr>
        <p><strong>リダイレクト先として指定されたURL:</strong></p>
        <pre>{target}</pre>
        <hr>
        <p>⚠️ 実際の環境では、このURLに外部リダイレクトされ、フィッシング攻撃などに悪用される可能性があります。</p>
        <hr>
        <p><a href="/">ホームに戻る</a></p>
    </body>
    </html>
    '''

@app.route('/open-redirect-demo')
def open_redirect_demo():
    """Open Redirect vulnerability demo page"""
    return render_template('open_redirect_demo.html')
@app.route('/files')
def file_view():
    """File view function
    
    Vulnerability 4: Path Traversal
    """
    filename = request.args.get('file', '')
    content = None
    error = None
    
    if filename:
        try:
            # Vulnerability 4: Path Traversal
            if filename.startswith('/'):
                file_path = filename
            elif filename.startswith('..'):
                base_dir = os.path.abspath(os.path.join(os.getcwd(), 'static', 'files'))
                file_path = os.path.normpath(os.path.join(base_dir, filename))
            else:
                file_path = os.path.join(os.getcwd(), 'static', 'files', filename)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            error = f'Failed to read file: {str(e)}'
    
    return render_template('file_view.html', filename=filename, content=content, error=error)

@app.route('/vulnerable-components')
def vulnerable_components():
    """Vulnerable Components information page
    
    Vulnerability 8: Vulnerable Components (A06:2021)
    Displays information about intentionally vulnerable packages
    """
    return render_template('vulnerable_components.html')
@app.route('/security-headers')
def security_headers():
    """Security Headers information page
    
    Vulnerability 5: Missing Security Headers
    Displays information about missing security headers
    """
    return render_template('security_headers.html')


@app.route('/component-versions')
def component_versions():
    """jQuery version disclosure endpoint
    
    Intentionally exposes jQuery version for security scanner detection
    """
    return jsonify({
        'library': {
            'jQuery': '2.2.4'  # CVE-2019-11358, CVE-2015-9251, CVE-2020-11022, CVE-2020-11023
        },
        'cves': [
            'CVE-2019-11358',  # Prototype Pollution
            'CVE-2015-9251',   # XSS via location.hash
            'CVE-2020-11022',  # XSS via htmlPrefilter
            'CVE-2020-11023'   # XSS via htmlPrefilter
        ],
        'warning': 'This jQuery version contains known security vulnerabilities. DO NOT use in production!'
    })

@app.route('/trigger-version-error')
def trigger_version_error():
    """Trigger error page with version information
    
    Deliberately causes an exception that exposes component versions in stack trace
    """
    import flask
    import jinja2
    import yaml
    
    # Intentionally raise exception with version info
    raise Exception(
        f"Component Versions - "
        f"Flask {flask.__version__}, "
        f"Jinja2 {jinja2.__version__}, "
        f"PyYAML {yaml.__version__}"
    )


@app.route('/api/info')
def api_info():
    """API information endpoint (debug info leakage example)
    
    Vulnerability 5: Information Disclosure
    """
    import sys
    import flask
    
    # Vulnerability 5: Debug information leakage
    return {
        'version': '1.0.0',
        'python_version': sys.version,
        'debug': app.debug,
        'database': 'vulnapp.db',
        'database_path': os.path.abspath('vulnapp.db'),
        'framework': 'Flask ' + flask.__version__,
        'server': 'Development Server',
        'host': request.host,
        'cwd': os.getcwd(),
        'endpoints': [str(rule) for rule in app.url_map.iter_rules()]
    }
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """ログインページ - CSRF Vulnerable
    
    GETとPOSTを同じエンドポイントで処理することで、
    スキャナーがCSRFを検出しやすくする
    """
    success = False
    username = None
    
    # POST: ログイン処理（CSRFトークンなし）
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # 簡易的な認証（デモ用）
        if username and password:
            success = True
    
    # テンプレートをレンダリング
    return render_template('login.html', success=success, username=username)



@app.route('/uploads/')
@app.route('/uploads')
def list_uploads():
    """Uploadsディレクトリの一覧表示
    
    🚨 脆弱性: Directory Listing (A01:2021)
    """
    upload_dir = os.path.join(os.getcwd(), 'uploads')
    
    try:
        file_list = []
        files = os.listdir(upload_dir)
        files.sort()
        
        for file in files:
            file_path = os.path.join(upload_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                mtime = os.path.getmtime(file_path)
                from datetime import datetime
                mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                
                file_list.append({
                    'name': file,
                    'size': size,
                    'mtime': mtime_str
                })
        
        return render_template('uploads_list.html', files=file_list)
        
    except Exception as e:
        return f"Error listing directory: {str(e)}", 500


@app.route('/uploads/<path:filename>')
@app.route('/download/<path:filename>')

def download_upload(filename):
    """アップロードされたファイルのダウンロード
    
    脆弱性: パストラバーサル対策が不十分
    """
    upload_dir = os.path.join(os.getcwd(), 'uploads')
    
    try:
        # 🚨 脆弱性: パストラバーサル対策が不十分
        # os.path.joinではなく文字列結合を使用（../が正規化されない）
        if filename.startswith("/"):
            # 絶対パスの場合はそのまま使用
            file_path = filename
        else:
            # 相対パスの場合はupload_dirと結合（../を含む場合も処理）
            file_path = os.path.normpath(os.path.join(upload_dir, filename))
            # os.path.normpathは正規化するが、upload_dirより上には行けないようにチェックしない

        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_file(file_path)
        else:
            return 'File not found', 404
            
    except Exception as e:
        return f'Error: {str(e)}', 500


@app.route('/static/downloads')
@app.route('/static/downloads/')
def list_downloads():
    """Directory Listing Vulnerable - staticディレクトリの一覧表示"""
    download_dir = os.path.join(os.getcwd(), 'static', 'downloads')
    
    try:
        files = os.listdir(download_dir)
        
        html = '''
        <html>
        <head><meta charset="UTF-8"><title>Downloads</title></head>
        <body>
            <h2>📥 Available Downloads</h2>
            <p style="color: red;">⚠️ 脆弱性: 本来非公開であるべきファイルが一覧表示されています</p>
            <ul>
        '''
        
        for file in files:
            file_path = os.path.join(download_dir, file)
            size = os.path.getsize(file_path)
            html += f'<li><a href="/static/downloads/{file}">{file}</a> ({size} bytes)</li>'
        
        html += '''
            </ul>
            <hr>
            <p><a href="/">ホームに戻る</a></p>
        </body>
        </html>
        '''
        
        return html
        
    except Exception as e:
        return f'Error: {str(e)}', 500


# ==========================================
# Clickjacking Vulnerability
# ==========================================
# 注: Clickjacking 対策は after_request フックで既に無効化されています
# （X-Frame-Options ヘッダーが設定されていない）

@app.route('/clickjacking-demo')
def clickjacking_demo():
    """Clickjacking のデモページ
    
    このページは iframe 内に埋め込み可能（X-Frame-Options がないため）
    """
    return render_template('clickjacking_demo.html')


@app.route('/clickjacking-attack-demo')
def clickjacking_attack():
    """Clickjacking 攻撃のデモページ（攻撃者が作成するページ）"""
    return '''
    <html>
    <head><meta charset="UTF-8"><title>攻撃者のページ</title></head>
    <body>
        <h2>🎁 無料ギフトをゲット！</h2>
        <p>クリックして無料ギフトを受け取ろう！</p>
        
        <div style="position: relative; width: 400px; height: 200px;">
            <!-- 透明な iframe で脆弱なページを重ねる -->
            <iframe src="/clickjacking-demo" 
                    style="position: absolute; top: -80px; left: -50px; opacity: 0.0; width: 500px; height: 300px;">
            </iframe>
            
            <!-- ユーザーがクリックすると思わせる偽のボタン -->
            <button style="position: absolute; top: 50px; left: 50px; padding: 20px; font-size: 18px; background-color: green; color: white;">
                🎁 ギフトを受け取る
            </button>
        </div>
        
        <hr>
        <p style="color: red;">⚠️ 上記の緑のボタンをクリックすると、実際には透明な iframe 内の「アカウント削除」ボタンがクリックされます</p>
    </body>
    </html>
    '''


# 管理用: レビュー削除エンドポイント


# ==========================================
# Stored XSS Vulnerability: Guestbook
# ==========================================

@app.route('/guestbook', methods=['GET', 'POST'])
def guestbook():
    """ゲストブック - Stored XSS Vulnerable
    
    GETとPOSTを同じエンドポイントで処理することで、
    スキャナーがStored XSSを検出しやすくする
    """
    conn = get_db_connection()
    
    # POST: 新しいコメントを投稿
    if request.method == 'POST':
        name = request.form.get('name', 'Anonymous')
        comment = request.form.get('comment', '')
        
        # 意図的な脆弱性: XSS対策なし
        try:
            conn.execute(
                "INSERT INTO guestbook (name, comment, created_at) VALUES (?, ?, datetime('now'))",
                (name, comment)
            )
            conn.commit()
        except Exception as e:
            print(f"Error saving guestbook entry: {e}")
    
    # GET: すべてのコメントを表示
    try:
        entries = conn.execute(
            "SELECT id, name, comment, created_at FROM guestbook ORDER BY id DESC LIMIT 50"
        ).fetchall()
    except Exception as e:
        print(f"Error fetching guestbook entries: {e}")
        entries = []
    finally:
        conn.close()
    
    return render_template('guestbook.html', entries=entries)


@app.route('/guestbook/clear', methods=['POST'])
def clear_guestbook():
    """ゲストブックをクリア（管理者用）"""
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM guestbook")
        conn.commit()
    except Exception as e:
        print(f"Error clearing guestbook: {e}")
    finally:
        conn.close()
    
    return redirect(url_for('guestbook'))



# Add custom headers to expose component versions (Vulnerability: Information Disclosure)
@app.after_request
def add_version_headers(response):
    """Add custom header exposing jQuery version
    
    Vulnerability: Information Disclosure
    Intentionally exposes jQuery version in HTTP headers for scanner detection
    """
    # Add custom header with jQuery version
    response.headers['X-Powered-By'] = 'jQuery/2.2.4'
    response.headers['X-jQuery-Version'] = '2.2.4'  # CVE-2019-11358, CVE-2015-9251, CVE-2020-11022, CVE-2020-11023
    
    return response

if __name__ == "__main__":
    # 🚨 脆弱性5: セキュリティヘッダーの欠如
    app.run(host='0.0.0.0', port=80, debug=True)
