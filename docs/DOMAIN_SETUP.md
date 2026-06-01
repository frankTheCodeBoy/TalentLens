# 🌐 Connect name.com Domain to GitHub Codespaces

**Prerequisites:**
- Domain from name.com (via GitHub Student Pack)
- Live Codespaces URL: `https://username-projectname-code.github.dev:8502`

## Option A: Simple Redirect (EASIEST - 2 minutes)

**Best for:** Quick demo/testing

### At name.com:
1. Log in to name.com
2. Go to **Domains** → Your domain → **DNS**
3. Click **Manage DNS** → **Add Custom DNS**
4. Add redirect to your Codespaces URL

### Result:
- Your domain points to the Codespaces instance
- Browser shows: `yourdomain.com` but loads your Codespaces app

---

## Option B: Reverse Proxy with Ngrok (FREE - 10 minutes)

**Best for:** Custom domain + Codespaces

### In Codespaces:
```bash
# Install ngrok
curl https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz | tar xz

# Create ngrok account (free): https://ngrok.com
# Get your auth token from dashboard

# Start ngrok tunnel
./ngrok config add-authtoken YOUR_AUTH_TOKEN
./ngrok http 8502  # Points to Streamlit port
```

Ngrok gives you a public URL like: `https://abcd-1234-ngrok.io`

### At name.com:
1. Go to DNS settings
2. Create **CNAME** record:
   - Name: `@` (or subdomain like `app`)
   - Value: `ngrok.io` endpoint
   - TTL: 3600

### Result:
- Your domain routes through ngrok tunnel to Codespaces
- Works from anywhere

---

## Option C: Use GitHub Pages Custom Domain (ADVANCED)

If you want a static site, configure in repo settings:
1. **Settings** → **Pages**
2. Custom domain: `yourdomain.com`
3. Update DNS at name.com with GitHub's nameservers

---

## ✅ Quick Test

Once configured:
```bash
# Test DNS resolution
nslookup yourdomain.com

# Should show name.com's nameservers or CNAME target
```

Then visit: `yourdomain.com` in your browser

---

## Recommended for You:
**Option B (Ngrok)** — Simple, free, doesn't require permanent infrastructure
- Live in 10 minutes
- Custom domain works immediately
- No server needed (Codespaces handles it)
- Tunnel runs while Codespaces is active

**Cost:** $0 (both free tier)  
**Time:** 10 minutes
