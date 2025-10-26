# Exposing Your Local Application with ngrok

This guide walks you through getting a temporary public domain to connect your local application to Telnyx.

## What is ngrok?

ngrok creates a secure tunnel from a public URL to your local server. This allows Telnyx (which needs a public HTTPS endpoint) to reach your application running on localhost.

---

## Step-by-Step Setup

### Step 1: Install ngrok

#### macOS (using Homebrew)
```bash
brew install ngrok
```

#### Alternative: Download directly
1. Go to https://ngrok.com/download
2. Download for macOS
3. Unzip and move to your PATH:
```bash
unzip ~/Downloads/ngrok-v3-stable-darwin.zip
sudo mv ngrok /usr/local/bin/
```

#### Verify installation
```bash
ngrok version
```

You should see something like: `ngrok version 3.x.x`

---

### Step 2: Sign Up for ngrok (Free)

1. Go to https://ngrok.com/signup
2. Create a free account (supports GitHub/Google login)
3. After signing in, you'll see your **authtoken** on the dashboard

---

### Step 3: Configure ngrok with Your Authtoken

Copy your authtoken from the ngrok dashboard, then run:

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

Example:
```bash
ngrok config add-authtoken 2abc123def456ghi789jkl
```

This saves your token to `~/.ngrok2/ngrok.yml`

---

### Step 4: Start Your Application

In your first terminal window:

```bash
cd /Users/senthilraj/Desktop/softwares/ai-appt-setter-dev1
./scripts/start-local.sh
```

Wait for the message:
```
Server starting on http://0.0.0.0:8000
```

**Keep this terminal running!**

---

### Step 5: Start ngrok Tunnel

Open a **new terminal window** and run:

```bash
cd /Users/senthilraj/Desktop/softwares/ai-appt-setter-dev1
./scripts/setup-ngrok.sh
```

Or manually:
```bash
ngrok http 8000
```

You'll see output like this:

```
ngrok                                                                    

Session Status                online                                          
Account                       your-email@example.com (Plan: Free)             
Version                       3.5.0                                           
Region                        United States (us)                              
Latency                       -                                               
Web Interface                 http://127.0.0.1:4040                          
Forwarding                    https://abc123def456.ngrok.io -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90    
                              0       0       0.00    0.00    0.00    0.00
```

**🎯 Important:** Copy the **Forwarding** HTTPS URL:
```
https://abc123def456.ngrok.io
```

**Keep this terminal running!**

---

### Step 6: Test Your Public URL

In a **third terminal** or browser:

```bash
curl https://abc123def456.ngrok.io/health
```

Expected response:
```json
{"ok":true}
```

Or visit in your browser:
```
https://abc123def456.ngrok.io/docs
```

You should see the FastAPI Swagger documentation.

---

### Step 7: Configure Telnyx Custom LLM

Now that you have a public URL, configure Telnyx:

1. **Go to Telnyx Mission Control Portal**
   - Visit: https://portal.telnyx.com/
   - Log in to your account

2. **Navigate to AI Assistants**
   - Left sidebar → **AI** → **AI Assistants**
   - Click on your assistant (or create a new one)

3. **Open the Agent Tab**
   - Click on your assistant name
   - Click the **"Agent"** tab at the top

4. **Enable Custom LLM**
   - Scroll down to find **"Use Custom LLM"**
   - Check the box ☑️ **"Use Custom LLM"**

5. **Configure Endpoint Details**
   
   Fill in these fields:
   
   - **Base URL**: `https://abc123def456.ngrok.io/v1`
     - Replace `abc123def456` with YOUR ngrok subdomain
     - Important: Include `/v1` at the end
   
   - **Model Name**: `gpt-4o-mini`
     - Or `gpt-4` if you want to use the more powerful model
   
   - **Integration Secret** (API Key):
     - Click **"Create new Integration Secret"**
     - Name it: `OpenAI API Key`
     - Paste your OpenAI API key (starts with `sk-proj-...`)
     - Click **Save**

6. **Validate Connection**
   - Click the **"Validate Connection"** button
   - You should see: ✅ **"Connection successful"**
   - If it fails, check:
     - Your local server is running
     - ngrok tunnel is active
     - Base URL format is correct: `https://your-url.ngrok.io/v1`

7. **Save Configuration**
   - Click **"Save"** at the bottom of the page

---

### Step 8: Test with a Phone Call

1. **Find Your Telnyx Phone Number**
   - In Telnyx Portal → **Numbers** → **My Numbers**
   - Note the phone number assigned to your AI Assistant

2. **Make a Test Call**
   - Call your Telnyx number from your phone
   - The call should be answered by your AI assistant
   - Try saying: "Hi, I'd like to book an appointment"

3. **Monitor Logs**
   - Watch your terminal where the app is running
   - You should see incoming requests from Telnyx
   - You'll see the persona being loaded and OpenAI responses

---

## Monitoring Your ngrok Tunnel

### Web Interface

ngrok provides a local web interface to monitor requests:

**Open in browser:**
```
http://localhost:4040
```

This shows:
- All HTTP requests going through the tunnel
- Request/response details
- Timing information
- Useful for debugging

### Terminal Output

In the ngrok terminal, you'll see:
- Number of connections
- Request counts
- Real-time activity

---

## Important Notes

### Free Plan Limitations

ngrok Free plan includes:
- ✅ 1 online ngrok agent
- ✅ 1 HTTP endpoint
- ✅ HTTPS support
- ⚠️ Random URL that changes when you restart
- ⚠️ 40 requests/minute limit (should be enough for testing)

### Persistent URL (Paid Feature)

If you restart ngrok, you'll get a new random URL and need to update Telnyx each time.

To get a **static domain** (doesn't change):
1. Upgrade to ngrok paid plan (~$8-10/month)
2. Configure a static subdomain
3. No need to update Telnyx after restarts

---

## Keeping Everything Running

You need **TWO terminal windows** running simultaneously:

**Terminal 1: Your Application**
```bash
cd /Users/senthilraj/Desktop/softwares/ai-appt-setter-dev1
./scripts/start-local.sh
```

**Terminal 2: ngrok Tunnel**
```bash
cd /Users/senthilraj/Desktop/softwares/ai-appt-setter-dev1
./scripts/setup-ngrok.sh
```

Both must stay running for Telnyx to reach your application.

---

## Troubleshooting

### "ngrok: command not found"

Install ngrok:
```bash
brew install ngrok
# or download from https://ngrok.com/download
```

### "Tunnel not found" or "Failed to connect"

1. Make sure your app is running first (`./scripts/start-local.sh`)
2. Check that port 8000 is correct
3. Verify nothing else is using port 8000:
```bash
lsof -i :8000
```

### Telnyx "Connection Failed"

1. Check your Base URL format: `https://your-url.ngrok.io/v1` (with `/v1`)
2. Verify ngrok is running and showing "online"
3. Test the health endpoint:
```bash
curl https://your-url.ngrok.io/health
```
4. Check that Integration Secret has your correct OpenAI API key

### "Authentication required" from ngrok

Run the authtoken command:
```bash
ngrok config add-authtoken YOUR_TOKEN
```

Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken

### Calls connect but AI doesn't respond

1. Check your app logs for errors
2. Verify `OPENAI_API_KEY` is set correctly in `env/.env.local`
3. Check ngrok web interface (http://localhost:4040) for request details
4. Look for OpenAI API errors in logs

---

## Alternative: Deploy to Production Server

For permanent hosting (instead of ngrok), you can deploy to:

1. **Cloud Platforms**
   - Heroku
   - Railway.app
   - Render.com
   - DigitalOcean App Platform
   - AWS Elastic Beanstalk
   - Google Cloud Run

2. **VPS Providers**
   - DigitalOcean Droplet
   - Linode
   - AWS EC2
   - Google Compute Engine

Then use your real domain in Telnyx:
```
https://api.yourdomain.com/v1
```

---

## Quick Reference Commands

```bash
# Start your app
./scripts/start-local.sh

# Start ngrok (in new terminal)
./scripts/setup-ngrok.sh

# Test health endpoint
curl https://YOUR-NGROK-URL.ngrok.io/health

# Test chat completions
curl -X POST https://YOUR-NGROK-URL.ngrok.io/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Hello"}]}'

# View ngrok web interface
open http://localhost:4040

# Stop ngrok
# Press Ctrl+C in the ngrok terminal
```

---

## Ready to Test!

Once both terminals are running and Telnyx is configured:

1. ✅ Application running on localhost:8000
2. ✅ ngrok tunnel active with HTTPS URL
3. ✅ Telnyx configured with your ngrok URL
4. ✅ Call your Telnyx number
5. ✅ Start talking to your AI assistant!

The AI will use the persona from `app/personas/default.txt` and have access to appointment booking tools.
