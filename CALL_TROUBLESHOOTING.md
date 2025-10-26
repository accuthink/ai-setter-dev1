# FIXING "CALL RINGS ONCE AND HANGS UP" ISSUE

## Root Cause Analysis

The issue happens when **AI Assistant is enabled in Telnyx Portal** but the configuration is incomplete or conflicting. When AI Assistant is enabled, Telnyx automatically handles answering and starting the AI - you don't need manual call control.

## ✅ CORRECT CONFIGURATION (Choose ONE approach)

### Option 1: Using AI Assistant (RECOMMENDED - Easiest)

This is the simplest approach and what you want for your use case.

#### Step 1: Configure Phone Number Connection

In **Telnyx Portal → Numbers → Your Phone Number**:

1. **Connection Type**: `Texml`
2. **TeXML Application**: Create new or select existing
3. In the TeXML Application settings:
   - **Status Callback**: `https://[your-devtunnel-url]/telnyx/call-control`
   - **Status Callback Method**: `POST`
   - Enable **AI Assistant**
   - Select your AI Assistant from dropdown

#### Step 2: Configure AI Assistant

In **Telnyx Portal → AI → Assistants → Your Assistant**:

1. **General Tab**:
   - Name: `Lone Star Appointment Setter`
   - Enable: `✅ Active`

2. **Agent Tab**:
   - **Enable "Use Custom LLM"**: `✅ Checked`
   - **Base URL**: `https://[your-devtunnel-url]`
     - Example: `https://abc123-8000.usw2.devtunnels.ms`
     - ⚠️ **NO `/v1` at the end!**
   - **Model**: `gpt-4o-mini`
   - **Integration Secret**: Your full OpenAI API key
     - Example: `sk-proj-eezWdH4msN8A4d_eRydD...`
   - **Click "Validate Connection"** → Should show ✅ Success
   - **Click "Save"**

3. **Voice Tab**:
   - **Language**: `English (US)` or `en-US`
   - **Voice**: Choose preferred voice (e.g., `alloy`, `echo`, `nova`)
   - **Speech Model**: `nova` (recommended for best quality)

4. **Behavior Tab**:
   - **Auto-answer**: `✅ Enabled` ← **CRITICAL: Must be enabled!**
   - **Greeting**: Leave empty (your Custom LLM will provide greeting via persona)
   - **Max Duration**: `300` seconds (5 minutes) or adjust as needed
   - **Silence Timeout**: `5` seconds
   - **Save Changes**

#### Step 3: Link AI Assistant to Phone Number

In **Telnyx Portal → Numbers → Your Phone Number**:

1. Go to **AI Assistant** tab
2. **Select Assistant**: Choose your configured assistant
3. **Enable for incoming calls**: `✅ Checked`
4. **Auto-start on answer**: `✅ Checked` ← **CRITICAL!**
5. **Click "Save"**

---

### Option 2: Manual Call Control (ADVANCED - Not Recommended)

Only use this if you want full manual control and are NOT using AI Assistant.

1. **DISABLE AI Assistant** in Telnyx Portal completely
2. Set Connection Type to **Call Control Application**
3. Set Webhook URL to: `https://[your-devtunnel-url]/telnyx/call-control`
4. In your code (`app/routers/ai_voice.py`), **uncomment** the manual answer logic:

```python
# Uncomment this block if NOT using AI Assistant:
logger.info(f"Manually answering call: {call_control_id}")
async with httpx.AsyncClient(timeout=10.0) as client:
    try:
        answer_response = await client.post(
            f"https://api.telnyx.com/v2/calls/{call_control_id}/actions/answer",
            headers={
                "Authorization": f"Bearer {settings.TELNYX_API_KEY}",
                "Content-Type": "application/json",
            },
        )
        answer_response.raise_for_status()
        logger.info(f"✅ Successfully answered call: {call_control_id}")
    except Exception as e:
        logger.error(f"❌ Failed to answer call: {str(e)}")
```

---

## 🔍 DEBUGGING STEPS

### Step 1: Verify Application is Running

```bash
# Terminal 1: Start application
cd /Users/senthilraj/Desktop/softwares/ai-appt-setter-dev1
./scripts/start-local.sh

# Should see:
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Verify DevTunnel is Running

```bash
# Terminal 2: Start DevTunnel
./scripts/setup-devtunnel.sh

# Copy the URL shown, e.g.:
# https://abc123-8000.usw2.devtunnels.ms
```

### Step 3: Test Endpoints

```bash
# Replace with your actual DevTunnel URL
export DEVTUNNEL_URL="https://abc123-8000.usw2.devtunnels.ms"

# Test 1: Health check
curl $DEVTUNNEL_URL/health
# Expected: {"ok":true,"service":"AI Appointment Setter"}

# Test 2: Status check
curl $DEVTUNNEL_URL/telnyx/status
# Expected: JSON with "status": "ready"

# Test 3: Models endpoint
curl $DEVTUNNEL_URL/models
# Expected: JSON with list of models

# Test 4: Chat completions (simulate Telnyx)
curl -X POST $DEVTUNNEL_URL/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "I need to book an appointment"}]
  }'
