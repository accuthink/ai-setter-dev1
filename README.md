# AI Appointment Setter – Telnyx + OpenAI Integration

This service is a FastAPI backend for an AI appointment setter that integrates with **Telnyx** for telephony and **OpenAI** for conversational AI and speech orchestration.

## Key Features

- ✅ **Persona-driven conversations**: Configurable AI personalities per customer/business type
- ✅ **OpenAI-compatible endpoint**: Telnyx Custom LLM integration via `/v1/chat/completions`
- ✅ **Context injection**: Business details and persona automatically injected into every conversation
- ✅ **Appointment tools**: Book, reschedule, cancel, and find available slots
- ✅ **Voice-first design**: Built specifically for phone-based interactions

## What's Included

### API Endpoints

- **`/health`** – Health check endpoint
- **`/v1/chat/completions`** – OpenAI-compatible chat completions (for Telnyx Custom LLM)
- **`/telnyx/ai`** – Telnyx AI Assistant webhook (placeholder)
- **`/telnyx/call-control`** – Telnyx Call Control webhook (fallback for manual orchestration)

### Persona System

Pre-configured personas in `app/personas/`:
- `default.txt` – General-purpose appointment assistant
- `medical_clinic.txt` – Healthcare/medical office assistant (HIPAA-aware)
- `salon_spa.txt` – Beauty and wellness salon assistant

Each persona includes:
- Personality and tone guidelines
- Conversation flow best practices
- Information collection requirements
- Edge case handling instructions
- Business-specific context placeholders

## Environment Setup

Environment-specific configuration files are stored in the `env/` directory:
- `env/.env.local` - Local development
- `env/.env.test` - Test/staging environment
- `env/.env.production` - Production settings

### Quick Setup

1. **For local development** (recommended):
   ```bash
   ./scripts/start-local.sh
   ```
   This automatically loads `env/.env.local` configuration.

2. **Or manually configure**:
   ```bash
   cp env/.env.local .env
   ```
   Then edit `.env` with your API keys.

### Required Configuration

Edit your environment file and set:

```bash
# Telnyx credentials
TELNYX_API_KEY=your_telnyx_api_key_here
TELNYX_SIGNING_SECRET=your_signing_secret_here

# OpenAI credentials
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# AI Assistant configuration
PERSONA_NAME=default
BUSINESS_NAME=Acme Hair Salon
```

### Environment Selection

Start with a specific environment:

```bash
./scripts/start-local.sh local      # Local development (default)
./scripts/start-local.sh test       # Test environment
./scripts/start-local.sh production # Production settings
```

## Telnyx "Custom LLM" Configuration

Telnyx AI Assistants now support **Custom LLM** mode, which routes all model requests to your own endpoint while Telnyx handles voice orchestration, STT, and TTS.

### Setup Steps

1. **Go to Telnyx Mission Control Portal**
   - Navigate to: AI Assistants → Your Assistant → Agent tab

2. **Enable Custom LLM**
   - Check ☑️ "Use Custom LLM"

3. **Configure the endpoint**
   - **Base URL**: `https://your-domain.com/v1`
   - **Model Name**: `gpt-4o-mini` (or any name you prefer)
   - **Integration Secret**: Create a new secret with your `OPENAI_API_KEY`

4. **Test the connection**
   - Click "Validate Connection" in the portal
   - Save your assistant configuration

### What Happens When a Call Comes In

1. Customer calls your Telnyx phone number
2. Telnyx answers and starts voice AI assistant
3. Telnyx sends conversation turns to **your** `/v1/chat/completions` endpoint
4. **Your application**:
   - Loads the configured persona (e.g., `medical_clinic`)
   - Injects business context (name, date/time, services)
   - Forwards to OpenAI with tool definitions
   - Returns OpenAI's response (text + optional tool calls)
5. Telnyx converts response to speech and plays to customer
6. Repeat for each conversation turn

**This means YOUR application controls the conversation logic, not just Telnyx.**

## Local Development

### Quick Start

Use the startup script (handles everything automatically):

```bash
./scripts/start-local.sh
```

This will:
- Check Python version
- Create/activate virtual environment
- Install dependencies
- Load local environment configuration
- Start the FastAPI server on http://0.0.0.0:8000

### Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env/.env.local .env
# Edit .env with your API keys

# Start server
uvicorn app.main:app --reload --port 8000
```

### Expose locally with ngrok (for Telnyx webhooks)

Use the provided script:

```bash
./scripts/setup-ngrok.sh
```

Or manually:

```bash
ngrok http 8000
```

Use the ngrok HTTPS URL in Telnyx:
- Custom LLM Base URL: `https://your-ngrok-url.ngrok.io/v1`

## Scripts

The `scripts/` directory contains helper scripts:

- **`start-local.sh`** - Complete startup script with environment management
- **`test-local.sh`** - Run local integration tests
- **`setup-ngrok.sh`** - Start ngrok tunnel for webhook testing

### Usage Examples

```bash
# Start with local config (default)
./scripts/start-local.sh

# Start with test config
./scripts/start-local.sh test

# Test the running application
./scripts/test-local.sh

# Expose to Telnyx via ngrok
./scripts/setup-ngrok.sh
```

## Testing the Integration

### 1. Test the health endpoint

```bash
curl http://localhost:8000/health
```

Expected: `{"ok": true}`

### 2. Test chat completions locally

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "I need to book a haircut for tomorrow morning"}
    ]
  }'
```

This will:
- Load your configured persona
- Inject business context
- Forward to OpenAI
- Return the assistant's response with tool calls

### 3. Test with Telnyx

1. Configure Telnyx Custom LLM (see setup steps above)
2. Call your Telnyx phone number
3. Speak naturally: "Hi, I'd like to book an appointment"
4. The AI assistant should respond using your configured persona

### 4. Monitor logs

Watch your terminal for incoming requests and persona injection:
```bash
uvicorn app.main:app --reload --log-level debug
```

## Customizing Personas

### Use an existing persona

Set in `.env`:
```bash
PERSONA_NAME=medical_clinic  # or salon_spa, default
BUSINESS_NAME=City Medical Center
```

### Create a new persona

1. Create a new file: `app/personas/my_business.txt`
2. Write detailed instructions (see existing personas for examples)
3. Update `.env`:
   ```bash
   PERSONA_NAME=my_business
   ```

### Per-customer personas

For multi-tenant setups, you can:
- Pass `persona_name` as a query parameter or header
- Map Telnyx phone numbers to specific personas
- Store persona mappings in a database

## Architecture

```
Telnyx Phone Call
    ↓
Telnyx AI Assistant (STT/TTS)
    ↓
POST /v1/chat/completions (your server)
    ↓
Persona Manager (loads persona + injects context)
    ↓
OpenAI API (with tools for booking)
    ↓
Response (text + tool calls)
    ↓
Back to Telnyx (converts to speech)
    ↓
Customer hears response
```

## Appointment Tools (Mock Implementation)

The following tools are defined and available to the AI:

- **`find_available_slots`**: Search for open appointment times
- **`book_appointment`**: Create a new appointment
- **`cancel_appointment`**: Cancel an existing appointment
- **`reschedule_appointment`**: Move an appointment to a new time

**⚠️ Currently using mock data.** Replace `execute_tool()` in `app/routers/ai_voice.py` with real database queries and calendar integrations.

## Next Steps

### Immediate (to make it production-ready)

1. **Replace mock tools** with real appointment logic:
   - Connect to your calendar system (Google Calendar, Outlook, etc.)
   - Store appointments in a database
   - Implement real availability checking

2. **Add webhook signature verification**:
   - Uncomment signature validation in `/telnyx/ai` and `/telnyx/call-control`
   - Use `TELNYX_SIGNING_SECRET` to verify requests

3. **Enhance persona injection**:
   - Load business hours, services, staff from database
   - Inject real-time availability status
   - Include current promotions or special instructions

4. **Add logging and monitoring**:
   - Log all conversations for quality assurance
   - Track booking success rates
   - Monitor tool execution failures

### Phase 2 (production features)

- Database models for appointments, customers, businesses
- Calendar integration (Google Calendar, Microsoft Outlook)
- SMS/email notifications and confirmations
- Admin dashboard for managing appointments
- Analytics and reporting

### Phase 3 (enterprise)

- Multi-tenant support (multiple businesses)
- Advanced scheduling rules (buffer times, double-booking prevention)
- Payment processing integration
- CRM integration (Salesforce, HubSpot)
- Call recording and transcription storage

## Troubleshooting

### "OPENAI_API_KEY not configured"
- Make sure you've created `.env` from `.env.example`
- Verify `OPENAI_API_KEY` is set correctly

### Telnyx not reaching your endpoint
- Ensure your server is publicly accessible (use ngrok for local dev)
- Check Telnyx webhook logs in Mission Control Portal
- Verify the Base URL in Telnyx matches your server URL

### Persona not loading
- Check that `PERSONA_NAME` matches a file in `app/personas/`
- File must be named `{persona_name}.txt`
- Falls back to `default.txt` if not found

### AI not using tools
- Verify OpenAI model supports function calling (gpt-4, gpt-4-turbo, gpt-4o, gpt-4o-mini)
- Check that tools are being passed in the request payload
- Review OpenAI API response for tool_calls

## Support

- [Telnyx Custom LLM Documentation](https://developers.telnyx.com/docs/inference/ai-assistants/custom-llm/)
- [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

Built with ❤️ for seamless voice-first appointment booking
