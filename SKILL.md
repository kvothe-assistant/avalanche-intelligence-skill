# Avalanche Intelligence Skill

A comprehensive OpenClaw skill for real-time monitoring, analysis, and reporting on the Avalanche blockchain ecosystem.

## Overview

This skill aggregates data from multiple sources to provide holistic intelligence on:
- 🔥 **Latest Trends** - What's hot in AVAX ecosystem
- 🏗️ **Major Projects** - New launches, partnerships, migrations
- 😊 **User Sentiment** - Social media mood analysis
- 📈 **Adoption Metrics** - TVL, addresses, transaction volume
- 🔧 **Technology Upgrades** - ACPs, hard forks, infrastructure changes

## Architecture

### Data Sources

| Category | Sources | Frequency |
|----------|---------|-----------|
| **On-Chain** | Avalanche C-Chain, Subnet explorers (SnowTrace, Avascan) | Real-time via RPC |
| **Social** | Twitter/X API v2, Reddit (r/avalancheavax), Discord (official servers) | Hourly |
| **News** | CoinDesk, The Block, DL News, official Ava Labs blog | Hourly |
| **GitHub** | avalanche-foundation repos, subnet projects | Daily |
| **Financial** | CoinGecko, CoinMarketCap, DeFiLlama | 15-min |
| **Governance** | Avalanche proposal forum, ACP discussions | Daily |

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    AVALANCHE INTELLIGENCE                     │
├─────────────────────────────────────────────────────────────┤
│  INGESTION LAYER                                            │
│  ├── Web Scraper (Playwright)                               │
│  ├── API Clients (Twitter, Reddit, Discord)                   │
│  ├── RSS Aggregator (news feeds)                            │
│  └── On-Chain Listener (WebSocket RPC)                      │
├─────────────────────────────────────────────────────────────┤
│  PROCESSING LAYER                                           │
│  ├── Sentiment Analyzer (local LLM/VADER)                   │
│  ├── Entity Extractor (projects, people, tech)              │
│  ├── Trend Detector (spike detection, anomaly)              │
│  └── Deduplicatpr (vector similarity)                       │
├─────────────────────────────────────────────────────────────┤
│  STORAGE LAYER                                              │
│  ├── Vector DB (ChromaDB for semantic search)               │
│  ├── Time-Series DB (InfluxDB for metrics)                  │
│  └── Document Store (MongoDB for articles)                  │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT LAYER                                               │
│  ├── Dashboard (real-time web UI)                           │
│  ├── Alerts (Discord/Signal/Telegram)                       │
│  ├── Reports (Markdown/HTML/PDF)                            │
│  └── API (REST/GraphQL)                                     │
└─────────────────────────────────────────────────────────────┘
```

## Implementation

### Command Structure

```bash
# Real-time monitoring
avalanche-intelligence watch [--interval 15m] [--alert-threshold high]

# Generate reports
avalanche-intelligence report [--timeframe 24h|7d|30d] [--format markdown]

# Sentiment analysis
avalanche-intelligence sentiment [--source twitter|reddit|all] [--keyword subnet]

# Project discovery
avalanche-intelligence projects [--category defi|gaming|rwa] [--new-only]

# Technology tracking
avalanche-intelligence tech [--acps] [--upgrades] [--testnets]

