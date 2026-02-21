# How Avalanche Intelligence Works as Your Skill

## 🎯 Overview

The **Avalanche Intelligence** skill is a **standalone Python tool** that you invoke through OpenClaw. Think of it like a **specialized AI assistant** that monitors the Avalanche ecosystem for you.

---

## 🔄 Integration Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR WORKFLOW                          │
└─────────────────────────────────────────────────────────────────┘

    │
    ▼
┌───────────────────────────────────────────────────────────────┐
│              OPENCLAW SESSION                          │
│                                                           │
│  You type: "avalanche-intelligence scan --hours 24"      │
└───────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────────┐
│          AVALANCHE INTELLIGENCE SKILL                 │
│                                                           │
│  1. Load config (config/config.yaml)                    │
│  2. Initialize collectors, analyzers, storage             │
│  3. Scan data sources (Twitter, Reddit, etc.)            │
│  4. Analyze (sentiment, entities, trends)              │
│  5. Store data (ChromaDB, SQLite, InfluxDB)          │
│  6. Return results to you                                │
└───────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────────┐
│                   YOUR TERMINAL OUTPUT                     │
│                                                           │
│  Scanning from twitter...                                 │
│  ✓ 142 items collected in 5.3s                         │
│  Scanning from reddit...                                   │
│  ✓ 87 items collected in 3.2s                           │
│                                                           │
│  [Search results, reports, alerts]                          │
└───────────────────────────────────────────────────────────────┘
```

---

## 📚 Architecture Deep Dive

### Data Flow

```
You (in OpenClaw)
        │
        ▼
    ┌───────────┐
    │ CLI Command │
    └───────┬───┘
            │
            ▼
    ┌──────────────────────────────┐
    │  Intelligence Engine        │
    │                           │
    │  ┌─────────────────────┐   │
    │  │ Data Collectors  │   │
    │  │ Twitter, Reddit,   │   │
    │  │ Discord, GitHub,   │   │
    │  │ RSS, On-chain    │   │
    │  └────────┬───────────┘   │
    │           │               │
    │           ▼               │
    │  ┌─────────────────────┐   │
    │  │ Processing Layer │   │
    │  │ Sentiment,       │   │
    │  │ Entities,        │   │
    │  │ Trends,          │   │
    │  │ Deduplication   │   │
    │  └────────┬───────────┘   │
    │           │               │
    │           ▼               │
    │  ┌─────────────────────┐   │
    │  │ Storage Layer    │   │
    │  │ Vector DB,       │   │
    │  │ Time Series,     │   │
    │  │ Document Store   │   │
    │  └────────┬───────────┘   │
    └───────────┴───────────────┘
                │
                ▼
       ┌────────────────┐
       │ Alert System │
       │ (Discord)    │
       └───────────────┘
```

---

## 🎯 Typical Usage Scenarios

### Scenario 1: Daily Avalanche Monitoring

**Your Goal:** See what's happening in Avalanche ecosystem today

**What You Type:**
```bash
avalanche-intelligence scan --hours 24 --sources twitter,reddit,g
```

**What Happens:**
```
1. You type command in OpenClaw
2. Skill loads your config
3. Collectors fetch last 24h from Twitter, Reddit, GitHub
4. Analyzers run sentiment, entity extraction
5. Deduplicator removes duplicate content
6. Storage saves all data to data/raw/
7. Skill shows summary:
   "✓ Twitter: 142 items in 5.3s
    ✓ Reddit: 87 items in 3.2s
    ✓ GitHub: 34 items in 2.1s"
```

**You Get:** Clean, deduplicated data from 3 sources with analysis tags

---

### Scenario 2: Track Specific Topic

**Your Goal:** Monitor "Spruce testnet" mentions across all sources

**What You Type:**
```bash
avalanche-intelligence search "spruce testnet" --deep
```

**What Happens:**
```
1. Skill searches across all collected data
2. Vector database finds semantically similar content
3. Ranks results by relevance score
4. Returns top 20 matches with context
```

**You Get:** Comprehensive list of all Spruce testnet discussions with source attribution

---

### Scenario 3: Continuous Monitoring with Alerts

**Your Goal:** Get alerted when important things happen

**What You Type:**
```bash
avalanche-intelligence watch --daemon --interval 900
```

**What Happens:**
```
1. Skill starts background daemon
2. Every 15 minutes:
   - Scans latest data
   - Analyzes for trends/spikes
   - Checks alert triggers
   - Sends Discord webhooks if matches
