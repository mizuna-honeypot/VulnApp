#!/bin/bash

echo "========================================"
echo "ZAPスキャン準備"
echo "========================================"
echo ""

# 現在のログをバックアップ
if [ -f flask.log ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    echo "📦 既存のログをバックアップ: flask.log.backup_$TIMESTAMP"
    cp flask.log flask.log.backup_$TIMESTAMP
fi

# ログファイルをクリア
echo "🧹 ログファイルをクリア"
> flask.log
> zap_scan_monitor.log 2>/dev/null

echo ""
echo "✅ 準備完了"
echo ""
echo "次のステップ:"
echo "  1. ZAPでスキャンを開始"
echo "  2. 別のターミナルで監視: ./monitor_zap_scan.sh"
echo "  3. スキャン完了後に分析: ./analyze_scan.sh"
echo ""
