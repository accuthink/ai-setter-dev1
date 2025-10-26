#!/bin/bash

# AI Appointment Setter - DevTunnel Setup Script
# Exposes local server using Microsoft DevTunnel

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Starting DevTunnel for AI Appointment Setter${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if devtunnel is installed
if ! command -v devtunnel &> /dev/null; then
    echo -e "${RED}❌ DevTunnel is not installed.${NC}\n"
    echo "Install DevTunnel:"
    echo -e "  ${YELLOW}brew install --cask devtunnel${NC}"
    echo ""
    echo "Or download from:"
    echo "  https://aka.ms/devtunnels/download"
    echo ""
    exit 1
fi

# Check if user is logged in
if ! devtunnel user show &> /dev/null; then
    echo -e "${YELLOW}⚠️  You need to login to DevTunnel first.${NC}\n"
    echo "Running login command..."
    echo ""
    devtunnel user login
    echo ""
fi

echo -e "${GREEN}✓ DevTunnel is ready${NC}\n"
echo -e "${YELLOW}Starting tunnel on port 8000...${NC}\n"
echo -e "${BLUE}========================================${NC}"
echo -e "Once started, copy the HTTPS URL and use it in Telnyx:"
echo -e "  ${GREEN}Custom LLM Base URL:${NC} https://your-url.usw2.devtunnels.ms/v1"
echo -e "${BLUE}========================================${NC}\n"
echo -e "${YELLOW}Press CTRL+C to stop the tunnel${NC}\n"

# Start the tunnel with anonymous access
exec devtunnel host -p 8000 --allow-anonymous
