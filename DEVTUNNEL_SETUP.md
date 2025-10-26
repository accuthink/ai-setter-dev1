# Exposing Your Local Application with DevTunnel

This guide walks you through getting a temporary public domain using Microsoft DevTunnel to connect your local application to Telnyx.

## What is DevTunnel?

DevTunnel is Microsoft's tunnel service that creates a secure connection from a public URL to your local development server. It's built into Visual Studio Code and is free to use with a Microsoft account.

---

## Step-by-Step Setup

### Step 1: Install DevTunnel CLI

#### macOS Installation

**Option A: Using Homebrew (Recommended)**
```bash
brew install --cask devtunnel
```

**Option B: Download directly from Microsoft**
1. Visit: https://aka.ms/devtunnels/download
2. Download the macOS version
3. Extract and install:
```bash
# Download and extract
curl -sL https://aka.ms/DevTunnelCliInstall | bash

# Or manually place in PATH
sudo mv devtunnel /usr/local/bin/
sudo chmod +x /usr/local/bin/devtunnel
```

#### Verify installation
```bash
devtunnel --version
```

You should see something like: `devtunnel 1.x.x`

---

### Step 2: Login to DevTunnel

DevTunnel requires a Microsoft account (free). You can use:
- Personal Microsoft account (Outlook, Hotmail, Live)
- GitHub account
- Azure Active Directory account

**Login command:**
```bash
devtunnel user login
```

This will:
1. Open your browser
2. Prompt you to sign in with Microsoft/GitHub
3. Ask for authorization
4. Return to terminal when complete

You should see:
```
Successfully logged in.
```

---

### Step 3: Start Your Application

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

### Step 4: Create and Start a DevTunnel

Open a **new terminal window** and run:

#### Option A: Quick temporary tunnel (recommended for testing)

```bash
devtunnel host -p 8000 --allow-anonymous
```

This creates a temporary tunnel that:
- Maps to your local port 8000
- Allows anonymous access (no authentication required for Telnyx)
- Will be deleted when you stop it

#### Option B: Create a persistent tunnel (stays across sessions)

```bash
# Create a persistent tunnel
devtunnel create --allow-anonymous

# Note the Tunnel ID from output (e.g., abc123def)

# Host the tunnel on port 8000
devtunnel port create -p 8000

# Start the tunnel
devtunnel host
```

---

### Step 5: Copy Your Public URL

After running the host command, you'll see output like:

```
Hosting port: 8000
Connect via browser: https://abc123def-8000.usw2.devtunnels.ms
Inspect network activity: https://abc123def-8000-inspect.usw2.devtunnels.ms

Ready to accept connections for tunnel: abc123def
```

**🎯 Important:** Copy the **Connect via browser** URL:
```
https://abc123def-8000.usw2.devtunnels.ms
```

**Keep this terminal running!**

---

### Step 6: Test Your Public URL

In a **third terminal** or browser:

```bash
curl https://abc123def-8000.usw2.devtunnels.ms/health
```

Expected response:
```json
{"ok":true}
```

Or visit in your browser:
```
https://abc123def-8000.usw2.devtunnels.ms/docs
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
   
   - **Base URL**: `https://abc123def-8000.usw2.devtunnels.ms/v1`
     - Replace `abc123def-8000.usw2.devtunnels.ms` with YOUR devtunnel URL
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
     - DevTunnel is active
     - Base URL format is correct: `https://your-url.usw2.devtunnels.ms/v1`

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

## DevTunnel Advanced Features

### Creating a Named Persistent Tunnel

For a tunnel that persists across restarts:

```bash
# Create with a custom name
devtunnel create my-appointment-setter --allow-anonymous

# Add a port
devtunnel port create my-appointment-setter -p 8000

# Host the tunnel
devtunnel host my-appointment-setter
```

### List Your Tunnels

```bash
devtunnel list
```

### Delete a Tunnel

```bash
devtunnel delete <tunnel-id>
```

### View Tunnel Details

```bash
devtunnel show <tunnel-id>
```

---

## DevTunnel vs ngrok Comparison

| Feature | DevTunnel | ngrok |
|---------|-----------|-------|
| **Free Tier** | ✅ Yes | ✅ Yes |
| **Login Required** | Microsoft account | ngrok account |
| **Random URL** | ✅ Changes on restart | ✅ Changes on restart |
| **HTTPS Support** | ✅ Yes | ✅ Yes |
| **Rate Limits** | Generous | 40 req/min free |
| **Persistent Tunnels** | ✅ Free | 💰 Paid feature |
| **Web Inspector** | ✅ Built-in | ✅ Built-in |
| **Authentication** | Azure AD supported | Various options |
| **VS Code Integration** | ✅ Native | Extension available |

---

## Monitoring Your DevTunnel

### Inspect Network Activity

DevTunnel provides an inspection URL:
```
https://abc123def-8000-inspect.usw2.devtunnels.ms
```

Open this in your browser to see:
- All HTTP requests going through the tunnel
- Request/response headers
- Response bodies
- Timing information
- Useful for debugging

