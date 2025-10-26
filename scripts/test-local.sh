#!/bin/bash

# AI Appointment Setter - Local Testing Script
# Quick tests to verify the application is running correctly

set -e

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_URL="http://localhost:8000"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Testing AI Appointment Setter${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Test 1: Health check
echo -e "${YELLOW}[1/3] Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s "$BASE_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q "true"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "   Response: $HEALTH_RESPONSE"
    exit 1
fi
echo ""

# Test 2: Test chat completions endpoint (requires OPENAI_API_KEY)
echo -e "${YELLOW}[2/3] Testing chat completions endpoint...${NC}"
CHAT_RESPONSE=$(curl -s -X POST "$BASE_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "Hello, I need to book an appointment"}
        ],
        "temperature": 0.7
    }')

if echo "$CHAT_RESPONSE" | grep -q "error"; then
    echo -e "${YELLOW}⚠️  Chat completions returned an error (check if OPENAI_API_KEY is set)${NC}"
    echo "   Error: $(echo $CHAT_RESPONSE | head -c 200)"
elif echo "$CHAT_RESPONSE" | grep -q "choices"; then
    echo -e "${GREEN}✓ Chat completions working${NC}"
    echo "   Model responded successfully"
else
    echo -e "${RED}❌ Unexpected response${NC}"
    echo "   Response: $(echo $CHAT_RESPONSE | head -c 200)"
fi
echo ""

# Test 3: Test Telnyx webhook endpoints
echo -e "${YELLOW}[3/3] Testing Telnyx webhook endpoints...${NC}"
AI_RESPONSE=$(curl -s -X POST "$BASE_URL/telnyx/ai" \
    -H "Content-Type: application/json" \
    -d '{"test": "data"}')

if echo "$AI_RESPONSE" | grep -q "assistant"; then
    echo -e "${GREEN}✓ Telnyx AI webhook accessible${NC}"
else
    echo -e "${RED}❌ Telnyx AI webhook failed${NC}"
fi

CONTROL_RESPONSE=$(curl -s -X POST "$BASE_URL/telnyx/call-control" \
    -H "Content-Type: application/json" \
    -d '{"data": {"event_type": "call.initiated"}}')

if echo "$CONTROL_RESPONSE" | grep -q "received"; then
    echo -e "${GREEN}✓ Telnyx Call Control webhook accessible${NC}"
else
    echo -e "${RED}❌ Telnyx Call Control webhook failed${NC}"
fi
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Testing complete!${NC}"
echo -e "${BLUE}========================================${NC}\n"
echo "Next steps:"
echo "  1. Ensure .env has OPENAI_API_KEY set"
echo "  2. Configure Telnyx Custom LLM to point to this server"
echo "  3. Use ngrok to expose localhost for Telnyx webhooks:"
echo "     ${YELLOW}ngrok http 8000${NC}"
echo ""
