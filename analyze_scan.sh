#!/bin/bash

# ZAPスキャンログ分析スクリプト
LOG_FILE="flask.log"

echo "========================================"
echo "ZAPスキャン分析レポート"
echo "生成時刻: $(date)"
echo "========================================"
echo ""

if [ ! -f "$LOG_FILE" ]; then
    echo "エラー: $LOG_FILE が見つかりません"
    exit 1
fi

# 基本統計
echo "【基本統計】"
echo "---"
TOTAL_REQUESTS=$(grep -E '"(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)' $LOG_FILE | wc -l)
echo "総リクエスト数: $TOTAL_REQUESTS"

GET_COUNT=$(grep '"GET' $LOG_FILE | wc -l)
POST_COUNT=$(grep '"POST' $LOG_FILE | wc -l)
echo "  - GET:  $GET_COUNT"
echo "  - POST: $POST_COUNT"
echo ""

# ステータスコード統計
echo "【ステータスコード】"
echo "---"
grep -oE 'HTTP/[0-9.]+ [0-9]+' $LOG_FILE | awk '{print $2}' | sort | uniq -c | sort -rn | while read count code; do
    echo "  $code: $count 回"
done
echo ""

# アクセスされたエンドポイント（上位20）
echo "【アクセス頻度の高いエンドポイント（上位20）】"
echo "---"
grep -oE '"(GET|POST|PUT|DELETE) [^ ]+' $LOG_FILE | awk '{print $2}' | sort | uniq -c | sort -rn | head -20 | while read count path; do
    printf "  %5d 回: %s\n" $count "$path"
done
echo ""

# エラー検出
echo "【エラー・警告】"
echo "---"
ERROR_COUNT=$(grep -i 'error\|exception\|traceback' $LOG_FILE | wc -l)
echo "エラー/例外の総数: $ERROR_COUNT"

if [ $ERROR_COUNT -gt 0 ]; then
    echo ""
    echo "最近のエラー（最新10件）:"
    grep -i 'error\|exception\|traceback' $LOG_FILE | tail -10 | while read line; do
        echo "  - $line"
    done
fi
echo ""

# 脆弱性関連のアクセスパターン
echo "【脆弱性テストのパターン検出】"
echo "---"

SQL_INJECTION=$(grep -iE "(OR 1=1|UNION SELECT|'--|\\'|%27)" $LOG_FILE | wc -l)
XSS_TESTS=$(grep -iE '(<script|alert\(|onerror=|onload=|%3Cscript)' $LOG_FILE | wc -l)
PATH_TRAVERSAL=$(grep -E '(\.\./|%2e%2e|/etc/passwd)' $LOG_FILE | wc -l)
COMMAND_INJECTION=$(grep -iE '(;\s*(ls|cat|wget|curl)|\||&&)' $LOG_FILE | wc -l)

echo "  SQLインジェクション試行: $SQL_INJECTION 回"
echo "  XSSテスト試行: $XSS_TESTS 回"
echo "  パストラバーサル試行: $PATH_TRAVERSAL 回"
echo "  コマンドインジェクション試行: $COMMAND_INJECTION 回"
echo ""

# タイムライン（最初と最後のリクエスト）
echo "【スキャンタイムライン】"
echo "---"
FIRST_REQ=$(grep -E '"(GET|POST)' $LOG_FILE | head -1 | awk '{print $4" "$5}' | tr -d '[]')
LAST_REQ=$(grep -E '"(GET|POST)' $LOG_FILE | tail -1 | awk '{print $4" "$5}' | tr -d '[]')
echo "開始時刻: $FIRST_REQ"
echo "最終時刻: $LAST_REQ"
echo ""

echo "========================================"
echo "分析完了"
echo "========================================"
