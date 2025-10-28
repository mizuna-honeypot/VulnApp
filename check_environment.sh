#!/bin/bash

echo "========================================="
echo "VulnApp環境チェック"
echo "========================================="
echo ""

echo "✅ 1. アプリケーションの起動状態"
if pgrep -f "python3 app.py" > /dev/null; then
    echo "   [OK] アプリケーションは起動中"
    ps aux | grep "python3 app.py" | grep -v grep
else
    echo "   [NG] アプリケーションが起動していません"
fi
echo ""

echo "✅ 2. ポート5000のリスニング状態"
sudo lsof -i :5000 2>/dev/null || echo "   [NG] ポート5000がリスニングしていません"
echo ""

echo "✅ 3. データベースの状態"
if [ -f "vulnapp.db" ]; then
    echo "   [OK] データベースファイル存在"
    echo "   商品数: $(sqlite3 vulnapp.db 'SELECT COUNT(*) FROM products')"
    echo "   レビュー数: $(sqlite3 vulnapp.db 'SELECT COUNT(*) FROM reviews')"
else
    echo "   [NG] データベースファイルが見つかりません"
fi
echo ""

echo "✅ 4. HTTPレスポンステスト"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/")
if [ "$HTTP_CODE" = "200" ]; then
    echo "   [OK] HTTPレスポンス: $HTTP_CODE"
else
    echo "   [NG] HTTPレスポンス: $HTTP_CODE"
fi
echo ""

echo "✅ 5. 主要エンドポイントのテスト"
for endpoint in "/" "/products" "/product/1" "/files" "/api/info"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000${endpoint}")
    echo "   ${endpoint}: $STATUS"
done
echo ""

echo "✅ 6. パブリックIPアドレス"
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null)
if [ -n "$PUBLIC_IP" ]; then
    echo "   パブリックIP: $PUBLIC_IP"
    echo "   スキャンURL: http://$PUBLIC_IP:5000"
else
    echo "   [INFO] EC2メタデータから取得できません"
fi
echo ""

echo "========================================="
echo "環境チェック完了"
echo "========================================="
