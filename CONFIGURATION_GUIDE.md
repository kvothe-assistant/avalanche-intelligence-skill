# Avalanche Intelligence - Data Source Configuration Guide

This guide will help you set up all the data sources for comprehensive Avalanche ecosystem monitoring.

---

## 📋 Required Credentials

### 1. **Twitter/X API** ✅
**What you need:**
- Bearer Token (from Twitter Developer Portal)

**How to get it:**
1. Go to: https://developer.twitter.com/en/portal/dashboard
2. Sign up for a Twitter Developer account (free tier available)
3. Create a new project/app
4. Navigate to "Keys and Tokens"
5. Copy the **Bearer Token**

**Free Tier Limits:**
- 300 requests/hour
- 500,000 tweets/month

---

### 2. **Reddit API** ✅
**What you need:**
- Client ID
- Client Secret

**How to get it:**
1. Go to: https://www.reddit.com/prefs/apps
2. Click "create another app..."
3. Choose "script" as the app type
4. Fill in:
   - Name: "avalanche-intelligence"
   - Description: "Avalanche ecosystem monitoring"
   - About URL: (leave blank)
   - Redirect URI: http://localhost:8080
5. Click "create app"
6. Copy:
   - The string under "personal use script" = **Client ID**
   - The string next to "secret" = **Client Secret**

**Free Tier Limits:**
- 100 requests/minute
- No major restrictions for reading public data

---

### 3. **Discord Bot** ✅
**What you need:**
- Bot Token
- Webhook URL (for alerts)

**How to get Bot Token:**
1. Go to: https://discord.com/developers/applications
2. Click "New Application"
3. Give it a name: "Avalanche Intelligence"
4. Navigate to "Bot" in the left sidebar
5. Click "Add Bot"
6. Under "Build-A-Bot", click "Reset Token"
7. Copy the **Token** (this is your bot token)

**How to get Webhook URL:**
1. In your Discord server, go to the channel where you want alerts
2. Click the gear icon (Edit Channel) → Integrations → Webhooks
3. Click "New Webhook"
4. Give it a name: "Avalanche Alerts"
5. Copy the **Webhook URL**

**Bot Permissions Needed:**
- Read Messages
- Read Message History
- Send Messages

---

### 4. **GitHub API** ✅
**What you need:**
- Personal Access Token

**How to get it:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a note: "Avalanche Intelligence"
4. Select scopes:
   - `repo` (for reading repos)
   - `public_repo` (sufficient for public repos)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

**Free Tier Limits:**
- 5,000 requests/hour
- More than enough for monitoring

---

### 5. **Avalanche RPC** ✅ (Already Configured)
**What you need:**
- RPC URL (already using public endpoint)

**Current Configuration:**
- Mainnet: `https://api.avax.network/ext/bc/C/rpc`
- Testnet: `https://api.avax-test.network/ext/bc/C/rpc`

**Free Tier Limits:**
- No rate limits on public endpoints
- Unlimited for basic queries

---

## 🔧 Configuration Template

Replace the placeholders in `config/config.yaml`:

```yaml
sources:
  twitter:
    enabled: true
    bearer_token: "YOUR_TWITTER_BEARER_TOKEN"
    track_keywords:
      - "avalanche"
      - "avax"
      - "subnet"
      - "spruce"
      - "evergreen"
      - "rwa"
      - "defi"
    follow_accounts:
      - "avalancheavax"
      - "kevinsekniqi"
      - "emin"
    rate_limit_per_hour: 300

  reddit:
    enabled: true
    client_id: "YOUR_REDDIT_CLIENT_ID"
    client_secret: "YOUR_REDDIT_CLIENT_SECRET"
    user_agent: "avalanche-intelligence/0.1.0"
    subreddits:
      - "avalancheavax"
      - "defi"
      - "cryptocurrency"
      - "Web3Gaming"
    rate_limit_per_hour: 100

  discord:
    enabled: true
    bot_token: "YOUR_DISCORD_BOT_TOKEN"
    webhook_url: "YOUR_DISCORD_WEBHOOK_URL"
    guilds:
      - "Avalanche"
    channels:
      - "announcements"
      - "tech-talk"

  github:
    enabled: true
    access_token: "YOUR_GITHUB_TOKEN"
    organizations:
      - "avalanche-foundation"
      - "avalanche-labs"
      - "ava-labs"
    repositories:
      - "ava-labs/avalanchejs"
      - "ava-labs/coreth"
    rate_limit_per_hour: 50

  rss:
    enabled: true
    feeds:
      - "https://www.avax.network/blog/rss"
      - "https://cointelegraph.com/tag/avalanche/rss"
      - "https://coindesk.com/arc/outboundfeeds/rss/tag/avalanche"

  onchain:
    enabled: true
    rpc_url: "https://api.avax.network/ext/bc/C/rpc"
    rate_limit_per_second: 10

analysis:
  sentiment_model: "vader"
  entity_extraction: true
  trend_detection: true
  deduplication_threshold: 0.85

alerts:
  enabled_channels:
    - "discord"
  triggers:
    - "trend_spike"
    - "price_change>10%"
    - "new_subnet"
    - "institutional_partnership"
    - "high_confidence"
  min_confidence: 0.7
```