# Search across all data
avalanche-intelligence search "evergreen spruce testnet"
```

### Key Features

#### 1. Smart Filtering
```python
# Only capture high-signal content
filters = {
    "min_engagement": 10,      # Skip tweets with <10 likes
    "verified_only": False,    # Option to filter noise
    "exclude_bots": True,      # ML-based bot detection
    "language": ["en", "tr"],  # Focus languages
    "sentiment_range": [-0.5, 1.0]  # Exclude extreme negativity spam
}
```

#### 2. Entity Linking
```python
# Auto-link entities across sources
entities = {
    "Spruce": {
        "type": "testnet",
        "related": ["Evergreen", "T. Rowe Price", "WisdomTree"],
        "mentions": 45,
        "sentiment": 0.72
    },
    "FUSD": {
        "type": "stablecoin",
        "issuer": "Fosun Wealth",
        "tvl": "$50M",
        "launch_date": "2026-02-01"
    }
}
```

#### 3. Trend Detection
```python
# Detect emerging trends before they explode
def detect_trending(topic, window="6h"):
    current = count_mentions(topic, window="now")
    baseline = count_mentions(topic, window=f"-{window} to -{window}")
    
    spike_ratio = current / baseline if baseline > 0 else float('inf')
    
    if spike_ratio > 3:
        return {"trend": "emerging", "multiplier": spike_ratio}
    elif spike_ratio > 10:
        return {"trend": "viral", "multiplier": spike_ratio}
```

#### 4. Sentiment Analysis
```python
# Multi-model sentiment for accuracy
sentiment_models = {
    "vader": "baseline twitter sentiment",
    "finbert": "financial domain-specific",
    "local_llm": "nuanced context understanding"
}

# Aggregate scores across models
composite_sentiment = weighted_average([
    vader_score * 0.3,
    finbert_score * 0.4,
    llm_score * 0.3
])
```

### Data Schemas

#### Social Post
```json
{
    "id": "tweet_1892345678901",
    "source": "twitter",
    "author": {
        "handle": "@avalanche_insider",
        "followers": 12500,
        "verified": false,
        "influence_score": 0.73
    },
    "content": "Just tested the Spruce testnet - instant finality is no joke...",
    "timestamp": "2026-02-18T14:23:00Z",
    "engagement": {
        "likes": 156,
        "replies": 23,
        "retweets": 45
    },
    "entities": ["Spruce", "Evergreen", "institutional"],
    "sentiment": 0.82,
    "category": "technology",
    "collected_at": "2026-02-18T14:25:00Z"
}
```

#### Project
```json
{
    "name": "Galaxy CLO 2025-1",
    "category": "rwa",
    "status": "live",
    "subnet": null,
    "tvl": "$75M",
    "partners": ["Galaxy Digital", "Arch Lending", "Grove", "INX"],
    "launch_date": "2026-01-15",
    "signals": [
        {"type": "twitter_mention", "count": 89, "sentiment": 0.71},
        {"type": "news_article", "count": 5, "sources": ["The Block", "CoinDesk"]},
        {"type": "onchain", "metric": "total_minted", "value": 75000000}
    ],
    "momentum_score": 0.88
}
```

## Configuration

### OpenClaw Integration

```yaml
# ~/.openclaw/skill-avalanche-intelligence.yaml
skill:
  name: avalanche-intelligence
  version: "1.0.0"
  
  # Data collection
  sources:
    twitter:
      enabled: true
      bearer_token: "${TWITTER_BEARER}"
      track_keywords: ["avalanche", "avax", "subnet", "avalanche9000"]
      follow_accounts: ["avalancheavax", "kevinsekniqi", "emingun sirer"]
      
    reddit:
      enabled: true
      subreddits: ["avalancheavax", "defi", "cryptocurrency"]
      
    discord:
      enabled: true
      guilds: ["Avalanche"]
      channels: ["announcements", "tech-talk"]
      
    rss:
      feeds:
        - "https://www.avax.network/blog/rss"
        - "https://cointelegraph.com/tag/avalanche/rss"
        - "https://coindesk.com/arc/outboundfeeds/rss/tag/avalanche"
        
  # Analysis
  analysis:
    sentiment_model: "vader"  # or "finbert", "local"
    entity_extraction: true
    trend_detection: true
    deduplication_threshold: 0.85
    
  # Storage
  storage:
    vector_db: "chromadb"
    time_series: "influxdb"
    retention_days: 90
    
  # Alerts
  alerts:
    channels: ["discord:#avalanche", "signal:gokcan83"]
    triggers:
