# Avalanche Intelligence Skill

## Overview

The **Avalanche Intelligence** skill provides real-time monitoring, analysis, and intelligence reporting on the Avalanche blockchain ecosystem through OpenClaw.

This skill aggregates data from multiple sources:
- **Social:** Twitter/X, Reddit, Discord
- **News:** RSS feeds from crypto outlets
- **Development:** GitHub repositories and events
- **On-chain:** Avalanche C-Chain blocks and transactions
- **Analysis:** Multi-model sentiment, entity extraction, trend detection

---

## Quick Start

### Installation

```bash
# Navigate to your workspace
cd /home/kvothe/.openclaw/workspace/skills/avalanche-intelligence

# Install dependencies
pip install -r requirements.txt

# Initialize configuration
python -m avalanche_intelligence init
```

### Configuration

Edit `config/config.yaml` with your API keys:

```yaml
sources:
  twitter:
    enabled: true
    bearer_token: "YOUR_TWITTER_BEARER_TOKEN"
    track_keywords: ["avalanche", "avax", "subnet"]
    follow_accounts: ["avalancheavax", "kevinsekniqi"]

  reddit:
    enabled: true
    client_id: "YOUR_REDDIT_CLIENT_ID"
    client_secret: "YOUR_REDDIT_CLIENT_SECRET"
    subreddits: ["avalancheavax", "defi", "cryptocurrency"]

  discord:
    enabled: true
    bot_token: "YOUR_DISCORD_BOT_TOKEN"
    webhook_url: "YOUR_DISCORD_WEBHOOK_URL"
    guilds: ["Avalanche"]
    channels: ["announcements", "tech-talk"]

  github:
    enabled: true
    access_token: "YOUR_GITHUB_TOKEN"
    organizations: ["avalanche-foundation", "avalanche-labs"]

  rss:
    enabled: true
    feeds:
      - "https://www.avax.network/blog/rss"
      - "https://cointelegraph.com/tag/avalanche/rss"

  onchain:
    enabled: true
    rpc_url: "https://api.avax.network/ext/bc/C/rpc"

alerts:
  enabled_channels: ["discord"]
  triggers:
    - "trend_spike"
    - "price_change>10%"
    - "high_confidence"
  min_confidence: 0.7
```

---

## Usage in OpenClaw

### Basic Commands

#### 1. Test Installation

```bash
avalanche-intelligence test
```

Tests that all dependencies are installed and configuration is valid.

---

#### 2. Scan Recent Data

```bash
# Scan last 24 hours from all sources
avalanche-intelligence scan --hours 24

# Scan specific sources only
avalanche-intelligence scan --hours 24 --sources twitter,reddit

# Scan and save report
avalanche-intelligence scan --hours 24 --output reports/scan.md
```

---

#### 3. Search Data

```bash
# Search across all collected data
avalanche-intelligence search "spruce testnet"

# Search specific source
avalanche-intelligence search "defi" --source reddit

# Deep search with more context
avalanche-intelligence search "avalanche9000" --deep
```

---

#### 4. Generate Reports

```bash
# Daily report (markdown)
avalanche-intelligence report --timeframe 24h --format markdown

# Weekly report (JSON)
avalanche-intelligence report --timeframe 7d --format json

# Monthly report (HTML)
avalanche-intelligence report --timeframe 30d --format html --output reports/monthly.html
```

---

#### 5. System Status

```bash
avalanche-intelligence status
```

Shows:
- Active collectors
- Total posts collected
- Total signals detected
- Storage statistics
- Collector status

---

#### 6. Continuous Monitoring

```bash
# Start watch daemon (runs in background)
avalanche-intelligence watch --daemon --interval 900

# Check every 15 minutes (default)
avalanche-intelligence watch --daemon

# Check every 5 minutes
avalanche-intelligence watch --daemon --interval 300
```

---

### Advanced Workflows

#### Workflow 1: Track Trending Topic

```bash
# 1. Scan recent data
avalanche-intelligence scan --hours 6 --sources twitter,reddit

# 2. Search for topic mentions
avalanche-intelligence search "spruce testnet" --deep

# 3. Generate sentiment report
avalanche-intelligence report --timeframe 6h
```

---

#### Workflow 2: Monitor Ecosystem Events

```bash
# 1. Start continuous monitoring
avalanche-intelligence watch --daemon --interval 900

# 2. Check alerts periodically
avalanche-intelligence status

# 3. Search for specific events
avalanche-intelligence search "acp proposal" --source github
```

---

#### Workflow 3: Analyze Sentiment Trends

```bash
# 1. Collect recent social data
avalanche-intelligence scan --hours 24 --sources twitter,reddit,discord

# 2. Generate report
avalanche-intelligence report --timeframe 24h --format markdown --output reports/sentiment.md

# 3. Review sentiment analysis
# (View report for aggregated sentiment scores)
```

---

## Output Examples

### Scan Output

