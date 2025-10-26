#!/bin/bash

# Test Telnyx Call Control Webhook
# This simulates a call.initiated event from Telnyx

DEVTUNNEL_URL="${1}"

if [ -z "$DEVTUNNEL_URL" ]; then
    echo "Usage: ./scripts/test-call-webhook.sh <your-devtunnel-url>"
    echo "Example: ./scripts/test-call-webhook.sh https://abc123-8000.usw2.devtunnels.ms"
    exit 1
fi

echo "Testing Telnyx webhook endpoints..."
echo "======================================"

# Test status endpoint
echo ""
echo "1. Testing status endpoint..."
curl -s "$DEVTUNNEL_URL/telnyx/status" | jq '.'

# Test models endpoint
echo ""
echo "2. Testing models endpoint..."
curl -s "$DEVTUNNEL_URL/models" | jq '.data[0]'

# Simulate a call.initiated webhook
echo ""
echo "3. Simulating call.initiated webhook..."
echo "(Note: This will fail to answer because it's a fake call_control_id)"
curl -X POST "$DEVTUNNEL_URL/telnyx/call-control" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "event_type": "call.initiated",
      "payload": {
        "call_control_id": "v3:test-call-control-id-12345",
        "call_leg_id": "test-call-leg-id-67890",
        "direction": "incoming",
        "from": "+15555551234",
        "to": "+15555559999",
        "state": "parked"
      }
    }
  }' | jq '.'

echo ""
echo "======================================"
echo "✅ If you see JSON responses above, your webhooks are working!"
echo ""
echo "Next steps:"
echo "1. In Telnyx Portal, set webhook URL to: $DEVTUNNEL_URL/telnyx/call-control"
echo "2. Configure AI Assistant with Base URL: $DEVTUNNEL_URL"
echo "3. Make a real test call to your Telnyx number"
echo ""
