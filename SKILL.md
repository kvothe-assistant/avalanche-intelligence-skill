# Avalanche Intelligence Skill

## ⚠️ IMPORTANT: This is a **Standalone Project**

This is **NOT** a regular OpenClaw skill to be used in-place. The Avalanche Intelligence tool has its own **standalone repository** and should be cloned separately.

---

## 📦 Installation (Choose Your Method)

### Method 1: Standalone Project (Recommended)

Clone and install as an independent project:

```bash
# Clone from GitHub
git clone https://github.com/kvothe-assistant/avalanche-intelligence-skill.git
cd avalanche-intelligence-skill

# Install dependencies
pip install -r requirements.txt

# Initialize configuration
python -m avalanche_intelligence init
```

### Method 2: As OpenClaw Integration (Optional)

Use it through your OpenClaw installation:

```bash
# Navigate to workspace
cd /home/kvothe/.openclaw/workspace/skills

# Clone into skills directory
git clone https://github.com/kvothe-assistant/avalanche-intelligence-skill.git avalanche-intelligence

# Install
cd avalanche-intelligence
pip install -e .

# Use via CLI
avalanche-intelligence scan --hours 24
```

**Note:** When using as an OpenClaw skill, the tool is still a standalone application with its own configuration and data directories.

---

## Overview

The **Avalanche Intelligence** project is a **standalone Python application** that provides real-time monitoring, analysis, and intelligence reporting on the Avalanche blockchain ecosystem.

It can be used with OpenClaw, but it operates as an **independent tool** with its own lifecycle, dependencies, and configuration.

This project aggregates data from multiple sources:

- **Social:** Twitter/X, Reddit, Discord
- **News:** RSS feeds from crypto outlets
- **Development:** GitHub repositories and events
- **On-chain:** Avalanche C-Chain blocks and transactions
- **Analysis:** Multi-model sentiment, entity extraction, trend detection

---

## 📊 Project Structure

The Avalanche Intelligence project has a **standalone architecture** with:

### Core Components
- **CLI Interface:** 7 commands (init, test, scan, search, report, status, watch)
- **Intelligence Engine:** Coordinates all collectors and analyzers
- **Configuration System:** YAML-based with environment variable support

### Data Layer (6 Collectors)
- **Twitter** - API v2 with keyword/account monitoring
- **Reddit** - PRAW with multi-subreddit support
- **Discord** - Real-time bot with webhook alerts
- **GitHub** - REST API with event tracking
- **RSS** - Multi-feed aggregator
- **On-chain** - Avalanche C-Chain RPC integration

### Processing Layer (4 Analyzers)
- **Sentiment Analyzer** - Multi-model (VADER, FinBERT, LLM)
- **Entity Extractor** - Named entity recognition + Avalanche ecosystem
- **Trend Detector** - Spike detection, momentum, anomaly detection
- **Deduplicator** - Vector similarity with ChromaDB

### Storage Layer (3 Backends)
- **Vector Database** - ChromaDB for semantic search
- **Time-Series Database** - InfluxDB for metrics
- **Document Store** - SQLite for structured data

### Alert Layer (2 Components)
- **Alert Manager** - Rule-based triggering and routing
- **Discord Notifier** - Webhook-based alerts with rich embeds

---

## 🚀 Quick Start

### Step 1: Clone and Install

```bash
# Clone from GitHub
git clone https://github.com/kvothe-assistant/avalanche-intelligence-skill.git
cd avalanche-intelligence-skill

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure

```bash
# Initialize configuration
python -m avalanche_intelligence init

# Edit config with your API keys
nano config/config.yaml
```

### Step 3: Run

```bash
# Test installation
python -m avalanche_intelligence test

# Scan data (last 24 hours)
python -m avalanche_intelligence scan --hours 24

# Search for topics
python -m avalanche_intelligence search "spruce testnet"

# Generate report
python -m avalanche_intelligence report --timeframe 24h

# Start continuous monitoring
python -m avalanche_intelligence watch --daemon --interval 900
```

---

## ⚙️ Configuration

Edit `config/config.yaml` with your API keys:

```yaml
sources:
  twitter:
    enabled: true
    bearer_token: "${TWITTER_BEARER_TOKEN}"
    track_keywords: ["avalanche", "avax", "subnet"]
    follow_accounts: ["avalancheavax", "kevinsekniqi"]

  reddit:
    enabled: true
    client_id: "${REDDIT_CLIENT_ID}"
    client_secret: "${REDDIT_CLIENT_SECRET}"
    subreddits: ["avalancheavax", "defi", "cryptocurrency"]

  discord:
    enabled: true
    bot_token: "${DISCORD_BOT_TOKEN}"
    webhook_url: "${DISCORD_WEBHOOK_URL}"
    guilds: ["Avalanche"]
    channels: ["announcements", "tech-talk"]

  github:
    enabled: true
    access_token: "${GITHUB_ACCESS_TOKEN}"
    organizations: ["avalanche-foundation", "avalanche-labs"]

  rss:
    enabled: true
    feeds:
      - "https://www.avax.network/blog/rss"
      - "https://cointelegraph.com/tag/avalanche/rss"

  onchain:
    enabled: true
    rpc_url: "${AVALANCHE_RPC_URL}"

