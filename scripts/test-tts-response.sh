#!/bin/bash
#
# Test TTS Response Format
# This script tests if your /chat/completions endpoint returns valid content
# that Telnyx can convert to speech.
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default to localhost
BASE_URL="${1:-http://localhost:8000}"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Testing TTS Response Format${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Testing endpoint: ${BASE_URL}${NC}"
echo ""

# Test 1: Simple greeting (first interaction)
echo -e "${BLUE}Test 1: First Interaction (Should include greeting)${NC}"
RESPONSE=$(curl -s -X POST "${BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "system", "content": "Use external LLM only."},
      {"role": "user", "content": "Hello"}
    ]
  }')

echo "$RESPONSE" | jq '.'

# Check if content exists and has length
CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content')
CONTENT_LENGTH=${#CONTENT}

echo ""
if [ $CONTENT_LENGTH -gt 0 ]; then
    echo -e "${GREEN}✅ Content exists: ${CONTENT_LENGTH} characters${NC}"
    echo -e "${GREEN}Content: ${CONTENT:0:200}...${NC}"
else
    echo -e "${RED}❌ No content in response!${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Test 2: Follow-up message (no greeting)
echo -e "${BLUE}Test 2: Follow-up Message (No greeting)${NC}"
RESPONSE2=$(curl -s -X POST "${BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "system", "content": "Use external LLM only."},
      {"role": "assistant", "content": "Hello! How can I help you?"},
      {"role": "user", "content": "I need to book an appointment"}
    ]
  }')

echo "$RESPONSE2" | jq '.'

CONTENT2=$(echo "$RESPONSE2" | jq -r '.choices[0].message.content')
CONTENT2_LENGTH=${#CONTENT2}

echo ""
if [ $CONTENT2_LENGTH -gt 0 ]; then
    echo -e "${GREEN}✅ Content exists: ${CONTENT2_LENGTH} characters${NC}"
    echo -e "${GREEN}Content: ${CONTENT2:0:200}...${NC}"
else
    echo -e "${RED}❌ No content in response!${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Test 3: Check models endpoint
echo -e "${BLUE}Test 3: Models Endpoint${NC}"
MODELS=$(curl -s "${BASE_URL}/models")
echo "$MODELS" | jq '.'

MODEL_COUNT=$(echo "$MODELS" | jq '.data | length')
echo ""
if [ $MODEL_COUNT -gt 0 ]; then
    echo -e "${GREEN}✅ Models endpoint working: ${MODEL_COUNT} models available${NC}"
else
    echo -e "${RED}❌ No models returned${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ All tests passed!${NC}"
echo ""
echo -e "${YELLOW}What to check in Telnyx Portal if TTS still doesn't work:${NC}"
echo -e "  1. AI Assistant → Voice Tab → Provider/Model/Voice configured"
echo -e "  2. AI Assistant → Voice Tab → All Speaking Plan sliders set to 0s"
echo -e "  3. Phone Number → AI Assistant enabled and linked"
echo -e "  4. Check Telnyx Portal call logs for TTS errors"
echo ""
echo -e "${BLUE}See TTS_TROUBLESHOOTING.md for detailed guidance${NC}"
echo ""
