import sqlite3
import os

def init_database():
    """データベースを初期化し、サンプルデータを投入"""
    
    # 既存のDBファイルがあれば削除
    if os.path.exists('vulnapp.db'):
        os.remove('vulnapp.db')
    
    # 必要なディレクトリを作成
    directories = ['uploads', 'static/files']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f'📁 ディレクトリ作成: {directory}')
    
    # uploadsディレクトリにサンプルファイルを作成
    upload_files = {
        'uploads/sample1.txt': 'これは公開されているサンプルファイルです。\nアップロードディレクトリの内容が誰でも閲覧できる状態になっています。',
        'uploads/sample2.txt': 'ユーザーがアップロードしたファイル2\nこのファイルも公開されています。',
        'uploads/confidential.txt': '機密情報：このファイルは本来非公開であるべきです。\nパスワード: SecretPassword123\nAPI Key: sk-1234567890abcdef',
        'uploads/document.pdf': 'Test data for download',
        'uploads/.gitkeep': '',
    }
    
    for filepath, content in upload_files.items():
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'📄 ファイル作成: {filepath}')
    
    conn = sqlite3.connect('vulnapp.db')
    cursor = conn.cursor()
    
    # 商品テーブル作成
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            category TEXT
        )
    ''')
    
    # レビューテーブル作成
    cursor.execute('''
        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            author TEXT NOT NULL,
            comment TEXT NOT NULL,
            rating INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # ゲストブックテーブル作成（Stored XSS用）
    cursor.execute('''
        CREATE TABLE guestbook (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            comment TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # サンプル商品データ
    products = [
        ('ノートパソコン', '高性能な最新モデル', 89800, 'electronics'),
        ('ワイヤレスマウス', '快適な操作性', 2980, 'electronics'),
        ('プログラミング入門書', '初心者向けの解説書', 3200, 'books'),
        ('USBメモリ 64GB', '高速転送対応', 1280, 'electronics'),
        ('Webセキュリティ本', 'セキュリティの基礎', 4800, 'books'),
        ('キーボード', 'メカニカル式', 12800, 'electronics'),
        ('モニター 27インチ', '4K解像度対応', 45000, 'electronics'),
        ('Python実践ガイド', '中級者向け', 3800, 'books'),
    ]
    
    cursor.executemany(
        'INSERT INTO products (name, description, price, category) VALUES (?, ?, ?, ?)',
        products
    )
    
    # サンプルレビューデータ
    reviews = [
        (1, '山田太郎', '素晴らしい製品です！', 5),
        (1, '佐藤花子', 'コスパが良いです', 4),
        (2, '鈴木一郎', '使いやすいマウスです', 5),
        (3, '田中次郎', '初心者にわかりやすい', 4),
    ]
    
    cursor.executemany(
        'INSERT INTO reviews (product_id, author, comment, rating) VALUES (?, ?, ?, ?)',
        reviews
    )
    
    # サンプルゲストブックデータ
    guestbook_entries = [
        ('山田太郎', 'はじめまして！素敵なサイトですね。'),
        ('佐藤花子', 'とても参考になりました。ありがとうございます！'),
        ('田中一郎', 'また訪問します。'),
    ]
    
    cursor.executemany(
        'INSERT INTO guestbook (name, comment) VALUES (?, ?)',
        guestbook_entries
    )
    
    conn.commit()
    conn.close()
    
    print('\n✅ データベースの初期化が完了しました')
    print('📊 商品数:', len(products))
    print('💬 レビュー数:', len(reviews))
    print('📝 ゲストブック件数:', len(guestbook_entries))

if __name__ == '__main__':
    init_database()
