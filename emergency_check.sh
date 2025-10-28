#!/bin/bash

echo "========================================="
echo "緊急診断"
echo "========================================="
echo ""

# Flask確認
echo "1. Flaskアプリケーション"
if pgrep -f "python3 app.py" > /dev/null; then
    echo "   ✅ Flask起動中"
    curl -s -o /dev/null -w "   ポート5000: HTTP %{http_code}\n" http://localhost:5000/
else
    echo "   ❌ Flask停止中"
fi

echo ""

# Nginx確認
echo "2. Nginx"
if systemctl is-active --quiet nginx; then
    echo "   ✅ Nginx起動中"
    curl -s -o /dev/null -w "   ポート80: HTTP %{http_code}\n" http://localhost:80/ 2>/dev/null || echo "   ⚠️ ポート80応答なし"
else
    echo "   ❌ Nginx停止中"
fi

echo ""

# パブリックIP
echo "3. アクセス情報"
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null)
if [ -n "$PUBLIC_IP" ]; then
    echo "   パブリックIP: $PUBLIC_IP"
    echo ""
    echo "   アクセスURL:"
    echo "   - Nginx経由: http://$PUBLIC_IP"
    echo "   - Flask直接: http://$PUBLIC_IP:5000"
else
    echo "   ⚠️ パブリックIP取得失敗"
fi

echo ""
echo "========================================="
