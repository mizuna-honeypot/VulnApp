#!/bin/bash

# Vulnerable Components Test Script

echo "=============================================="
echo "Vulnerable Components Detection Tests"
echo "=============================================="

echo -e "\n[INFO] Checking Python environment..."
python3 --version

echo -e "\n[TEST 1] Installing pip-audit in virtual environment..."
pip install pip-audit

echo -e "\n[TEST 2] Running pip-audit on requirements.txt..."
cd ..
pip-audit -r requirements.txt || echo "Some vulnerabilities found (expected)"

echo -e "\n[TEST 3] Checking installed packages..."
pip list | grep -E "Flask|Werkzeug|Jinja2"

echo -e "\n[TEST 4] Checking for known CVEs in JSON format..."
pip-audit --format json -r requirements.txt > /tmp/vulnerabilities.json 2>&1 || true
if [ -s /tmp/vulnerabilities.json ]; then
    cat /tmp/vulnerabilities.json | python3 -m json.tool | head -50
else
    echo "No JSON output (vulnerabilities may exist in text format above)"
fi

echo -e "\n[INFO] Alternative: Use OWASP Dependency-Check"
echo "Download from: https://github.com/jeremylong/DependencyCheck"
echo "Run: dependency-check.sh --project VulnApp --scan requirements.txt"

echo -e "\n✅ Vulnerable components scan completed"