```
Collecting from twitter...
  ✓ 142 items collected in 5.3s

Collecting from reddit...
  ✓ 87 items collected in 3.2s

Collecting from github...
  ✓ 34 items collected in 2.1s

╔════════════════════════════════════════════════╗
║  Source            │ Posts │ Signals │ Duration   ║
╠════════════════════════════════════════════════╣
║  twitter          │   142 │        0 │      5.3s   ║
║  reddit           │    87 │        0 │      3.2s   ║
║  github           │    34 │        0 │      2.1s   ║
╚══════════════════════════════════════════════════╝

✓ Scan complete!
Data saved to: data/raw/scan_20260221-103015.json
```

---

### Search Output

```
Searching: avalanche subnet launch...
Found 15 results:

┌─────────────┬────────┬─────────────────────────────────────┬─────────────┐
│ Relevance   │ Source │ Content Preview                 │ Date        │
├─────────────┼────────┼─────────────────────────────────────┼─────────────┤
│ 0.95       │ twitter │ New subnet launched on Fuji testnet... │ 2026-02-21 │
│ 0.82       │ reddit   │ Avalanche subnet announcement: ...     │ 2026-02-21 │
│ 0.75       │ github   │ Created new subnet template ...      │ 2026-02-20 │
└─────────────┴────────┴─────────────────────────────────────┴─────────────┘
```

---

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
  ✓ rss: Active
  ✗ onchain: Inactive
```

---

## Data Sources Explained

### Twitter/X
- **API:** Twitter API v2
- **Data:** Tweets, replies, mentions, engagement
- **Rate Limit:** 300 requests/hour (configurable)
- **Features:** Sentiment, entities, influence scoring

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
- **Data:** Events (Push, PR, Issue, Release, etc.)
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

## Analysis Capabilities

### Sentiment Analysis
- **Models:** VADER, FinBERT, LLM (composite)
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

## Alert Types

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

## Storage Architecture

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

## Best Practices

### 1. API Keys Management
- Store API keys in environment variables, not in config files
- Use different tokens for different environments (dev/prod)
- Rotate tokens regularly for security

### 2. Rate Limiting
- Respect platform rate limits
- Use batch operations when possible
- Implement backoff strategies for failed requests

### 3. Storage Management
- Set appropriate retention periods (default: 90 days)
- Regularly clean up old data
- Monitor database sizes and performance

### 4. Alert Thresholds
- Adjust confidence thresholds based on use case
- Set appropriate trigger frequencies
- Test alert rules before production deployment

### 5. Monitoring
- Use continuous monitoring for critical alerts
- Monitor storage sizes and disk usage
- Track collector uptime and error rates

---

## Troubleshooting

### Common Issues

**"VADER not installed"**
```bash
pip install vaderSentiment
```

**"ChromaDB error"**
```bash
pip install chromadb
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

## Configuration Reference

### Analysis Configuration
```yaml
analysis:
  sentiment_model: "vader"        # Options: vader, finbert, llm
  entity_extraction: true             # Enable entity extraction
  trend_detection: true               # Enable trend detection
  deduplication_threshold: 0.85      # Similarity threshold (0-1)
```

### Storage Configuration
```yaml
storage:
  retention_days: 90                  # Data retention period
  vector_db_path: "data/vector_db"  # ChromaDB location
  document_store_path: "data/documents" # SQLite location
```

### Alert Configuration
```yaml
alerts:
  enabled_channels: ["discord"]       # Output channels
  triggers: ["trend_spike", "high_confidence", ...]
  min_confidence: 0.7                 # Minimum confidence (0-1)
```

---

## Contributing

To extend the skill:

1. **Add a new collector:** Inherit from `BaseCollector` and implement `collect()` and `search()`
2. **Add a new analyzer:** Create a new class in `analyzers/` directory
3. **Add a new storage backend:** Implement interface in `storage/` directory
4. **Update tests:** Add test cases for new functionality

See `CONTRIBUTING.md` for detailed guidelines.

---

## Documentation

- **Full Documentation:** https://github.com/kvothe-assistant/avalanche-intelligence-skill
- **API Docs:** See inline docstrings in each module
- **Configuration Examples:** `config/config.example.yaml`

---

## License

MIT License - See `LICENSE` file

---

## Quick Reference

```bash
# Common commands
avalanche-intelligence init              # Initialize
avalanche-intelligence test              # Test install
avalanche-intelligence status            # System status
avalanche-intelligence scan --hours 24  # Collect data
avalanche-intelligence search "query"     # Search
avalanche-intelligence report             # Generate report
avalanche-intelligence watch --daemon    # Monitor

# Configuration
config/config.yaml                     # Main config
config/config.example.yaml             # Template

# Data locations
data/raw/                            # Raw collected data
data/processed/                       # Processed data
data/vector_db/                        # ChromaDB database
data/documents/                        # SQLite database
```

---

**Created:** 2026-02-21
**Version:** 1.0.0
**Status:** Production-Ready ✅
