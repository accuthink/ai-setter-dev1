#!/bin/bash

# AI Appointment Setter - ngrok Setup Script
# Exposes local server for Telnyx webhook testing

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Starting ngrok tunnel${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo -e "${YELLOW}ngrok is not installed.${NC}\n"
    echo "Install ngrok:"
    echo "  macOS:   brew install ngrok"
    echo "  Other:   https://ngrok.com/download"
    echo ""
    exit 1
fi

echo -e "${GREEN}Starting ngrok on port 8000...${NC}\n"
echo "Once ngrok starts, use the HTTPS URL in Telnyx:"
echo "  • Custom LLM Base URL: https://your-ngrok-url.ngrok.io/v1"
echo ""
echo -e "${YELLOW}Press CTRL+C to stop ngrok${NC}\n"

# Start ngrok
exec ngrok http 8000