3. Runs indefinitely until stopped
```

**You Get:** Real-time alerts to your Discord when:
   - Topic mentions spike 3x
   - Sentiment shows extreme polarity
   - New subnet launched
   - ACP proposal detected

---

### Scenario 4: Generate Weekly Report

**Your Goal:** Summarize Avalanche ecosystem for the week

**What You Type:**
```bash
avalanche-intelligence report --timeframe 7d --format markdown --output reports/weekly.md
```

**What Happens:**
```
1. Skill queries storage for last 7 days
2. Collects metrics, top trends, sentiment summary
3. Generates formatted markdown report
4. Saves to reports/weekly.md
5. You review and share with team
```

**You Get:** Professional report with charts, trends, insights ready to share

---

## 🔧 Installation & Setup

### Step 1: Clone Repository

```bash
# Navigate to your workspace
cd /home/kvothe/.openclaw/workspace

# Clone Avalanche Intelligence
git clone https://github.com/kvothe-assistant/avalanche-intelligence-skill.git

# Enter project
cd avalanche-intelligence-skill
```

### Step 2: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install spaCy model (for entity extraction)
python -m spacy download en_core_web_sm
```

### Step 3: Configure

```bash
# Initialize configuration
python -m avalanche_intelligence init

# Edit config file
nano config/config.yaml
```

Add your API keys:
```yaml
sources:
  twitter:
    bearer_token: "YOUR_TWITTER_BEARER_TOKEN"
  reddit:
    client_id: "YOUR_REDDIT_CLIENT_ID"
    client_secret: "YOUR_REDDIT_CLIENT_SECRET"
  discord:
    bot_token: "YOUR_DISCORD_BOT_TOKEN"
    webhook_url: "YOUR_DISCORD_WEBHOOK_URL"
```

### Step 4: Test

```bash
# Verify installation
python -m avalanche_intelligence test

# First scan
python -m avalanche_intelligence scan --hours 1
```

---

## 📊 Data Storage Locations

The skill stores data in its own directory:

```
avalanche-intelligence-skill/
├── config/
│   └── config.yaml                    # Your API keys (gitignored!)
├── data/
│   ├── raw/                            # Collected JSON data
│   ├── processed/                       # Analyzed data
│   ├── vector_db/                       # ChromaDB (semantic search)
│   ├── documents/                        # SQLite database
│   └── reports/                         # Generated reports
└── data/documents/intelligence.db       # SQLite DB file
```

**Important:** The skill has its own data - separate from OpenClaw's memory system!

---

## 🎯 Daily Workflow Example

**Morning (09:00):**
```bash
# Check what happened overnight
avalanche-intelligence scan --hours 24
avalanche-intelligence report --timeframe 24h
```

**Mid-day (12:00):**
```bash
# Search for specific topic
avalanche-intelligence search "evergreen" --source twitter
```

**Afternoon (15:00):**
```bash
# Check system status
avalanche-intelligence status
```

**Evening (18:00):**
```bash
# Prepare for next day
avalanche-intelligence report --timeframe 24h --output reports/daily.md
```

---

## 🔗 Integration with OpenClaw

The skill works **independently** but you use it through OpenClaw:

```
┌─────────────────────────────────────────────────────┐
│                  OPENCLAW                     │
│                                                  │
│  Your main AI assistant (Kvothe)              │
│  - Has access to your memory                  │
│  - Manages your workspace                   │
│  - Coordinates all tools                    │
└──────────────────────┬──────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────┐
│     AVALANCHE INTELLIGENCE SKILL       │
│                                             │
│  - Installed in workspace/              │
│  - Invoked via CLI commands             │
│  - Has its own config and data          │
│  - Runs as independent process          │
└──────────────────────┬─────────────────────┘
                     │
                     ▼
          ┌──────────────────────────┐
          │ EXTERNAL SERVICES     │
          │                      │
          │  Twitter API          │
          │  Reddit API           │
          │  GitHub API            │
          │  Discord API           │
          │  Avalanche RPC         │
          └───────────────────────┘
```

