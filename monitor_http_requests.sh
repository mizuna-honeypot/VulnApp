#!/bin/bash

# HTTPリクエスト監視スクリプト
# Flaskのログから/guestbook関連のリクエストを抽出

LOG_FILE="/tmp/vulnapp.log"
MONITOR_LOG="/tmp/http_monitor.log"

echo "========================================" | tee -a $MONITOR_LOG
echo "HTTP Request Monitoring Started: $(date)" | tee -a $MONITOR_LOG
echo "Target: /guestbook endpoint" | tee -a $MONITOR_LOG
echo "========================================" | tee -a $MONITOR_LOG
echo "" | tee -a $MONITOR_LOG

# リアルタイムでログを監視
tail -f $LOG_FILE 2>/dev/null | while read -r line; do
    # /guestbook関連のリクエストを検出
    if echo $line | grep -qE '/guestbook'; then
        echo "" | tee -a $MONITOR_LOG
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Guestbook Request:" | tee -a $MONITOR_LOG
        echo "$line" | tee -a $MONITOR_LOG
        
        # POSTリクエストを特別にマーク
        if echo $line | grep -q 'POST'; then
            echo "🔴 [POST REQUEST DETECTED]" | tee -a $MONITOR_LOG
        fi
        
        # GETリクエストの検出
        if echo $line | grep -q 'GET'; then
            echo "🔵 [GET REQUEST DETECTED]" | tee -a $MONITOR_LOG
        fi
        
        echo "" | tee -a $MONITOR_LOG
    fi
done
