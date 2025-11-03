#!/bin/bash

# 統合監視スクリプト
# Guestbookのデータベース変更とHTTPリクエストを同時監視

echo "========================================"
echo "Starting Comprehensive Guestbook Monitoring"
echo "========================================"
echo ""
echo "Monitoring targets:"
echo "  1. Database changes (~/VulnApp/vulnapp.db)"
echo "  2. HTTP requests (/tmp/vulnapp.log)"
echo ""
echo "Log files:"
echo "  - /tmp/guestbook_monitor.log"
echo "  - /tmp/http_monitor.log"
echo ""
echo "Press Ctrl+C to stop all monitors"
echo ""

# 既存のログファイルをクリア
> /tmp/guestbook_monitor.log
> /tmp/http_monitor.log

# データベース監視をバックグラウンドで起動
~/VulnApp/monitor_guestbook.sh &
DB_MONITOR_PID=$!

# HTTPリクエスト監視をバックグラウンドで起動
~/VulnApp/monitor_http_requests.sh &
HTTP_MONITOR_PID=$!

echo "Monitoring started:"
echo "  - Database monitor PID: $DB_MONITOR_PID"
echo "  - HTTP monitor PID: $HTTP_MONITOR_PID"
echo ""

# Ctrl+C処理
trap "echo ''; echo 'Stopping monitors...'; kill $DB_MONITOR_PID $HTTP_MONITOR_PID 2>/dev/null; exit 0" INT

# 統合ログ表示
echo "========================================"
echo "Real-time Monitoring Output"
echo "========================================"
echo ""

tail -f /tmp/guestbook_monitor.log /tmp/http_monitor.log
