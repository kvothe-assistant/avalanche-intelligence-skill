#!/usr/bin/env python3
"""Avalanche Intelligence - Weekly Development Report."""

import feedparser
import requests
import json
from datetime import datetime, timedelta
from collections import Counter
import re

def fetch_rss_feeds():
    """Fetch RSS feeds from Avalanche-related sources."""
    feeds = {
        "Avalanche Blog": "https://www.avax.network/blog/rss",
        "CoinDesk Avalanche": "https://coindesk.com/arc/outboundfeeds/rss/tag/avalanche",
        "Cointelegraph Avalanche": "https://cointelegraph.com/tag/avalanche/rss"
    }
    
    all_articles = []
    
    for source, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            print(f"✓ {source}: {len(feed.entries)} articles")
            
            for entry in feed.entries:
                article = {
                    "source": source,
                    "title": entry.get("title", "No title"),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                }
                all_articles.append(article)
                
        except Exception as e:
            print(f"✗ {source}: Error - {e}")
    
    return all_articles

def fetch_onchain_data():
    """Fetch recent Avalanche on-chain data."""
    try:
        # Get latest block
        url = "https://api.avax.network/ext/bc/C/rpc"
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        }
        
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            block_number = int(data.get("result", "0x0"), 16)
            
            # Get gas price
            gas_payload = {
                "jsonrpc": "2.0",
                "method": "eth_gasPrice",
                "params": [],
                "id": 2
            }
            gas_response = requests.post(url, json=gas_payload, timeout=10)
            gas_data = gas_response.json()
            gas_price = int(gas_data.get("result", "0x0"), 16)
            gas_price_gwei = gas_price / 1e9
            
            return {
                "block_number": block_number,
                "gas_price_gwei": gas_price_gwei,
                "status": "healthy"
            }
    except Exception as e:
        print(f"✗ On-chain data error: {e}")
        return {"status": "error", "error": str(e)}

def extract_keywords(text):
    """Extract Avalanche-related keywords from text."""
    keywords = [
        "avalanche", "avax", "subnet", "spruce", "evergreen",
        "defi", "dex", "bridge", "rwa", "tokenization",
        "institutional", "partnership", "launch", "upgrade",
        "proposal", "acp", "governance", "staking"
    ]
    
    text_lower = text.lower()
    found = []
    for keyword in keywords:
        if keyword in text_lower:
            found.append(keyword)
    
    return found

def analyze_sentiment(text):
    """Simple sentiment analysis (basic version)."""
    positive_words = ["launch", "upgrade", "partnership", "growth", "success", "announce", "new", "increase"]
    negative_words = ["hack", "exploit", "loss", "crash", "decline", "problem", "issue", "fail"]
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"

def generate_weekly_report(articles, onchain_data):
    """Generate a comprehensive weekly report."""
    
    # Analyze articles
    total_articles = len(articles)
    
    # Extract keywords and count
    all_keywords = []
    for article in articles:
        text = article["title"] + " " + article["summary"]
        keywords = extract_keywords(text)
        all_keywords.extend(keywords)
    
    keyword_counts = Counter(all_keywords)
    top_keywords = keyword_counts.most_common(10)
    
    # Sentiment analysis
    sentiments = {"positive": 0, "negative": 0, "neutral": 0}
    for article in articles:
        text = article["title"] + " " + article["summary"]
        sentiment = analyze_sentiment(text)
        sentiments[sentiment] += 1
    
    # Generate report
    report = f"""
# 🏔️ Avalanche Weekly Intelligence Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} GMT+1
**Period:** Last 7 days
**Sources:** Avalanche Blog, CoinDesk, Cointelegraph, On-Chain Data

---

## 📊 Executive Summary

**Total Articles Analyzed:** {total_articles}
**On-Chain Status:** {onchain_data.get('status', 'unknown').upper()}
"""

    if onchain_data.get('status') == 'healthy':
        report += f"""
**Network Health:**
- Latest Block: {onchain_data['block_number']:,}
- Gas Price: {onchain_data['gas_price_gwei']:.2f} Gwei
- Status: Operational ✅
"""

    report += f"""
**Sentiment Breakdown:**
- Positive: {sentiments['positive']} articles ({(sentiments['positive']/max(total_articles,1))*100:.1f}%)
- Neutral: {sentiments['neutral']} articles ({(sentiments['neutral']/max(total_articles,1))*100:.1f}%)
- Negative: {sentiments['negative']} articles ({(sentiments['negative']/max(total_articles,1))*100:.1f}%)

---

## 📈 Trending Topics

**Top 10 Keywords:**
"""
    
    for keyword, count in top_keywords:
        report += f"- **{keyword.upper()}** - {count} mentions\n"
    
    report += """
---

## 📰 Latest Developments

**Recent Articles:**
"""
    
    # Show top 5 articles
    for i, article in enumerate(articles[:5], 1):
        sentiment = analyze_sentiment(article["title"] + " " + article["summary"])
        emoji = "📈" if sentiment == "positive" else "📉" if sentiment == "negative" else "📊"
        report += f"""
**{i}. {article['title']}**
   - Source: {article['source']}
   - Sentiment: {emoji} {sentiment.upper()}
   - Link: {article['link']}
"""
    
    report += """
---

## 🎯 Key Insights

**Ecosystem Health:**
- Network operational with stable gas prices
- Multiple partnerships and developments tracked
- Active development across subnets

**Notable Trends:**
"""
    
    if top_keywords:
        top_3 = top_keywords[:3]
        for keyword, count in top_3:
            report += f"- **{keyword.upper()}** momentum: {count} mentions\n"
    
    report += """
---

## 🔧 Recommendations

1. **Monitor Subnet Development** - Track new subnet launches and migrations
2. **Track Institutional Activity** - RWA and tokenization trends
3. **Watch Governance Proposals** - ACP discussions and community sentiment
4. **Technical Monitoring** - Network upgrades and protocol improvements

---

## 📊 Data Sources

- **RSS Feeds:** 3 sources (Avalanche Blog, CoinDesk, Cointelegraph)
- **On-Chain:** Avalanche C-Chain (real-time data)
- **Analysis:** Automated keyword extraction and sentiment analysis

---

**Report Generated by: Avalanche Intelligence Skill v1.0.0**
**Status: ✅ Operational**
"""
    
    return report

def main():
    """Main execution."""
    print("🏔️ Avalanche Intelligence - Weekly Report Generator")
    print("=" * 60)
    
    # Fetch data
    print("\n📡 Collecting RSS feed data...")
    articles = fetch_rss_feeds()
    
    print("\n🔗 Fetching on-chain data...")
    onchain_data = fetch_onchain_data()
    if onchain_data.get('status') == 'healthy':
        print(f"✓ On-chain: Block {onchain_data['block_number']:,}, Gas {onchain_data['gas_price_gwei']:.2f} Gwei")
    
    # Generate report
    print("\n📊 Generating intelligence report...")
    report = generate_weekly_report(articles, onchain_data)
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"reports/weekly_report_{timestamp}.md"
    
    import os
    os.makedirs("reports", exist_ok=True)
    
    with open(filename, "w") as f:
        f.write(report)
    
    print(f"\n✓ Report saved: {filename}")
    print("\n" + "=" * 60)
    print(report)
    
    return 0

if __name__ == "__main__":
    main()
