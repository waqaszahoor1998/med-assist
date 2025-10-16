#!/bin/bash

echo "=================================================="
echo "🧪 FRONTEND ENDPOINTS TEST - POST CLEANUP"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8000/api"

# Test counter
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local auth_header=$5
    
    echo -n "Testing: $name ... "
    
    if [ "$method" == "GET" ]; then
        if [ -z "$auth_header" ]; then
            response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/$endpoint")
        else
            response=$(curl -s -o /dev/null -w "%{http_code}" -H "$auth_header" "$BASE_URL/$endpoint")
        fi
    elif [ "$method" == "POST" ]; then
        if [ -z "$auth_header" ]; then
            response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$BASE_URL/$endpoint")
        else
            response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -H "$auth_header" -d "$data" "$BASE_URL/$endpoint")
        fi
    elif [ "$method" == "PUT" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -X PUT -H "Content-Type: application/json" -H "$auth_header" -d "$data" "$BASE_URL/$endpoint")
    elif [ "$method" == "DELETE" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE -H "$auth_header" "$BASE_URL/$endpoint")
    fi
    
    if [ "$response" == "200" ] || [ "$response" == "201" ]; then
        echo -e "${GREEN}✅ PASS${NC} ($response)"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} ($response)"
        ((FAILED++))
    fi
}

# ========================================================================
# 1. AUTHENTICATION ENDPOINTS (No auth required)
# ========================================================================
echo "1️⃣  AUTHENTICATION ENDPOINTS"
echo "----------------------------------------"

test_endpoint "Ping API" "GET" "ping/" "" ""
test_endpoint "User Login" "POST" "auth/login/" '{"username":"waqas","password":"123123123"}' ""

# Get token for authenticated tests
echo ""
echo "Getting authentication token..."
TOKEN=$(curl -s -X POST "$BASE_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"waqas","password":"123123123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['tokens']['access'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Failed to get authentication token${NC}"
    exit 1
fi

AUTH_HEADER="Authorization: Bearer $TOKEN"
echo -e "${GREEN}✅ Got authentication token${NC}"
echo ""

# ========================================================================
# 2. PRESCRIPTION ENDPOINTS (Frontend uses these)
# ========================================================================
echo "2️⃣  PRESCRIPTION ENDPOINTS"
echo "----------------------------------------"

test_endpoint "Analyze Prescription" "POST" "prescription/analyze/" '{"text":"Take Paracetamol 500mg twice daily"}' "$AUTH_HEADER"
test_endpoint "Get Prescription History" "GET" "prescription/history/?limit=10" "" "$AUTH_HEADER"

echo ""

# ========================================================================
# 3. NOTIFICATION ENDPOINTS (Frontend uses these)
# ========================================================================
echo "3️⃣  NOTIFICATION ENDPOINTS"
echo "----------------------------------------"

test_endpoint "Get All Notifications" "GET" "notifications/" "" "$AUTH_HEADER"
test_endpoint "Get Unread Count" "GET" "notifications/unread-count/" "" "$AUTH_HEADER"
test_endpoint "Mark All Read" "POST" "notifications/mark-all-read/" "" "$AUTH_HEADER"

echo ""

# ========================================================================
# 4. REMINDER ENDPOINTS (Frontend uses these - NEW FORMAT)
# ========================================================================
echo "4️⃣  REMINDER ENDPOINTS (New Database-Backed)"
echo "----------------------------------------"

# Test GET reminders/list/ (new format)
test_endpoint "Get Reminders List" "GET" "reminders/list/" "" "$AUTH_HEADER"

# Test POST reminders/create/ (new format)
test_endpoint "Create Reminder" "POST" "reminders/create/" '{"medicine_name":"Test Medicine","dosage":"100mg","frequency":"daily","reminder_times":["08:00"],"notes":"Test reminder"}' "$AUTH_HEADER"

# Get a reminder ID for update/delete tests
REMINDER_ID=$(curl -s -H "$AUTH_HEADER" "$BASE_URL/reminders/list/" | \
  python3 -c "import sys, json; data = json.load(sys.stdin); print(data['reminders'][0]['id'] if data.get('reminders') else '')" 2>/dev/null)

if [ -n "$REMINDER_ID" ]; then
    test_endpoint "Update Reminder" "PUT" "reminders/$REMINDER_ID/update/" '{"active":false}' "$AUTH_HEADER"
    # Note: Not deleting to preserve data
    echo "   ℹ️  Delete endpoint available: DELETE reminders/$REMINDER_ID/delete/"
fi

test_endpoint "Trigger Notifications" "POST" "reminders/trigger-notifications/" "" "$AUTH_HEADER"
test_endpoint "Get Reminder Stats" "GET" "reminders/stats/" "" "$AUTH_HEADER"

echo ""

# ========================================================================
# 5. PROFILE ENDPOINTS (Frontend uses these)
# ========================================================================
echo "5️⃣  PROFILE ENDPOINTS"
echo "----------------------------------------"

test_endpoint "Get User Profile" "GET" "auth/profile/" "" "$AUTH_HEADER"
test_endpoint "Update User Profile" "PUT" "auth/profile/update/" '{"first_name":"Test","last_name":"User"}' "$AUTH_HEADER"

echo ""

# ========================================================================
# 6. MEDICAL KNOWLEDGE ENDPOINTS (Frontend uses these)
# ========================================================================
echo "6️⃣  MEDICAL KNOWLEDGE ENDPOINTS"
echo "----------------------------------------"

test_endpoint "Search Medical Knowledge" "GET" "medical-knowledge/search/?query=diabetes" "" "$AUTH_HEADER"
test_endpoint "Get Medical Stats" "GET" "medical-knowledge/stats/" "" "$AUTH_HEADER"

echo ""

# ========================================================================
# 7. MEDICINE SEARCH ENDPOINTS (Frontend uses these)
# ========================================================================
echo "7️⃣  MEDICINE SEARCH ENDPOINTS"
echo "----------------------------------------"

test_endpoint "Search Medicines" "GET" "medicines/search/?query=aspirin" "" "$AUTH_HEADER"

echo ""

# ========================================================================
# 8. VERIFY OLD ENDPOINTS ARE REMOVED
# ========================================================================
echo "8️⃣  VERIFY LEGACY ENDPOINTS REMOVED"
echo "----------------------------------------"

# These should return 404 or not be accessible
echo -n "Checking legacy reminders/ endpoint ... "
OLD_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/reminders/")
if [ "$OLD_RESPONSE" == "404" ] || [ "$OLD_RESPONSE" == "405" ]; then
    echo -e "${GREEN}✅ REMOVED${NC} (returns $OLD_RESPONSE)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  STILL EXISTS${NC} (returns $OLD_RESPONSE)"
    ((FAILED++))
fi

echo -n "Checking legacy reminders/set/ endpoint ... "
OLD_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/reminders/set/")
if [ "$OLD_RESPONSE" == "404" ] || [ "$OLD_RESPONSE" == "405" ]; then
    echo -e "${GREEN}✅ REMOVED${NC} (returns $OLD_RESPONSE)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  STILL EXISTS${NC} (returns $OLD_RESPONSE)"
    ((FAILED++))
fi

echo -n "Checking legacy user/profile/ endpoint ... "
OLD_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/user/profile/")
if [ "$OLD_RESPONSE" == "404" ] || [ "$OLD_RESPONSE" == "405" ]; then
    echo -e "${GREEN}✅ REMOVED${NC} (returns $OLD_RESPONSE)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  STILL EXISTS${NC} (returns $OLD_RESPONSE)"
    ((FAILED++))
fi

echo ""

# ========================================================================
# SUMMARY
# ========================================================================
echo "=================================================="
echo "📊 TEST SUMMARY"
echo "=================================================="
echo ""
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo ""
    echo "✅ Backend cleanup successful!"
    echo "✅ All frontend endpoints working!"
    echo "✅ Legacy endpoints properly removed!"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
    echo ""
    echo "Please check the failed endpoints above."
    echo ""
    exit 1
fi