alerts:
  enabled_channels: ["discord"]
  triggers:
    - "trend_spike"
    - "price_change>10%"
    - "high_confidence"
  min_confidence: 0.7
```

---

## 🎯 CLI Commands

### Core Commands

```bash
avalanche-intelligence init              # Initialize configuration
avalanche-intelligence test              # Test installation
avalanche-intelligence status            # Show system status
avalanche-intelligence scan --hours 24  # Collect data
avalanche-intelligence search "query"     # Search data
avalanche-intelligence report             # Generate report
avalanche-intelligence watch --daemon    # Continuous monitoring
```

### Command Options

#### `scan`
```bash
--hours N          # Hours to scan (default: 24)
--sources X,Y,Z     # Specific sources (default: all)
--output FILE      # Save scan results
```

#### `search`
```bash
--query "text"     # Search query
--source NAME       # Filter by source (default: all)
--deep             # More results with context
```

#### `report`
```bash
--timeframe 24h    # Time period (24h, 7d, 30d)
--format markdown    # Output format (markdown, json, html)
--output FILE      # Save report
```

#### `watch`
```bash
--daemon           # Run as background daemon
--interval 900      # Check interval in seconds (default: 15m)
```

---

## 📊 Data Sources

### Twitter/X
- **API:** Twitter API v2
- **Data:** Tweets, replies, mentions, engagement metrics
- **Rate Limit:** 300 requests/hour (configurable)
- **Features:** Sentiment analysis, entity extraction, influence scoring

### Reddit
- **API:** PRAW (Python Reddit API)
- **Data:** Posts, comments, upvotes
- **Rate Limit:** 100 requests/hour (configurable)
- **Features:** Subreddit monitoring, flair extraction

### Discord
- **API:** Discord.py
- **Data:** Messages, reactions, mentions
- **Features:** Real-time listening, webhook alerts, channel filtering

### GitHub
- **API:** GitHub REST API v3
- **Data:** Events (Push, PR, Issue, Release, etc.), repositories
- **Features:** Organization monitoring, repository search, activity tracking

### RSS Feeds
- **Format:** RSS/Atom
- **Data:** News articles, blog posts
- **Features:** Multi-feed aggregation, HTML stripping, duplicate detection

### On-Chain
- **RPC:** Avalanche C-Chain
- **Data:** Blocks, transactions, address data
- **Features:** Real-time monitoring, transaction parsing, balance queries

---

## 🧠 Analysis Capabilities

### Sentiment Analysis
- **Models:** VADER, FinBERT, LLM (composite scoring)
- **Output:** Score (-1 to +1), label (positive/negative/neutral), confidence
- **Batch Processing:** Analyze multiple texts efficiently

### Entity Extraction
- **Types:** Projects, organizations, people, technology, tokens
- **Ecosystem:** 100+ Avalanche-specific entities pre-defined
- **Methods:** spaCy NER, regex patterns, keyword matching

### Trend Detection
- **Spike Detection:** Identifies sudden mention increases (3x, 5x, 10x thresholds)
- **Momentum Analysis:** Sustained growth/decline trends over time
- **Anomaly Detection:** Z-score based outlier detection

### Deduplication
- **Methods:** Exact string matching, fuzzy matching, vector similarity
- **Threshold:** Configurable similarity threshold (default: 0.85)
- **Backends:** Cosine similarity for vectors

---

## 💾 Storage Architecture

### Vector Database (ChromaDB)
- **Purpose:** Semantic search and similarity matching
- **Use Cases:** Content deduplication, intelligent search, entity linking
- **Path:** `data/vector_db/`

### Time-Series Database (InfluxDB)
- **Purpose:** Metrics storage and analytics
- **Use Cases:** Trend detection, anomaly detection, time-series queries
- **Path:** Remote server (configured)

### Document Store (SQLite)
- **Purpose:** Structured data persistence
- **Use Cases:** Documents, signals, projects storage, full-text search
- **Path:** `data/documents/intelligence.db`

---

## 🚨 Alert Types

### Trend Spike
Triggered when an entity's mentions spike significantly above baseline.

### High Confidence
Triggered when sentiment analysis shows extreme polarity with high confidence.

### Price Change
Triggered when token prices change by configured percentage.

### ACP Proposal
Triggered when new Avalanche Community Proposal (ACP) is detected.

### New Subnet
Triggered when a new Avalanche subnet is launched.

### Institutional Partnership
Triggered when major institution partnerships are announced.

---

## 🔧 Best Practices

### API Keys Management
- Store API keys in environment variables, not in config files
- Use different tokens for different environments (dev/prod)
- Rotate tokens regularly for security

### Rate Limiting
- Respect platform rate limits
- Use batch operations when possible
- Implement backoff strategies for failed requests

### Storage Management
- Set appropriate retention periods (default: 90 days)
- Regularly clean up old data
- Monitor database sizes and performance

### Alert Thresholds
- Adjust confidence thresholds based on use case
- Set appropriate trigger frequencies
- Test alert rules before production deployment

### Monitoring
- Use continuous monitoring for critical alerts
- Monitor storage sizes and disk usage
- Track collector uptime and error rates

---

## 📈 Usage Examples

### Example 1: Daily Monitoring

```bash
# Scan recent data
avalanche-intelligence scan --hours 24

