# TTS (Text-to-Speech) Troubleshooting Guide

## Important: Understanding Your Architecture

You are using **Telnyx AI Assistant with Custom LLM mode**. This means:

✅ **What Happens Automatically:**
- Telnyx answers the call
- Telnyx handles Speech-to-Text (STT) - converts caller's voice to text
- Telnyx calls your `/chat/completions` endpoint with the text
- Your app returns text response in OpenAI format
- Telnyx handles Text-to-Speech (TTS) - converts your text to voice
- Caller hears the AI voice

❌ **What You Should NOT Do:**
- Do NOT manually call Telnyx `/speak` endpoint (that's for manual Call Control mode)
- Do NOT try to handle audio/voice in your application
- Do NOT manually answer calls (AI Assistant does this)

## Current Issue: TTS Not Playing

Based on logs, your application is working correctly:
- ✅ Call is answered
- ✅ AI Assistant starts
- ✅ Your `/chat/completions` endpoint receives requests
- ✅ OpenAI generates responses
- ✅ You return valid text responses
- ❌ **Telnyx is not converting your text to speech**

## Root Causes (In Order of Likelihood)

### 1. Voice Tab Not Configured (MOST COMMON)

**Problem**: Telnyx AI Assistant has no TTS provider/voice configured.

**Solution**: Configure Voice Tab in Telnyx Portal:

1. Go to **Telnyx Portal → AI → Assistants → Your Assistant**
2. Click **Voice Tab**
3. Configure:
   ```
   Provider: Telnyx
   Model: NaturalHD (or Standard)
   Voice: astra (or any voice from the list)
   Language: en-US
   
   Speaking Plan (CRITICAL - set all to 0 seconds):
   - Wait Seconds: 0
   - On Punctuation Seconds: 0
   - On No Punctuation Seconds: 0  
   - On Number Seconds: 0
   ```
4. Click **Save**
5. Test call immediately

**Why This Happens**: By default, AI Assistant might not have TTS enabled or configured.

---

### 2. Response Format Issue

**Problem**: Your response might not have the content in the correct field.

**Current Response Format** (what you're sending):
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "gpt-4o-mini",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Your text response here"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {...}
}
```

**What to Check**:
- The `choices[0].message.content` field MUST contain text
- Content MUST NOT be null or empty string
- Content should be plain text, not HTML or special formatting

**New Logging**: The updated code now validates and logs:
```
🤖 OpenAI Response Content (123 chars): Your text response...
📤 Sending to Telnyx (123 chars): Your text response...
```

If you see `(0 chars)` - that's the problem!

---

### 3. Greeting Configuration Conflict

**Problem**: If you set a greeting in Telnyx Portal AND your app tries to send greeting, it might cause issues.

**Check**:
1. Go to **Telnyx Portal → AI → Assistants → Your Assistant → Behavior Tab**
2. Look at **Greeting** field
3. **Recommended**: Leave it EMPTY (your Custom LLM provides greeting via persona)

**Why**: If Telnyx greeting is set, it might play but then not process your app's responses.

---

### 4. Voice App Not Linked to Phone Number

**Problem**: AI Assistant is configured but not assigned to your phone number.

**Solution**:
1. Go to **Telnyx Portal → Numbers → Your Phone Number**
2. Click **AI Assistant tab**
3. Verify:
   - AI Assistant is **Selected** (dropdown should show your assistant)
   - **Enable for incoming calls**: ✅ Checked
   - **Auto-start on answer**: ✅ Checked
4. Click **Save**

---

### 5. Billing/Account Issue

**Problem**: TTS requires credits and your account might have insufficient balance.

**Check**:
1. Go to **Telnyx Portal → Billing**
2. Verify you have available balance
3. Check if TTS is enabled for your account type
4. Some trial accounts have limited TTS capabilities

---

## Step-by-Step Debugging

### Step 1: Check Your Logs

Make a test call and watch for these log entries:

```bash
# Good - Everything working:
INFO - 📞 Telnyx Event: call.initiated
INFO - ✅ Call answered
INFO - 🤖 AI Assistant activated
INFO - 🎙️ Received chat completion request
INFO - 🤖 OpenAI Response Content (156 chars): Hello! Thank you for calling...
INFO - 📤 Sending to Telnyx (156 chars): Hello! Thank you for calling...

# Bad - Empty content:
INFO - 🤖 OpenAI Response Content (0 chars): 
INFO - 📤 Sending to Telnyx (0 chars):
❌ This means OpenAI returned empty response - check your persona/prompts

# Bad - No /chat/completions call:
INFO - 📞 Telnyx Event: call.initiated
INFO - ✅ Call answered
INFO - 🤖 AI Assistant activated
(no chat completion request)
❌ This means Telnyx AI Assistant is not calling your Custom LLM endpoint
```

### Step 2: Verify Telnyx Configuration

Run this checklist in Telnyx Portal:

```
□ AI Assistant → Agent Tab:
  □ "Use Custom LLM" is checked
  □ Base URL: https://your-url (no /v1)
  □ Model: gpt-4o-mini
  □ Integration Secret: Your OpenAI API key
  □ "Validate Connection" shows ✅ Success

□ AI Assistant → Voice Tab:
  □ Provider: Telnyx (or other TTS provider)
  □ Model: NaturalHD
  □ Voice: Selected (e.g., astra)
  □ Language: en-US
  □ All Speaking Plan sliders: 0s

□ AI Assistant → Behavior Tab:
  □ Auto-answer: ✅ Enabled
  □ Greeting: Empty (or your custom greeting)
  □ Max Duration: 300+ seconds

□ Phone Number → AI Assistant Tab:
  □ Assistant selected in dropdown
  □ Enable for incoming calls: ✅
  □ Auto-start on answer: ✅
```

### Step 3: Test with Diagnostic Endpoint

To see exactly what Telnyx is sending to your app:

```bash
# Temporarily point Telnyx Base URL to:
https://your-devtunnel-url/telnyx/diagnostic

# Make a test call
# Check your logs for full request details
# Then change back to your normal Base URL
```

### Step 4: Test OpenAI Directly

Verify OpenAI is returning content:

```bash
curl -X POST https://your-url/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "Hello"}
    ]
  }'