### Terminal Output

In the DevTunnel terminal, you'll see:
- Connection status
- Incoming requests
- Real-time activity logs

---

## Keeping Everything Running

You need **TWO terminal windows** running simultaneously:

**Terminal 1: Your Application**
```bash
cd /Users/senthilraj/Desktop/softwares/ai-appt-setter-dev1
./scripts/start-local.sh
```

**Terminal 2: DevTunnel**
```bash
devtunnel host -p 8000 --allow-anonymous
```

Both must stay running for Telnyx to reach your application.

---

## Create a DevTunnel Startup Script

For convenience, create a DevTunnel startup script:

```bash
#!/bin/bash
# scripts/setup-devtunnel.sh

echo "Starting DevTunnel on port 8000..."
echo ""
echo "Once started, use the HTTPS URL in Telnyx:"
echo "  • Custom LLM Base URL: https://your-devtunnel-url.usw2.devtunnels.ms/v1"
echo ""
echo "Press CTRL+C to stop the tunnel"
echo ""

devtunnel host -p 8000 --allow-anonymous
```

Make it executable:
```bash
chmod +x scripts/setup-devtunnel.sh
```

Then use it:
```bash
./scripts/setup-devtunnel.sh
```

---

## Troubleshooting

### "devtunnel: command not found"

Install DevTunnel:
```bash
brew install --cask devtunnel
# or
curl -sL https://aka.ms/DevTunnelCliInstall | bash
```

### "User not logged in"

Login to DevTunnel:
```bash
devtunnel user login
```

This will open your browser for Microsoft/GitHub authentication.

### "Failed to create tunnel"

1. Check you're logged in:
```bash
devtunnel user show
```

2. Try logging out and back in:
```bash
devtunnel user logout
devtunnel user login
```

### Telnyx "Connection Failed"

1. Check your Base URL format: `https://your-url.usw2.devtunnels.ms/v1` (with `/v1`)
2. Verify DevTunnel is running and showing "Ready to accept connections"
3. Test the health endpoint:
```bash
curl https://your-url.usw2.devtunnels.ms/health
```
4. Check that Integration Secret has your correct OpenAI API key
5. Ensure you used `--allow-anonymous` flag when creating the tunnel

### "Access Denied" or "Forbidden"

DevTunnel requires `--allow-anonymous` flag for external services like Telnyx to access it:

```bash
devtunnel host -p 8000 --allow-anonymous
```

### Port Already in Use

If port 8000 is already in use:

1. Find what's using it:
```bash
lsof -i :8000
```

2. Stop that process or use a different port:
```bash
# Run your app on different port
uvicorn app.main:app --port 8001

# Run DevTunnel on that port
devtunnel host -p 8001 --allow-anonymous
```

### Tunnel URL Changed After Restart

Free temporary tunnels get new URLs on restart. Options:

1. **Accept it**: Update Telnyx each time you restart
2. **Use persistent tunnel**: Create a named tunnel that keeps the same ID
3. **Deploy to production**: Use a permanent domain

---

## Alternative: Use VS Code DevTunnel Extension

If you use VS Code:

1. DevTunnel is built into VS Code (Version 1.70+)
2. Open Command Palette (`Cmd+Shift+P`)
3. Type: `Forward a Port`
4. Enter port: `8000`
5. Right-click the forwarded port → **Port Visibility** → **Public**
6. Copy the URL and use in Telnyx

---

## Quick Reference Commands

```bash
# Login
devtunnel user login

# Check login status
devtunnel user show

# Quick temporary tunnel (easiest)
devtunnel host -p 8000 --allow-anonymous

# Create persistent tunnel
devtunnel create my-tunnel --allow-anonymous
devtunnel port create my-tunnel -p 8000
devtunnel host my-tunnel

# List tunnels
devtunnel list

# Show tunnel details
devtunnel show <tunnel-id>

# Delete tunnel
devtunnel delete <tunnel-id>

# Logout
devtunnel user logout

# Test your endpoint
curl https://YOUR-DEVTUNNEL-URL.usw2.devtunnels.ms/health
```

---

## Summary: Quick Start with DevTunnel

```bash
# 1. Install
brew install --cask devtunnel

# 2. Login
devtunnel user login

# 3. Start your app (Terminal 1)
./scripts/start-local.sh

# 4. Start DevTunnel (Terminal 2)
devtunnel host -p 8000 --allow-anonymous

# 5. Copy the HTTPS URL shown

# 6. Configure Telnyx with: https://YOUR-URL.usw2.devtunnels.ms/v1

# 7. Call your Telnyx number and test!
```

---

## Production Deployment

For permanent hosting (instead of DevTunnel), deploy to:
- Azure App Service (integrates well with DevTunnel workflow)
- Railway.app
- Render.com
- DigitalOcean
- AWS/GCP

Then use your real domain:
```
https://api.yourdomain.com/v1
```

---

**Ready to test with DevTunnel!** 🚀

The main advantage: DevTunnel is free, has no rate limits, and integrates seamlessly with Microsoft ecosystem. Perfect for development and testing!
