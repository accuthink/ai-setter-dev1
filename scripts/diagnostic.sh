#!/bin/bash

# Quick diagnostic script to verify everything is configured correctly

echo "🔍 AI Appointment Setter - Configuration Diagnostic"
echo "=================================================="
echo ""

# Check if .env.local exists
echo "1. Checking environment configuration..."
if [ -f "env/.env.local" ]; then
    echo "   ✅ env/.env.local found"
    
    # Check critical variables (without showing full keys)
    if grep -q "TELNYX_API_KEY" env/.env.local && [ -n "$(grep TELNYX_API_KEY env/.env.local | cut -d'=' -f2 | tr -d '"' | tr -d ' ')" ]; then
        echo "   ✅ TELNYX_API_KEY is set"
    else
        echo "   ❌ TELNYX_API_KEY is missing or empty"
    fi
    
    if grep -q "OPENAI_API_KEY" env/.env.local && [ -n "$(grep OPENAI_API_KEY env/.env.local | cut -d'=' -f2 | tr -d '"' | tr -d ' ')" ]; then
        echo "   ✅ OPENAI_API_KEY is set"
    else
        echo "   ❌ OPENAI_API_KEY is missing or empty"
    fi
    
    PERSONA_NAME=$(grep "^PERSONA_NAME" env/.env.local | cut -d'=' -f2 | tr -d '"' | tr -d ' ')
    if [ -n "$PERSONA_NAME" ]; then
        echo "   ✅ PERSONA_NAME=$PERSONA_NAME"
        
        # Check if persona file exists
        if [ -f "app/personas/${PERSONA_NAME}.txt" ]; then
            echo "   ✅ Persona file app/personas/${PERSONA_NAME}.txt exists"
        else
            echo "   ❌ Persona file app/personas/${PERSONA_NAME}.txt NOT FOUND"
        fi
    else
        echo "   ❌ PERSONA_NAME is missing"
    fi
    
    BUSINESS_NAME=$(grep "^BUSINESS_NAME" env/.env.local | cut -d'=' -f2 | tr -d '"')
    if [ -n "$BUSINESS_NAME" ]; then
        echo "   ✅ BUSINESS_NAME=$BUSINESS_NAME"
    else
        echo "   ⚠️  BUSINESS_NAME is not set"
    fi
else
    echo "   ❌ env/.env.local NOT FOUND"
fi

echo ""
echo "2. Checking Python environment..."
if [ -d ".venv" ]; then
    echo "   ✅ Virtual environment exists"
    
    if [ -f ".venv/bin/python" ]; then
        PYTHON_VERSION=$(.venv/bin/python --version 2>&1)
        echo "   ✅ Python: $PYTHON_VERSION"
    fi
else
    echo "   ❌ Virtual environment not found - run: python3 -m venv .venv"
fi

echo ""
echo "3. Checking application files..."
required_files=(
    "app/main.py"
    "app/routers/ai_voice.py"
    "app/services/persona_service.py"
    "app/core/config.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file NOT FOUND"
    fi
done

echo ""
echo "4. Checking if application is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Application is running on port 8000"
    
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
    echo "   Response: $HEALTH_RESPONSE"
else
    echo "   ❌ Application is NOT running"
    echo "   → Start it with: ./scripts/start-local.sh"
fi

echo ""
echo "5. Checking DevTunnel/ngrok..."
if command -v devtunnel &> /dev/null; then
    echo "   ✅ DevTunnel is installed"
else
    echo "   ⚠️  DevTunnel not found"
fi

if command -v ngrok &> /dev/null; then
    echo "   ✅ ngrok is installed"
else
    echo "   ⚠️  ngrok not found"
fi

# Check if any tunnel is running
if pgrep -x "devtunnel" > /dev/null; then
    echo "   ✅ DevTunnel process is running"
elif pgrep -x "ngrok" > /dev/null; then
    echo "   ✅ ngrok process is running"
else
    echo "   ❌ No tunnel is running"
    echo "   → Start DevTunnel: ./scripts/setup-devtunnel.sh"
    echo "   → Or start ngrok: ./scripts/setup-ngrok.sh"
fi

echo ""
echo "=================================================="
echo "📋 NEXT STEPS:"
echo ""
echo "If everything above shows ✅:"
echo "1. Copy your DevTunnel/ngrok URL"
echo "2. Configure it in Telnyx Portal:"
echo "   - AI Assistant Base URL: https://[your-url]"
echo "   - Phone Number Webhook: https://[your-url]/telnyx/call-control"
echo "3. Make a test call!"
echo ""
echo "If you see ❌ errors:"
echo "1. Fix the issues listed above"
echo "2. Run this diagnostic again"
echo "3. Check CALL_TROUBLESHOOTING.md for detailed help"
echo ""
