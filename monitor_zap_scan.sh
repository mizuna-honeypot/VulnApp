#!/bin/bash

# ZAPスキャン監視スクリプト
LOG_FILE="zap_scan_monitor.log"
STATS_FILE="zap_scan_stats.txt"
ACCESS_LOG="flask.log"

echo "========================================"
echo "ZAPスキャン監視開始: $(date)"
echo "========================================"

# 既存のログをクリア
> $LOG_FILE
> $STATS_FILE

echo "監視中... (Ctrl+Cで停止)"
echo ""

# リアルタイム監視
tail -f flask.log 2>/dev/null | while read line; do
    echo "$line" | tee -a $LOG_FILE
    
    # リクエスト数をカウント
    if [[ $line =~ GET|POST|PUT|DELETE ]]; then
        REQ_COUNT=$(grep -c "GET\|POST\|PUT\|DELETE" $LOG_FILE)
        echo -ne "\r総リクエスト数: $REQ_COUNT  "
    fi
done