# Generate report
avalanche-intelligence report --timeframe 24h --format markdown --output reports/daily.md
```

### Example 2: Trend Research

```bash
# Scan last 24 hours
avalanche-intelligence scan --hours 24 --sources twitter,reddit

# Search for specific topics
avalanche-intelligence search "subnet launch" --deep
```

### Example 3: Continuous Monitoring

```bash
# Start watch daemon
avalanche-intelligence watch --daemon --interval 900

# Check system status
avalanche-intelligence status
```

---

## 🐛 Troubleshooting

### Common Issues

**"VADER not installed"**
```bash
pip install vaderSentiment
```

**"ChromaDB error"**
```bash
pip install chromadb
```

**"spaCy model not found"**
```bash
python -m spacy download en_core_web_sm
```

**"Discord bot token invalid"**
- Verify bot token in Discord Developer Portal
- Ensure bot has necessary permissions
- Check bot is not rate limited

**"Rate limit exceeded"**
- Increase interval between scans
- Reduce number of tracked accounts/keywords
- Use API token with higher limits

---

## 📋 Configuration Reference

### Analysis Configuration
```yaml
analysis:
  sentiment_model: "vader"      # Options: vader, finbert, llm
  entity_extraction: true
  trend_detection: true
  deduplication_threshold: 0.85
```

### Storage Configuration
```yaml
storage:
  retention_days: 90
  vector_db_path: "data/vector_db"
  document_store_path: "data/documents"
```

### Alert Configuration
```yaml
alerts:
  enabled_channels: ["discord"]
  triggers: ["trend_spike", "high_confidence", ...]
  min_confidence: 0.7
```

---

## 🤝 Contributing

To extend the project:

1. **Add a new collector:** Inherit from `BaseCollector` and implement `collect()` and `search()`
2. **Add a new analyzer:** Create a new class in `analyzers/` directory
3. **Add a new storage backend:** Implement interface in `storage/` directory
4. **Update tests:** Add test cases for new functionality

See `CONTRIBUTING.md` for detailed guidelines.

---

## 📚 Documentation

- **Full Documentation:** https://github.com/kvothe-assistant/avalanche-intelligence-skill
- **API Docs:** See inline docstrings in each module
- **Configuration Examples:** `config/config.example.yaml`

---

## 📜 License

MIT License - See `LICENSE` file

---

## 🔗 Repository

**URL:** https://github.com/kvothe-assistant/avalanche-intelligence-skill
**Version:** 1.0.0
**Status:** Production-Ready ✅

---

## 📝 Quick Reference

```bash
# Installation
git clone https://github.com/kvothe-assistant/avalanche-intelligence-skill
cd avalanche-intelligence-skill
pip install -r requirements.txt
python -m avalanche_intelligence init

# Configuration
config/config.yaml                     # Main config
config/config.example.yaml             # Template

# Data locations
data/raw/                            # Raw collected data
data/processed/                       # Processed data
data/vector_db/                        # ChromaDB database
data/documents/                        # SQLite database

# CLI Commands
avalanche-intelligence init              # Initialize
avalanche-intelligence test              # Test install
avalanche-intelligence status            # System status
avalanche-intelligence scan --hours 24  # Collect data
avalanche-intelligence search "query"     # Search
avalanche-intelligence report             # Generate report
avalanche-intelligence watch --daemon    # Monitor
```

---

**Created:** 2026-02-21
**Updated:** 2026-02-21 10:45 GMT+1
**Version:** 1.0.0
**Status:** Production-Ready ✅
