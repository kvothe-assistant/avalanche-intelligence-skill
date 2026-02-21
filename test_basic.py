#!/usr/bin/env python3
"""Simple test for Avalanche Intelligence skill."""

import sys
import click
import requests
import feedparser

print('Testing basic collectors...')

# Test RSS collector
try:
    rss_feed = feedparser.parse('https://www.avax.network/blog/rss')
    print(f'✓ RSS feed parsed: {len(rss_feed.entries)} entries')
except Exception as e:
    print(f'✗ RSS feed error: {e}')

print('\\n✓ Basic test completed!')