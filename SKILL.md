# Avalanche Intelligence Skill

## ⚠️ IMPORTANT: This is Kvothe's Intelligence Tool

This is **NOT** a tool for Gokcan to use directly. This is **Kvothe's** intelligence gathering system that I use to prepare briefings and reports for Gokcan about the Avalanche blockchain ecosystem.

---

## 🎯 Purpose

The Avalanche Intelligence skill provides **Kvothe** with comprehensive data collection and analysis capabilities for the Avalanche blockchain ecosystem. Kvothe uses this tool to:

- Monitor Avalanche developments across multiple sources
- Analyze trends, sentiment, and key events
- Prepare detailed briefings for Gokcan
- Track ecosystem health and momentum
- Identify important signals and anomalies

---

## 🔄 Workflow

```
Gokcan          Kvothe (AI)              Avalanche Intelligence
     │                    │                              │
     │ "Briefing on      │                              │
     │  Avalanche"       │                              │
     ├────────────────────►                              │
     │                    │                              │
     │                    │  scan --hours 24             │
     │                    ├──────────────────────────────►
     │                    │                              │
     │                    │  Collect from Twitter, Reddit│
     │                    │  GitHub, on-chain, etc.     │
     │                    │                              │
     │                    │  Analyze sentiment, trends  │
     │                    │  Extract entities, detect   │
     │                    │  spikes and anomalies       │
     │                    │                              │
     │                    │◄──────────────────────────────┤
     │                    │  Raw data + analysis         │
     │                    │                              │
     │                    │  Synthesize into briefing    │
     │                    │                              │
     │◄────────────────────┤                              │
     │ "Here's your        │                              │
     │  briefing: ..."     │                              │
```

---

## 📋 What Kvothe Can Do With This Skill

### 1. Daily Briefings
**Gokcan asks:** "Give me a briefing on Avalanche"

**Kvothe does:**
```bash
avalanche-intelligence scan --hours 24
avalanche-intelligence report --timeframe 24h
```

**Kvothe delivers:**
- Key developments in last 24h
- Trending topics with mention counts
- Sentiment analysis (positive/negative/neutral)
- Notable events (new subnets, ACP proposals, partnerships)
- Anomalies or spikes detected

---

### 2. Topic Deep-Dive
**Gokcan asks:** "What's happening with Spruce testnet?"

**Kvothe does:**
```bash
avalanche-intelligence search "spruce testnet" --deep
```

**Kvothe delivers:**
- All recent mentions across sources
- Sentiment breakdown
- Key influencers discussing it
- Timeline of major announcements
- Related projects/partners

---

### 3. Trend Analysis
**Gokcan asks:** "What trends are emerging in Avalanche?"

**Kvothe does:**
```bash
avalanche-intelligence scan --hours 168  # 1 week
avalanche-intelligence report --timeframe 7d
```

**Kvothe delivers:**
- Topics with momentum (3x+ increase)
- Emerging projects/protocols
- Sentiment shifts over time
- Correlation between events
- Predictions based on patterns

---

### 4. On-Chain Intelligence
**Gokcan asks:** "Any interesting on-chain activity?"

**Kvothe does:**
```bash
avalanche-intelligence scan --sources onchain --hours 24
```

**Kvothe delivers:**
- Large transactions (>100 AVAX)
- New contract deployments
- Address clustering patterns
- Gas usage anomalies
- Notable wallet movements

---

### 5. Event Monitoring
**Gokcan asks:** "Monitor for ACP proposals"

**Kvothe does:**
```bash
avalanche-intelligence search "acp proposal" --source github
avalanche-intelligence watch --daemon --interval 900
```

**Kvothe delivers:**
- Real-time alerts when new proposals appear
- Historical context on similar proposals
- Community sentiment on GitHub
- Related discussions on Twitter/Reddit

---

## 🎯 Briefing Formats

### Standard Briefing
```
📊 **Avalanche Daily Briefing - Feb 21, 2026**

**Key Developments:**
1. Spruce testnet launched (347 mentions, +180% vs yesterday)
2. New ACP-123 proposal submitted
3. FUSD stablecoin integration announced

**Trending Topics:**
- "Evergreen" (289 mentions, sentiment: 0.72)
- "Subnet migration" (156 mentions, sentiment: 0.68)
- "Institutional RWA" (98 mentions, sentiment: 0.81)

**Sentiment Overview:**
- Overall: 0.71 (positive)
- Twitter: 0.73 | Reddit: 0.69 | GitHub: 0.75

**Notable Events:**
- 🔥 3x spike in "institutional" mentions
- ⚠️ Anomaly detected: Unusual on-chain activity (342 large txs)
- 🚀 New project: Project-X launched on subnet

**Recommendations:**
- Monitor Spruce testnet adoption closely
- Track ACP-123 community feedback
- Watch institutional RWA momentum
```

---

### Executive Summary
```
🎯 **Avalanche Executive Summary**

**Health Score:** 8.2/10 (↑ from 7.9 yesterday)

**Top 3 Insights:**
1. Spruce testnet generating significant buzz (3x spike)
2. Institutional interest at all-time high
3. New subnet proposals increasing ecosystem diversity

**Risk Signals:**
- None detected (sentiment stable)

**Opportunity Signals:**
- RWA tokenization gaining momentum
- DeFi protocols expanding to subnets

**Action Items:**
- Track Spruce testnet progress
- Monitor institutional partnership announcements
```