# Should return JSON with choices[0].message.content populated
```

### Step 5: Check Telnyx Call Logs

1. Go to **Telnyx Portal → Calls** (or Mission Control)
2. Find your test call
3. Click to view details
4. Look for:
   - AI Assistant events (started, messages, ended)
   - Any error messages
   - TTS events (if TTS was attempted)
   - Webhook delivery status

---

## Quick Fixes to Try

### Fix 1: Explicitly Enable TTS (Voice Tab)
The most common issue - just needs Voice Tab configuration.

### Fix 2: Restart Everything
```bash
# Terminal 1: Stop app (Ctrl+C) and restart
./scripts/start-local.sh

# Terminal 2: Restart DevTunnel
./scripts/setup-devtunnel.sh

# Make test call
```

### Fix 3: Simplify Greeting
If greeting is too long or has special characters, try a simpler one:

Edit `app/personas/medical_clinic.txt` and shorten the greeting section.

### Fix 4: Test with Direct Text
Modify the greeting to be super simple:

```python
greeting = "Hello, this is a test."
```

If this works but your normal greeting doesn't, the issue is content length or format.

### Fix 5: Check for Rate Limits
```bash
# Check OpenAI API status
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_OPENAI_KEY"

# Should return 200, not 429 (rate limit)
```

---

## Expected Behavior (Working System)

When everything works correctly:

```
1. Caller dials your Telnyx number
   ↓
2. Call is answered within 1-2 seconds
   ↓
3. Caller hears: "Hello! Thank you for calling Lone Star neurology clinic..."
   (This is TTS working)
   ↓
4. Caller says: "I need to book an appointment"
   ↓
5. Your app logs show:
   - Received user message
   - OpenAI generates response
   - Response content logged (with actual text)
   ↓
6. Caller hears: "May I have your full name and date of birth, please?"
   (TTS working again)
   ↓
7. Conversation continues...
```

---

## Still Not Working?

If you've tried everything above:

### Option A: Manual Speak Mode (Alternative Architecture)

Switch to manual Call Control mode:

1. **Disable AI Assistant** in Telnyx Portal
2. Change Phone Number connection to **Call Control Application**
3. Implement manual speak calls in your code (GPT-5 suggestion)
4. Your app will need to:
   - Answer calls manually
   - Capture call_control_id
   - Call `/v2/calls/{id}/actions/speak` for each response
   - Handle all voice orchestration

**Note**: This is more complex but gives you full control.

### Option B: Contact Telnyx Support

Provide them with:
- Your phone number
- Test call timestamp
- Your AI Assistant name/ID
- Screenshot of Voice Tab configuration
- Sample from your application logs

They can check server-side if TTS is failing.

---

## Summary Checklist

Before contacting support, verify:

- [ ] Application is running and accessible
- [ ] DevTunnel/ngrok is running and stable
- [ ] `/chat/completions` endpoint returns valid responses with content
- [ ] Logs show "OpenAI Response Content (123 chars): ..." with actual text
- [ ] Telnyx AI Assistant has Voice Tab configured
- [ ] Voice Tab has Provider, Model, Voice selected
- [ ] All Speaking Plan sliders are set to 0s
- [ ] AI Assistant is linked to phone number
- [ ] Phone number has AI Assistant enabled
- [ ] Telnyx account has sufficient balance
- [ ] Call logs in Telnyx Portal show AI Assistant starting
- [ ] No errors in Telnyx Portal call details

---

## Key Difference from GPT-5 Suggestion

**GPT-5's suggestion is for a different architecture:**

```python
# GPT-5 suggested this (Manual Call Control mode):
r = client.post(
    f"https://api.telnyx.com/v2/calls/{CALL_CONTROL_ID}/actions/speak",
    headers={"Authorization": f"Bearer {TELNYX_API_KEY}"},
    json={"payload": tts_text, "voice": "...", "language": "en-US"}
)
```

**You should NOT do this** if using AI Assistant with Custom LLM.

**Your architecture:**
- You only return text in OpenAI format
- Telnyx AI Assistant handles TTS automatically
- No need to call `/speak` endpoint manually

The GPT-5 approach is valid for **manual mode** but NOT for **AI Assistant mode**.

---

## Need Help?

1. Check your logs first (enable DEBUG level if needed)
2. Verify Telnyx Voice Tab configuration
3. Test with a simple greeting text
4. Check Telnyx Portal call logs
5. Contact Telnyx support with specific details

**Most likely fix**: Configure Voice Tab settings in Telnyx Portal!
