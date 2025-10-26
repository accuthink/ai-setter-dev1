# Quick Start Guide - AI Appointment Setter

## 🚀 Get Started in 3 Steps

### 1. Clone and Configure

```bash
cd /Users/senthilraj/Desktop/softwares/ai-appt-setter-dev1

# Edit local environment config
nano env/.env.local
```

**Required settings in `env/.env.local`:**
- `OPENAI_API_KEY` - Your OpenAI API key
- `TELNYX_API_KEY` - Your Telnyx API key
- `PERSONA_NAME` - Choose: default, medical_clinic, or salon_spa
- `BUSINESS_NAME` - Your business name

### 2. Start the Server

```bash
chmod +x scripts/*.sh
./scripts/start-local.sh
```

The script will:
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Load environment configuration
- ✅ Start server on http://localhost:8000

### 3. Connect Telnyx

**Option A: Use ngrok (for testing)**

In a new terminal:
```bash
./scripts/setup-ngrok.sh
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

**Option B: Deploy to production**

Deploy to your server and use your domain.

**Configure Telnyx:**

1. Go to [Telnyx Mission Control](https://portal.telnyx.com/)
2. Navigate to: **AI Assistants** → Your Assistant → **Agent** tab
3. Check ☑️ **"Use Custom LLM"**
4. Set **Base URL**: `https://your-domain.com/v1` (or ngrok URL)
5. Set **Model Name**: `gpt-4o-mini`
6. Create **Integration Secret** with your OPENAI_API_KEY
7. Click **Validate Connection**
8. **Save**

---

## 📞 Test Your Integration

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected: `{"ok":true}`

### Test 2: Chat Completions

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "I need to book a haircut for tomorrow"}
    ]
  }'
```

Should return OpenAI response with persona context.

### Test 3: Call Your Telnyx Number

1. Call your Telnyx phone number
2. Speak naturally: "Hi, I'd like to book an appointment"
3. The AI should respond using your configured persona
4. Try booking, rescheduling, or canceling

---

## 🎭 Personas

Choose a persona by setting `PERSONA_NAME` in `env/.env.local`:

### Available Personas

- **`default`** - General-purpose appointment assistant
  - Professional and friendly
  - Works for any business type
  - Good starting point

- **`medical_clinic`** - Healthcare assistant
  - HIPAA-aware language
  - Handles urgent cases appropriately
  - Patient-focused communication

- **`salon_spa`** - Beauty and wellness assistant
  - Warm and enthusiastic
  - Service-focused (cuts, color, treatments)
  - Special occasion awareness

### Create Custom Persona

1. Create `app/personas/my_business.txt`
2. Write detailed instructions (see existing personas)
3. Set `PERSONA_NAME=my_business` in env file
4. Restart server

---

## 📁 Project Structure

```
ai-appt-setter-dev1/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── core/
│   │   └── config.py              # Configuration loader
│   ├── personas/
│   │   ├── default.txt            # General persona
│   │   ├── medical_clinic.txt     # Healthcare persona
│   │   └── salon_spa.txt          # Beauty/wellness persona
│   ├── routers/
│   │   └── ai_voice.py            # Telnyx & OpenAI endpoints
│   └── services/
│       └── persona_service.py     # Persona management
├── env/
│   ├── .env.local                 # Local development config
│   ├── .env.test                  # Test environment config
│   └── .env.production            # Production config
├── scripts/
│   ├── start-local.sh             # Startup script
│   ├── test-local.sh              # Testing script
│   └── setup-ngrok.sh             # ngrok tunnel script
└── README.md                       # Full documentation
```

---

## 🔧 Troubleshooting

### "uvicorn: command not found"

The startup script handles this automatically. If running manually:

```bash
source .venv/bin/activate
python -m uvicorn app.main:app --reload
```

### "OPENAI_API_KEY not configured"

Edit your environment file:

```bash
nano env/.env.local
# Set OPENAI_API_KEY=sk-...
```

Then restart:

```bash
./scripts/start-local.sh
```

### Telnyx not reaching endpoint

- ✅ Ensure server is running (`./scripts/start-local.sh`)
- ✅ Ensure ngrok is running (`./scripts/setup-ngrok.sh`)
- ✅ Use HTTPS URL from ngrok in Telnyx
- ✅ Check Telnyx webhook logs in Mission Control

### Persona not loading

- ✅ Verify `PERSONA_NAME` matches file in `app/personas/`
- ✅ File must be named `{persona_name}.txt`
- ✅ Falls back to `default.txt` if not found

### AI not using booking tools

- ✅ Verify using gpt-4, gpt-4o, or gpt-4o-mini
- ✅ Tools are automatically included in requests
- ✅ Check tool execution in server logs

---

## 📚 Next Steps

### Phase 1: Basic Testing (You are here)
- ✅ Server running locally
- ✅ Telnyx Custom LLM configured
- ✅ Persona loaded and working
- ⏳ Test call with Telnyx
- ⏳ Verify tool calls work

### Phase 2: Real Appointment Logic
- Replace mock tools with real database
- Add calendar integration (Google/Outlook)
- Implement real availability checking
- Add appointment storage

### Phase 3: Production Features
- Add webhook signature verification
- Set up SMS/email notifications
- Create admin dashboard
- Add logging and monitoring
- Deploy to production server

---

## 🆘 Support

- **Telnyx Docs**: https://developers.telnyx.com/docs/inference/ai-assistants/custom-llm/
- **OpenAI Docs**: https://platform.openai.com/docs/api-reference/chat
- **Project README**: Full documentation in `README.md`

---

**Ready to test?**

```bash
./scripts/start-local.sh
```

Then call your Telnyx number! 📞