---

## 💡 Pro Tips

### Tip 1: Use Environment Variables
```bash
# Set in your shell environment
export TWITTER_BEARER_TOKEN="your_token_here"
export REDDIT_CLIENT_ID="your_client_id"

# Config will automatically expand ${TWITTER_BEARER_TOKEN}
```

### Tip 2: Start Small
```bash
# Start with 1 source, 1 hour
avalanche-intelligence scan --sources twitter --hours 1

# Verify it works before enabling all sources
```

### Tip 3: Check Storage Regularly
```bash
# See how much data you've collected
ls -lh data/raw/
du -sh data/vector_db/

# Clean up old data
rm data/raw/scan_2026*
```

### Tip 4: Customize for Your Needs
Edit `config/config.yaml` to track:
- Specific keywords (your projects)
- Specific accounts (your team members)
- Specific subreddits (relevant communities)

---

## 🚀 Quick Start Commands

Copy-paste these to get started:

```bash
# 1. Clone
git clone https://github.com/kvothe-assistant/avalanche-intelligence-skill.git
cd avalanche-intelligence-skill

# 2. Install
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Initialize
python -m avalanche_intelligence init

# 4. Edit config (add your API keys)
nano config/config.yaml

# 5. Test
python -m avalanche_intelligence test

# 6. First scan
python -m avalanche_intelligence scan --hours 1

# 7. Start monitoring (background)
python -m avalanche_intelligence watch --daemon --interval 900
```

---

## 📈 Example Outputs

### Scan Output
```
Collecting from twitter...
  ✓ 142 items collected in 5.3s
Collecting from reddit...
  ✓ 87 items collected in 3.2s
Collecting from github...
  ✓ 34 items collected in 2.1s

╔══════════════════════════════════════╗
║  Source    │ Posts │ Signals │ Duration ║
╠══════════════════════════════════════╣
║  twitter    │   142 │        0 │      5.3s ║
║  reddit     │    87 │        0 │      3.2s ║
║  github     │    34 │        0 │      2.1s ║
╚══════════════════════════════════════╝
```

### Search Output
```
Searching: "spruce testnet"...
Found 15 results:

┌────────────┬────────┬─────────────────────────────┬──────────────┐
│ Relevance   │ Source │ Content Preview          │ Date         │
├────────────┼────────┼─────────────────────────────┼──────────────┤
│ 0.95       │ twitter │ Just tested Spruce... │ 2026-02-21  │
│ 0.87       │ reddit  │ Spruce testnet update... │ 2026-02-20  │
│ 0.82       │ github  │ Added subnet support...    │ 2026-02-19  │
└────────────┴────────┴─────────────────────────────┴──────────────┘
```

### Status Output
```
📊 Avalanche Intelligence Status

📊 System:
  Active Sources: 5
  Total Posts: 12,847
  Signals Found: 23

💾 Storage:
  Raw Data: 145.2 MB
  Processed: 234.1 MB
  Vector DB: initialized

🔍 Collectors:
  ✓ twitter: Active
  ✓ reddit: Active
  ✓ discord: Active
  ✓ github: Active
  ✗ onchain: Inactive
```

---

## 🎯 Summary

**What You Get:**

1. **Autonomous Ecosystem Monitor** - Runs continuously, collects data
2. **Intelligent Analysis** - Multi-model sentiment, entity extraction, trends
3. **Search Capability** - Find anything across all collected data
4. **Reporting System** - Generate professional reports on demand
5. **Alert System** - Get notified of important events via Discord
6. **Production Storage** - ChromaDB, InfluxDB, SQLite

**How You Use It:**

- Type commands in OpenClaw
- Skill executes independently
- Results return to your terminal
- Data stored in skill's own directories
- You review, analyze, share as needed

**It's like having a dedicated AI research assistant** for Avalanche! 🚀

---

**Created:** 2026-02-21
**For:** Avalanche Intelligence Skill v1.0.0
