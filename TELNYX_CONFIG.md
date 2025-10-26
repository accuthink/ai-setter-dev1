# Telnyx Configuration Guide

## Problem: Call Rings Once and Hangs Up
**Solution**: Your application now automatically answers calls and starts the AI Assistant!

## Webhook Configuration

### Step 1: Configure Your Telnyx Phone Number

In Telnyx Portal → Numbers → Your Phone Number:

1. **Connection Type**: Select "Call Control"
2. **Webhook URL**: `https://[your-devtunnel-url]/telnyx/call-control`
   - Example: `https://abc123-8000.usw2.devtunnels.ms/telnyx/call-control`
3. **Failover URL** (optional): Same URL for redundancy
4. **Webhook API Version**: V2
5. Click **Save**

### Step 2: Configure AI Assistant (Custom LLM)

In Telnyx Portal → AI Assistants → Your Assistant:

1. **Enable "Use Custom LLM"**: ✅ Check this box
2. **Base URL**: `https://[your-devtunnel-url]`
   - Example: `https://abc123-8000.usw2.devtunnels.ms`
   - ⚠️ DO NOT include `/v1` - Telnyx adds this automatically
3. **Model**: `gpt-4o-mini` (or your configured model)
4. **Integration Secret**: Your OpenAI API key
5. **Voice Settings**:
   - Voice: `female` (or `male` - you can change in code)
   - Language: `en-US`
6. **Click "Validate Connection"** - Should show ✅ Success
7. **Save Configuration**

### Step 3: Link AI Assistant to Phone Number

In Telnyx Portal → Your Phone Number:

1. Go to **AI Assistant** tab
2. Select your configured AI Assistant
3. **Enable AI Assistant** for incoming calls
4. Click **Save**

## How It Works

### Call Flow:
```
1. Customer calls your Telnyx number
   ↓
2. Telnyx sends "call.initiated" webhook to /telnyx/call-control
   ↓
3. Your app answers the call via Telnyx API
   ↓
4. Your app starts AI Assistant via Telnyx API
   ↓
5. AI Assistant connects to your Custom LLM endpoint (/chat/completions)
   ↓
6. Your app injects medical_clinic persona + business context
   ↓
7. OpenAI generates responses using the persona
   ↓
8. Telnyx handles speech-to-text and text-to-speech
   ↓
9. Customer has conversation with AI using your persona
```

## Webhook Events Your App Handles

| Event | Description | Your App's Response |
|-------|-------------|---------------------|
| `call.initiated` | Call arrives | Answer call + Start AI Assistant |
| `call.answered` | Call connected | Log confirmation |
| `call.hangup` | Call ended | Log completion |
| `call.ai.started` | AI Assistant activated | Log status |
| `call.ai.ended` | AI Assistant stopped | Log status |

## Testing Your Configuration

### 1. Check Status Endpoint
```bash
curl https://[your-devtunnel-url]/telnyx/status
```

Should return:
```json
{
  "status": "ready",
  "service": "AI Appointment Setter",
  "endpoints": {
    "call_control": "/telnyx/call-control",
    "ai_webhook": "/telnyx/ai"
  },
  "configuration": {
    "persona": "medical_clinic",
    "business": "Lone Star neurology clinic",
    "model": "gpt-4o-mini"
  }
}
```

### 2. Check Models Endpoint
```bash
curl https://[your-devtunnel-url]/models
```

Should return list of available models.

### 3. Make a Test Call
1. Call your Telnyx number
2. Call should be answered immediately
3. AI should greet you using the medical_clinic persona
4. Watch logs in your terminal for real-time activity

## Monitoring Calls

Watch your application logs for:
```
INFO - Received Telnyx Call Control event: call.initiated
INFO - Answering incoming call: [call_control_id]
INFO - Successfully answered call: [call_control_id]
INFO - Successfully started AI Assistant for call: [call_control_id]
INFO - Received chat completion request for model: gpt-4o-mini
INFO - Loaded persona: medical_clinic for Lone Star neurology clinic
INFO - Calling OpenAI API with model: gpt-4o-mini
INFO - OpenAI request successful
```

## Customizing Voice Settings

To change the AI voice, edit in `app/routers/ai_voice.py`:

```python
json={
    "language": "en-US",
    "voice": "male",  # Options: "male", "female"
}
```

Available languages: en-US, en-GB, es-ES, fr-FR, de-DE, it-IT, pt-BR, and more.

## Troubleshooting

### Call still rings and hangs up?
- ✅ Verify webhook URL is set in Telnyx phone number settings
- ✅ Check that DevTunnel is running and accessible
- ✅ Verify TELNYX_API_KEY in .env.local is correct
- ✅ Check application logs for errors

### AI doesn't start?
- ✅ Verify AI Assistant is enabled for your phone number
- ✅ Check Custom LLM configuration (Base URL, Model, Secret)
- ✅ Click "Validate Connection" in Telnyx portal

### Wrong persona or behavior?
- ✅ Check PERSONA_NAME in .env.local matches a file in app/personas/
- ✅ Verify BUSINESS_NAME is correct
- ✅ Review persona file content in app/personas/medical_clinic.txt

## Support

Check logs first:
```bash
# Your application logs show detailed request/response info
# Look for ERROR or WARNING messages
```

Telnyx Portal:
- View call logs in Portal → Calls
- Check webhook delivery status
- Review AI Assistant conversation transcripts
