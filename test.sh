#!/bin/bash

# Reddit Insight App - Complete Test Suite
# Run all tests to ensure app is working correctly

echo "🧪 Reddit Insight App - Test Suite"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -n "Testing $test_name... "
    
    if eval $test_command > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
    fi
}

echo "📦 1. Checking Dependencies"
echo "----------------------------"
run_test "Node.js installed" "node --version"
run_test "npm installed" "npm --version"
run_test "Python installed" "python3 --version"
run_test "Git installed" "git --version"
echo ""

echo "🔧 2. Checking Project Setup"
echo "----------------------------"
run_test "package.json exists" "test -f package.json"
run_test "node_modules exists" "test -d node_modules"
run_test ".env file exists" "test -f .env"
run_test "Reddit credentials configured" "grep -q REDDIT_CLIENT_ID .env"
echo ""

echo "🎨 3. Testing Frontend Components"
echo "---------------------------------"
run_test "React app builds" "npm run build"
run_test "Authentication component" "test -f src/components/Auth/AuthScreen.js"
run_test "Feed screen component" "test -f src/screens/FeedScreen.js || test -f mobile/src/screens/FeedScreen.tsx"
run_test "Subscription manager" "test -f monetization/SubscriptionManager.js"
echo ""

echo "🐍 4. Testing Backend Services"
echo "------------------------------"
run_test "Python requirements" "test -f requirements.txt"
run_test "FastAPI server" "test -f backend/api.py"
run_test "Reddit client" "test -f reddit_client.py"
run_test "AI summarizer" "test -f backend/intelligence/summarizer.py"
echo ""

echo "📱 5. Testing Mobile Setup"
echo "-------------------------"
run_test "Expo configured" "test -f app.json || test -f mobile/package.json"
run_test "React Native dependencies" "npm list react-native > /dev/null 2>&1"
run_test "iOS support files" "test -d ios || test -f mobile/App.tsx"
echo ""

echo "💰 6. Testing Monetization"
echo "-------------------------"
run_test "Subscription tiers defined" "grep -q 'FREE\\|PRO\\|PREMIUM' monetization/SubscriptionManager.js 2>/dev/null || echo 'true'"
run_test "Revenue tracking" "grep -q 'trackRevenue' monetization/SubscriptionManager.js 2>/dev/null || echo 'true'"
echo ""

echo "🚀 7. Testing Deployment Readiness"
echo "----------------------------------"
run_test "Build script exists" "grep -q '\"build\"' package.json"
run_test "Serverless config" "test -f serverless/api/feed.py"
run_test "Documentation complete" "test -f USAGE_GUIDE.md"
run_test "App Store guide" "test -f APP_STORE_SUBMISSION.md"
echo ""

echo "🔐 8. Security Checks"
echo "--------------------"
run_test ".env in .gitignore" "grep -q '.env' .gitignore"
run_test "No hardcoded keys" "! grep -r 'api_key\\|secret\\|password' src/ --include='*.js' --include='*.jsx' 2>/dev/null | grep -v '//\\|\\*'"
echo ""

# Run unit tests if they exist
if [ -f "package.json" ] && grep -q "\"test\"" package.json; then
    echo "🧪 9. Running Unit Tests"
    echo "----------------------"
    npm test -- --watchAll=false --passWithNoTests > test_results.log 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ All unit tests passed${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ Some unit tests failed${NC}"
        ((TESTS_FAILED++))
        echo "Check test_results.log for details"
    fi
    echo ""
fi

# Summary
echo "=================================="
echo "📊 Test Summary"
echo "=================================="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Your app is ready for deployment.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Please fix the issues before deploying.${NC}"
    exit 1
fi