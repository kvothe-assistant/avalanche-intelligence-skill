# Avalanche Intelligence Skill

An OpenClaw skill for real-time monitoring, analysis, and reporting on the Avalanche blockchain ecosystem.

## Overview

This skill aggregates data from multiple sources to provide holistic intelligence on:
- 🔥 **Latest Trends** - What's hot in AVAX ecosystem
- 🏗️ **Major Projects** - New launches, partnerships, migrations
- 😊 **User Sentiment** - Social media mood analysis
- 📈 **Adoption Metrics** - TVL, addresses, transaction volume
- 🔧 **Technology Upgrades** - ACPs, hard forks, infrastructure changes

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your Twitter, Reddit, Discord credentials

# Test the skill
python -m avalanche_intelligence test

# Run a scan
python -m avalanche_intelligence scan --hours 24
```

## Architecture

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
│  └── Deduplicator (vector similarity)                       │
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

## Data Sources

| Category | Sources | Frequency |
|----------|---------|-----------|
| **On-Chain** | Avalanche C-Chain, Subnet explorers (SnowTrace, Avascan) | Real-time via RPC |
| **Social** | Twitter/X API v2, Reddit (r/avalancheavax), Discord (official servers) | Hourly |
| **News** | CoinDesk, The Block, DL News, official Ava Labs blog | Hourly |
| **GitHub** | avalanche-foundation repos, subnet projects | Daily |
| **Financial** | CoinGecko, CoinMarketCap, DeFiLlama | 15-min |
| **Governance** | Avalanche proposal forum, ACP discussions | Daily |

## Features

### Smart Filtering
- Minimum engagement thresholds
- Verified-only filtering
- ML-based bot detection
- Language filtering
- Sentiment range filtering

### Entity Linking
- Auto-link entities across sources
- Relationship mapping
- Influence scoring
- Momentum tracking

### Trend Detection
- Emerging trend identification (3x spike)
- Viral trend detection (10x spike)
- Time-window analysis
- Multi-source correlation

### Sentiment Analysis
- Multi-model aggregation (VADER, FinBERT, LLM)
- Weighted composite scores
- Domain-specific analysis
- Context-aware interpretation

## Configuration

See `config/config.example.yaml` for full configuration options.

Required API keys:
- **Twitter** - Bearer token from developer.twitter.com
- **Reddit** - Client ID/secret from reddit.com/prefs/apps
- **Discord** - Bot token and webhook URL
- **GitHub** - Personal access token (optional, for private repos)

## Usage Examples

```bash
# Scan last 24 hours from all sources
python -m avalanche_intelligence scan --hours 24

# Scan specific sources
python -m avalanche_intelligence scan --hours 24 --sources twitter,reddit

# Generate daily report
python -m avalanche_intelligence report --timeframe 24h --format markdown

# Search across all data
python -m avalanche_intelligence search "spruce testnet"

# Start continuous monitoring
python -m avalanche_intelligence watch --interval 900

# Sentiment analysis
python -m avalanche_intelligence sentiment --source twitter --keyword subnet

# Project discovery
python -m avalanche_intelligence projects --category defi --new-only
```

## Project Status

- ✅ Repository structure
- ✅ Skill specification (SKILL.md)
- ✅ CLI interface framework
- ✅ Base collector interface
- ✅ Configuration system
- 🚧 Twitter collector (in progress)
- 🚧 Reddit collector (in progress)
- 🚧 Sentiment analysis (planned)
- 🚧 Entity extraction (planned)
- 🚧 Trend detection (planned)
- 🚧 Storage backends (planned)
- 🚧 Alert system (planned)

## License

MIT License

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

---

**Repository:** https://github.com/kvothe-assistant/avalanche-intelligence-skill
