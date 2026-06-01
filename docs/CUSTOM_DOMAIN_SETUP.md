# 🌐 Custom Domain Setup (name.com + GitHub Codespaces)

## Option A: CNAME Redirect (Easiest - 5 minutes)

### Step 1: Get Your Codespaces URL
In Codespaces terminal:
```bash
# The URL will be in PORTS tab, looks like:
# https://username-projectname-xxxx.githubpreview.dev:8502
```

### Step 2: Configure name.com DNS

1. Log in to **name.com**
2. Go to **Domains** → Your domain → **DNS Settings**
3. Click **Add Record**
4. Create a CNAME record:
   - **Type:** CNAME
   - **Name:** @ (or subdomain like `app`)
   - **Value:** `username-projectname-xxxx.githubpreview.dev`
   - **TTL:** 3600

### Step 3: Wait for DNS Propagation
- Takes 5-30 minutes
- Test: `nslookup yourdomain.com`

### Result:
- Visit `yourdomain.com` in browser
- **Redirects to** GitHub Codespaces instance
- **Shows:** Your Streamlit app

---

## Option B: Ngrok Tunnel (More Reliable - 10 minutes)

### Step 1: Install Ngrok
```bash
# In Codespaces:
curl https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz | tar xz
```

### Step 2: Create Ngrok Account
- Go to https://ngrok.com
- Sign up (free)
- Copy auth token from dashboard

### Step 3: Start Ngrok Tunnel
```bash
./ngrok config add-authtoken YOUR_AUTH_TOKEN
./ngrok http 8502  # Points to Streamlit
```

Output:
```
Forwarding: https://abc-123-ngrok.io -> localhost:8502
```

### Step 4: Configure name.com
- Create CNAME: `yourdomain.com` → `ngrok.io`
- Or use URL forwarding

### Result:
- Visit `yourdomain.com`
- **Sees:** Your app via Ngrok tunnel
- **More stable** than direct Codespaces CNAME

---

## Option C: Cloudflare Workers (Free Proxy - 15 minutes)

**Best for:** Professional look, more control

1. Sign up at **cloudflare.com** (free)
2. Add your domain
3. Create Worker script that proxies to Codespaces
4. Deploy
5. Access via `yourdomain.com`

---

## Recommended: **Option B (Ngrok)**

Why:
- ✅ No DNS propagation delay
- ✅ Works immediately
- ✅ More reliable
- ✅ Free tier sufficient
- ✅ Easy to switch if needed

---

## Keep Codespaces Running 24/7

Your GitHub Student Pack includes **60 hours/month free**:

```bash
# In Codespaces terminal, run background process:
nohup docker compose up -d &
```

This keeps your app live even if you close the terminal.

**Cost:** 60 hours/month = ~2 hours/day average = well within limit

---

## Final Setup

1. Start Codespaces
2. `export HUGGINGFACE_API_KEY="hf_..."`
3. `docker compose up -d`
4. Setup Ngrok tunnel
5. Point name.com to Ngrok
6. **Live in 15 minutes!** 🎉
