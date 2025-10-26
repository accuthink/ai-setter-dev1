#!/bin/bash

# AI Appointment Setter - Local Development Startup Script
# This script sets up and starts the application for local development
#
# Usage:
#   ./scripts/start-local.sh [environment]
#   environment: local (default), test, production

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the project root directory (parent of scripts folder)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Determine environment (default to local)
ENVIRONMENT="${1:-local}"

# Convert to uppercase (compatible with zsh/bash 3.x)
ENVIRONMENT_UPPER=$(echo "$ENVIRONMENT" | tr '[:lower:]' '[:upper:]')

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AI Appointment Setter - ${ENVIRONMENT_UPPER} Startup${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Step 1: Check Python version
echo -e "${YELLOW}[1/6] Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Found Python $PYTHON_VERSION${NC}\n"

# Step 2: Create virtual environment if it doesn't exist
echo -e "${YELLOW}[2/6] Setting up virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    echo "Creating new virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}\n"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}\n"
fi

# Step 3: Activate virtual environment and install dependencies
echo -e "${YELLOW}[3/6] Installing dependencies...${NC}"
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip > /dev/null 2>&1

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}\n"
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

# Step 4: Check for .env file and load environment-specific config
echo -e "${YELLOW}[4/6] Checking environment configuration...${NC}"

# Check if environment-specific config exists
ENV_FILE="env/.env.${ENVIRONMENT}"
if [ -f "$ENV_FILE" ]; then
    echo -e "${GREEN}✓ Found environment config: $ENV_FILE${NC}"
    
    # Copy environment-specific config to .env
    if [ -f ".env" ]; then
        echo -e "${YELLOW}⚠️  Backing up existing .env to .env.backup${NC}"
        cp .env .env.backup
    fi
    
    cp "$ENV_FILE" .env
    echo -e "${GREEN}✓ Loaded $ENVIRONMENT environment configuration${NC}"
else
    echo -e "${YELLOW}⚠️  Environment file $ENV_FILE not found${NC}"
    
    # Fall back to .env or .env.example
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo -e "${YELLOW}⚠️  Please edit .env and add your API keys:${NC}"
            echo -e "   - OPENAI_API_KEY"
            echo -e "   - TELNYX_API_KEY"
            echo -e "   - PERSONA_NAME (default, medical_clinic, salon_spa)"
            echo -e "   - BUSINESS_NAME\n"
            echo -e "${YELLOW}Press Enter after updating .env to continue...${NC}"
            read -r
        else
            echo -e "${RED}❌ .env.example not found${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ Using existing .env file${NC}"
    fi
fi

# Validate .env file has required keys
if [ -f ".env" ]; then
    # Check if required keys are set
    if grep -q "OPENAI_API_KEY=your_openai" .env || grep -q "OPENAI_API_KEY=$" .env || grep -q "OPENAI_API_KEY=\"\"" .env; then
        echo -e "${YELLOW}⚠️  OPENAI_API_KEY is not set in .env${NC}"
        echo -e "   Please update .env with your OpenAI API key"
    else
        echo -e "${GREEN}✓ OPENAI_API_KEY is configured${NC}"
    fi
    
    if grep -q "PERSONA_NAME=" .env; then
        PERSONA=$(grep "PERSONA_NAME=" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        echo -e "${GREEN}✓ Using persona: $PERSONA${NC}"
    fi
    
    if grep -q "BUSINESS_NAME=" .env; then
        BUSINESS=$(grep "BUSINESS_NAME=" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        echo -e "${GREEN}✓ Business name: $BUSINESS${NC}"
    fi
    
    if grep -q "ENV=" .env; then
        CURRENT_ENV=$(grep "^ENV=" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        echo -e "${GREEN}✓ Environment: $CURRENT_ENV${NC}"
    fi
    echo ""
fi

# Step 5: List available personas
echo -e "${YELLOW}[5/6] Available personas:${NC}"
if [ -d "app/personas" ]; then
    for persona in app/personas/*.txt; do
        basename "$persona" .txt | sed 's/^/  • /'
    done
    echo ""
else
    echo -e "${RED}❌ app/personas directory not found${NC}"
fi

# Step 6: Start the application
echo -e "${YELLOW}[6/6] Starting FastAPI server...${NC}\n"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Server starting on http://0.0.0.0:8000${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Available endpoints:"
echo "  • http://localhost:8000/health"
echo "  • http://localhost:8000/v1/chat/completions"
echo "  • http://localhost:8000/telnyx/ai"
echo "  • http://localhost:8000/telnyx/call-control"
echo ""
echo "API Documentation:"
echo "  • http://localhost:8000/docs (Swagger UI)"
echo "  • http://localhost:8000/redoc (ReDoc)"
echo ""
echo -e "${YELLOW}Press CTRL+C to stop the server${NC}\n"

# Start uvicorn with reload for development using the venv python
exec .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
