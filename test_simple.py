#!/usr/bin/env python3
"""Simple test for Avalanche Intelligence - RSS and On-chain only."""

import feedparser

def test_rss():
    """Test RSS feed parsing."""
    try:
        feed = feedparser.parse('https://www.avax.network/blog/rss')
        print(f"✓ RSS test: {len(feed.entries)} entries parsed")
        return True
    except Exception as e:
        print(f"✗ RSS test failed: {e}")
        return False

def test_onchain():
    """Test on-chain data fetching (basic)."""
    import requests
    
    try:
        url = "https://api.avax.network/ext/bc/C/rpc"
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        }
        
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            block_number = int(data.get("result", "0x0"), 16)
            print(f"✓ On-chain test: Current block {block_number}")
            return True
        else:
            print(f"✗ On-chain test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ On-chain test failed: {e}")
        return False

def main():
    """Run simple tests."""
    print("Testing Avalanche Intelligence (RSS + On-chain only)...")
    
    rss_ok = test_rss()
    onchain_ok = test_onchain()
    
    if rss_ok and onchain_ok:
        print("\\n✓ All tests passed!")
        return 0
    else:
        print("\\n✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    main()
