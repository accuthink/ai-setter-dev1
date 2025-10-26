#!/bin/bash

# Test the greeting functionality
# This simulates what Telnyx sends on the first call

DEVTUNNEL_URL="${1:-http://localhost:8000}"

echo "🧪 Testing Greeting Functionality"
echo "=================================="
echo ""
echo "Testing against: $DEVTUNNEL_URL"
echo ""

# Test 1: Empty messages array (very first call)
echo "Test 1: First call with empty messages array"
echo "---------------------------------------------"
curl -X POST "$DEVTUNNEL_URL/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": []
  }' | jq '.choices[0].message.content'

echo ""
echo ""

# Test 2: Only system message (Telnyx might send this)
echo "Test 2: First call with only system message"
echo "--------------------------------------------"
curl -X POST "$DEVTUNNEL_URL/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant"}
    ]
  }' | jq '.choices[0].message.content'

echo ""
echo ""

# Test 3: User says hello (second interaction)
echo "Test 3: User says hello (should use OpenAI)"
echo "-------------------------------------------"
curl -X POST "$DEVTUNNEL_URL/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "Hello"}
    ]
  }' | jq '.choices[0].message.content'

echo ""
echo ""
echo "✅ Test complete!"
echo ""
echo "Expected results:"
echo "  Test 1 & 2: Should return greeting from application"
echo "  Test 3: Should return response from OpenAI with persona"
echo ""