---

### Technical Briefing
```
🔧 **Avalanche Technical Intelligence**

**Protocol Updates:**
- Teleporter v2.3 released
- Gas optimization in latest AvalancheGo
- New subnet template for EVM chains

**On-Chain Metrics:**
- TPS: 4,500 (↑12%)
- Active addresses: 284,000 (↑8%)
- TVL: $8.2B (↑3.2%)

**Developer Activity:**
- 47 commits to avalanche-labs/* repos
- 12 new subnet proposals
- 3 major protocol upgrades announced

**Technical Sentiment:**
- Positive on scalability improvements
- Concerns about centralization
- Excitement about Teleporter
```

---

## 🛠️ Technical Architecture

### Data Collection (6 Sources)
- **Twitter/X:** API v2 with sentiment analysis
- **Reddit:** Multi-subreddit monitoring
- **Discord:** Real-time message collection
- **GitHub:** Repository events and proposals
- **RSS:** News aggregation from crypto outlets
- **On-chain:** Avalanche C-Chain RPC monitoring

### Analysis Pipeline (4 Layers)
1. **Sentiment Analysis:** VADER + FinBERT + LLM composite
2. **Entity Extraction:** spaCy + Avalanche ecosystem entities
3. **Trend Detection:** Spike detection, momentum analysis, anomalies
4. **Deduplication:** Vector similarity for clean data

### Storage (3 Backends)
- **ChromaDB:** Semantic search and similarity
- **InfluxDB:** Time-series metrics
- **SQLite:** Documents, signals, projects

---

## 📊 Example Commands Kvothe Uses

### Morning Routine
```bash
# Daily scan
avalanche-intelligence scan --hours 24

# Generate briefing
avalanche-intelligence report --timeframe 24h --format markdown
```

### Deep Research
```bash
# Search specific topic
avalanche-intelligence search "new subnet" --deep

# Analyze sentiment
avalanche-intelligence scan --sources twitter,reddit --hours 168
```

### Continuous Monitoring
```bash
# Start background monitoring
avalanche-intelligence watch --daemon --interval 900
```

### Ecosystem Health
```bash
# Check all systems
avalanche-intelligence status

# Generate weekly report
avalanche-intelligence report --timeframe 7d
```

---

## ⚙️ Configuration

The skill reads configuration from:
```
config/config.yaml
```

Key settings:
```yaml
sources:
  twitter:
    enabled: true
    track_keywords: ["avalanche", "avax", "subnet", "spruce", "evergreen"]
  reddit:
    subreddits: ["avalancheavax", "defi"]
  github:
    organizations: ["avalanche-foundation", "avalanche-labs"]
  onchain:
    enabled: true
    rpc_url: "https://api.avax.network/ext/bc/C/rpc"

analysis:
  sentiment_model: "vader"
  trend_detection: true
  entity_extraction: true

alerts:
  enabled_channels: ["discord"]
  triggers: ["trend_spike", "high_confidence", "new_subnet"]
```

---

## 📈 Metrics Kvothe Can Track

### Ecosystem Health
- Total mentions per day
- Sentiment trends over time
- Active project count
- Developer activity (commits, PRs)

### Trend Detection
- Topic momentum (3x, 5x, 10x spikes)
- Emerging projects
- Viral content
- Anomaly detection

### On-Chain Metrics
- Transaction volume
- Active addresses
- Gas usage patterns
- Large transactions (>100 AVAX)

### Community Sentiment
- Overall sentiment score
- Platform-specific sentiment
- Influencer mentions
- Response patterns

---

## 🔧 Maintenance

Kvothe maintains this skill:
- Updates dependencies weekly
- Monitors storage usage
- Cleans up old data (retention: 90 days)
- Tests API connections
- Validates sentiment models

---

## 📚 Documentation Structure

```
avalanche-intelligence-skill/
├── SKILL.md                    # This file (Kvothe's usage guide)
├── INTEGRATION_GUIDE.md         # Technical integration details
├── README.md                   # Project documentation
├── CONTRIBUTING.md             # Development guidelines
└── config/config.example.yaml  # Configuration template
```

---

## 🎯 Summary

**What This Skill Does:**
- Provides Kvothe with comprehensive Avalanche intelligence
- Collects data from 6 sources automatically
- Analyzes sentiment, trends, and anomalies
- Stores data for historical analysis
- Generates briefings and reports

**How Gokcan Uses It:**
- Asks Kvothe for briefings ("Give me Avalanche briefing")
- Requests specific research ("What's happening with Spruce?")
- Wants periodic updates ("Weekly ecosystem report")
- Needs specific analysis ("On-chain activity this week")

**What Kvothe Delivers:**
- Clear, actionable briefings
- Trend analysis with insights
- Sentiment breakdowns
- Anomaly alerts
- Technical intelligence

---

**This is Kvothe's intelligence tool for keeping Gokcan informed about the Avalanche ecosystem.** 🏔️

---

**Created:** 2026-02-21
**Updated:** 2026-02-21 11:15 GMT+1
**Version:** 2.0.0 - Corrected for Kvothe's usage
**Status:** Production-Ready ✅