# Expected: JSON response with assistant message
```

### Step 4: Watch Logs During Call

When you make a test call, watch your Terminal 1 logs. You should see:

```
✅ GOOD (AI Assistant enabled):
INFO - 📞 Telnyx Event: call.initiated | Call ID: v3:xxx
INFO - 📲 New incoming call: +1234567890 → +1987654321
INFO - 📞 Telnyx Event: call.answered | Call ID: v3:xxx
INFO - ✅ Call answered: v3:xxx
INFO - 🤖 AI Assistant activated for call: v3:xxx
INFO - Received chat completion request for model: gpt-4o-mini
INFO - Loaded persona: medical_clinic for Lone Star neurology clinic
INFO - Calling OpenAI API with model: gpt-4o-mini
INFO - OpenAI request successful

❌ BAD (Configuration issue):
INFO - 📞 Telnyx Event: call.initiated | Call ID: v3:xxx
INFO - 📞 Telnyx Event: call.hangup | Call ID: v3:xxx
(No call.answered or AI events = problem!)
```

### Step 5: Check Telnyx Portal Logs

1. Go to **Telnyx Portal → Calls** (or Mission Control → Calls)
2. Find your recent test call
3. Click to view details
4. Check:
   - ✅ Was the call answered?
   - ✅ Did AI Assistant start?
   - ✅ Are there any error messages?
   - ✅ Check webhook delivery status

---

## 🚨 COMMON ISSUES & FIXES

### Issue 1: "Call rings once and hangs up immediately"

**Cause**: AI Assistant not enabled or auto-answer is disabled

**Fix**:
- ✅ Go to AI Assistant → Behavior tab → Enable "Auto-answer"
- ✅ Go to Phone Number → AI Assistant tab → Enable "Auto-start on answer"
- ✅ Verify AI Assistant is assigned to the phone number

### Issue 2: "Connection validation fails in Telnyx Portal"

**Cause**: Base URL incorrect or application not accessible

**Fix**:
- ✅ Use DevTunnel URL WITHOUT `/v1`: `https://abc123-8000.usw2.devtunnels.ms`
- ✅ Verify DevTunnel is running: `curl https://[url]/models`
- ✅ Check application logs for incoming validation requests
- ✅ Ensure OPENAI_API_KEY in .env.local is correct

### Issue 3: "AI starts but doesn't respond correctly"

**Cause**: Persona not loading or OpenAI API key invalid

**Fix**:
- ✅ Check PERSONA_NAME in .env.local matches file: `medical_clinic`
- ✅ Verify file exists: `app/personas/medical_clinic.txt`
- ✅ Test OpenAI API key manually:
  ```bash
  curl https://api.openai.com/v1/models \
    -H "Authorization: Bearer YOUR_KEY"
  ```

### Issue 4: "No logs appear when calling"

**Cause**: Webhook URL not configured or incorrect

**Fix**:
- ✅ Double-check webhook URL in Telnyx Portal matches DevTunnel URL
- ✅ Add `/telnyx/call-control` to the end
- ✅ Test webhook manually:
  ```bash
  curl -X POST https://[devtunnel-url]/telnyx/call-control \
    -H "Content-Type: application/json" \
    -d '{"data":{"event_type":"call.initiated","payload":{"call_control_id":"test"}}}'
  ```

### Issue 5: "DevTunnel keeps disconnecting"

**Cause**: DevTunnel idle timeout or network issues

**Fix**:
- ✅ Use ngrok instead: `./scripts/setup-ngrok.sh`
- ✅ Or use persistent DevTunnel:
  ```bash
  devtunnel host -p 8000 --allow-anonymous --persistent
  ```

---

## 📋 VERIFICATION CHECKLIST

Before making a test call, verify:

- [ ] Application is running (`./scripts/start-local.sh`)
- [ ] DevTunnel is running and you have the URL
- [ ] Health endpoint works: `curl https://[url]/health`
- [ ] Models endpoint works: `curl https://[url]/models`
- [ ] Telnyx Portal shows:
  - [ ] Phone number has Connection configured
  - [ ] AI Assistant is configured with Custom LLM
  - [ ] Base URL is set (without `/v1`)
  - [ ] "Validate Connection" shows success ✅
  - [ ] AI Assistant is enabled for the phone number
  - [ ] Auto-answer is enabled in AI Assistant settings
- [ ] Your .env.local has:
  - [ ] Valid TELNYX_API_KEY
  - [ ] Valid OPENAI_API_KEY
  - [ ] PERSONA_NAME=medical_clinic
  - [ ] BUSINESS_NAME set correctly

---

## 🎯 RECOMMENDED SETUP (Summary)

**Use this exact configuration:**

1. **Phone Number Connection**: TeXML Application
2. **TeXML Webhook**: `https://[devtunnel-url]/telnyx/call-control`
3. **AI Assistant Enabled**: Yes
4. **Custom LLM Base URL**: `https://[devtunnel-url]` (no `/v1`)
5. **Auto-answer in AI Assistant**: Enabled
6. **Auto-start on answer**: Enabled

This setup lets Telnyx handle the call answering automatically, and your application just provides the AI intelligence through the Custom LLM endpoint.

---

## 📞 TEST CALL SCRIPT

After configuration, test with this flow:

1. **Call the Telnyx number**
2. **Expected**: Call is answered within 1-2 seconds
3. **Expected**: AI greets you using the medical_clinic persona
4. **Say**: "I need to book an appointment"
5. **Expected**: AI asks about your name, service needed, preferred date/time
6. **Expected**: AI can use appointment booking tools
7. **Watch logs**: See OpenAI API calls and responses

---

Need more help? Check the logs first - they show exactly what's happening!