---

## 🔒 Security Best Practices

### Option 1: Environment Variables (Recommended)

Instead of putting credentials directly in config.yaml, use environment variables:

```yaml
sources:
  twitter:
    bearer_token: "${TWITTER_BEARER_TOKEN}"
  
  reddit:
    client_id: "${REDDIT_CLIENT_ID}"
    client_secret: "${REDDIT_CLIENT_SECRET}"
  
  discord:
    bot_token: "${DISCORD_BOT_TOKEN}"
    webhook_url: "${DISCORD_WEBHOOK_URL}"
  
  github:
    access_token: "${GITHUB_TOKEN}"
```

Then set them in your shell:
```bash
export TWITTER_BEARER_TOKEN="your_actual_token_here"
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
# ... etc
```

### Option 2: .env File

Create `.env` file (add to .gitignore!):
```bash
TWITTER_BEARER_TOKEN=your_actual_token
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_WEBHOOK_URL=your_webhook_url
GITHUB_TOKEN=your_github_token
```

---

## ✅ Testing Each Source

After configuring, test each source:

### Test Twitter
```bash
python3 -c "from avalanche_intelligence import IntelligenceEngine; engine = IntelligenceEngine(); print(engine.collectors.get('twitter'))"
```

### Test Reddit
```bash
python3 -c "import praw; reddit = praw.Reddit(client_id='YOUR_ID', client_secret='YOUR_SECRET', user_agent='test'); print('Reddit OK')"
```

### Test Discord
```bash
python3 -c "import discord; print('Discord library OK')"
```

### Test GitHub
```bash
curl -H "Authorization: token YOUR_GITHUB_TOKEN" https://api.github.com/user
```

---

## 🚀 Quick Setup Checklist

- [ ] Twitter Developer account created
- [ ] Twitter Bearer Token copied
- [ ] Reddit App created
- [ ] Reddit Client ID & Secret copied
- [ ] Discord Bot created
- [ ] Discord Bot Token copied
- [ ] Discord Webhook URL created
- [ ] GitHub Personal Access Token created
- [ ] All credentials added to config.yaml or .env
- [ ] Each source tested individually
- [ ] Full scan test completed

---

## 📊 Expected Results After Setup

With all sources configured, you should see:

```
Collecting from twitter...
  ✓ 247 items collected in 8.2s

Collecting from reddit...
  ✓ 156 items collected in 5.1s

Collecting from discord...
  ✓ 89 items collected in 3.7s

Collecting from github...
  ✓ 67 items collected in 4.3s

Collecting from rss...
  ✓ 34 items collected in 2.8s

Collecting from onchain...
  ✓ 512 items collected in 12.4s

Total: 1,105 items collected
```

---

## 🎯 Which Sources Should You Prioritize?

**For Comprehensive Monitoring:**
1. **Twitter** (most real-time updates)
2. **Reddit** (community sentiment)
3. **GitHub** (development activity)
4. **On-chain** (network health)
5. **Discord** (if you have access to relevant servers)
6. **RSS** (news aggregation)

**For Quick Setup:**
1. **On-chain** (already working)
2. **RSS** (already working)
3. **GitHub** (easiest to set up)
4. **Reddit** (quick setup)
5. **Twitter** (requires developer account)
6. **Discord** (requires bot permissions)

---

**Ready to configure? Let me know which sources you want to set up first!** 🚀
