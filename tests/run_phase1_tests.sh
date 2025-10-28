#!/bin/bash

# Phase 1 Integration Test Runner

echo "=============================================="
echo "VulnApp Phase 1 - Full Test Suite"
echo "=============================================="

# Check if server is running
if ! curl -s http://localhost:5000 > /dev/null; then
    echo "❌ Error: VulnApp server is not running"
    echo "Please start the server with: python app.py"
    exit 1
fi

echo "✅ Server is running"

# Run CSRF tests
echo -e "\n\n#################### CSRF TESTS ####################"
bash test_csrf.sh

# Run Command Injection tests
echo -e "\n\n#################### COMMAND INJECTION TESTS ####################"
bash test_command_injection.sh

# Run Vulnerable Components tests
echo -e "\n\n#################### VULNERABLE COMPONENTS TESTS ####################"
bash test_vulnerable_components.sh

echo -e "\n\n=============================================="
echo "✅ All Phase 1 tests completed!"
echo "=============================================="
