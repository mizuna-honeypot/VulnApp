#!/bin/bash

# Guestbook監視スクリプト
# TenableWASがどのようなペイロードを送信しているか監視

LOG_FILE="/tmp/guestbook_monitor.log"
DB_FILE="/home/ubuntu/VulnApp/vulnapp.db"

echo "========================================" | tee -a $LOG_FILE
echo "Guestbook Monitoring Started: $(date)" | tee -a $LOG_FILE
echo "========================================" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# 初期データベース状態
echo "[INFO] Initial database state:" | tee -a $LOG_FILE
sqlite3 $DB_FILE "SELECT COUNT(*) FROM guestbook;" 2>/dev/null | xargs -I {} echo "Total entries: {}" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# リアルタイム監視ループ
LAST_COUNT=$(sqlite3 $DB_FILE "SELECT COUNT(*) FROM guestbook;" 2>/dev/null)

echo "[INFO] Monitoring /guestbook endpoint..." | tee -a $LOG_FILE
echo "[INFO] Press Ctrl+C to stop" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

while true; do
    CURRENT_COUNT=$(sqlite3 $DB_FILE "SELECT COUNT(*) FROM guestbook;" 2>/dev/null)
    
    if [ $CURRENT_COUNT -gt $LAST_COUNT ]; then
        NEW_ENTRIES=$((CURRENT_COUNT - LAST_COUNT))
        echo "" | tee -a $LOG_FILE
        echo "[ALERT] $NEW_ENTRIES new entries detected at $(date)" | tee -a $LOG_FILE
        echo "========================================" | tee -a $LOG_FILE
        
        # 最新のエントリを表示
        sqlite3 $DB_FILE "SELECT id, name, comment, created_at FROM guestbook ORDER BY id DESC LIMIT $NEW_ENTRIES;" 2>/dev/null | while IFS='|' read -r id name comment created_at; do
            echo "" | tee -a $LOG_FILE
            echo "Entry ID: $id" | tee -a $LOG_FILE
            echo "Name: $name" | tee -a $LOG_FILE
            echo "Comment: $comment" | tee -a $LOG_FILE
            echo "Created: $created_at" | tee -a $LOG_FILE
            echo "---" | tee -a $LOG_FILE
            
            # XSSペイロード検出
            if echo $comment | grep -qiE '<script|onerror|onload|javascript:|alert\(|<img'; then
                echo "⚠️  [XSS PAYLOAD DETECTED]" | tee -a $LOG_FILE
            fi
            
            # SQLインジェクション検出
            if echo $comment | grep -qiE 'UNION|SELECT|DROP|INSERT|UPDATE|DELETE|--|;'; then
                echo "⚠️  [SQL INJECTION PATTERN DETECTED]" | tee -a $LOG_FILE
            fi
            
            echo "" | tee -a $LOG_FILE
        done
        
        echo "========================================" | tee -a $LOG_FILE
        LAST_COUNT=$CURRENT_COUNT
    fi
    
    sleep 2
done
