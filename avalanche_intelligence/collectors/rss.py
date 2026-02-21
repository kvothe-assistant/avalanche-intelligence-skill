"""RSS feed collector using feedparser."""

import feedparser
from typing import List, Dict, Any
from datetime import datetime, timedelta

from .base import BaseCollector


class RSSCollector(BaseCollector):
    """Collector for RSS/Atom feeds."""

    def __init__(self, config):
        super().__init__("rss", config)
        self.feeds = config.feeds
        self.rate_limit_per_hour = config.rate_limit_per_hour

    async def collect(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Collect articles from RSS feeds.

        Args:
            hours: Number of hours of historical data to collect

        Returns:
            List of article objects with metadata
        """
        if not self.feeds:
            print("Warning: No RSS feeds configured")
            return []

        articles = []

        for feed_url in self.feeds:
            try:
                feed_articles = await self._fetch_feed(feed_url, hours)
                articles.extend(feed_articles)
            except Exception as e:
                print(f"Error fetching feed {feed_url}: {e}")

        # Remove duplicates (by URL)
        seen_urls = set()
        unique_articles = []

        for article in articles:
            url = article.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)

        return unique_articles

    async def _fetch_feed(self, feed_url: str, hours: int) -> List[Dict[str, Any]]:
        """Fetch articles from a single RSS feed.

        Args:
            feed_url: URL of the RSS feed
            hours: Number of hours to filter

        Returns:
            List of articles
        """
        articles = []
        start_time = datetime.now() - timedelta(hours=hours)

        try:
            # Parse feed
            feed = feedparser.parse(feed_url)

            # Extract feed info
            feed_title = feed.get("feed", {}).get("title", "Unknown Feed")
            feed_description = feed.get("feed", {}).get("description", "")

            # Parse entries
            for entry in feed.entries:
                article = self._parse_entry(entry, feed_title, feed_url)

                # Filter by time
                if article["timestamp"]:
                    article_time = datetime.fromisoformat(article["timestamp"])
                    if article_time > start_time:
                        articles.append(article)

            print(f"  ✓ {feed_title}: {len(articles)} articles")

        except Exception as e:
            print(f"Error parsing feed {feed_url}: {e}")

        return articles

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search collected articles.

        Args:
            query: Search query

        Returns:
            List of matching articles
        """
        # For RSS, we need to fetch from feeds and search
        # This is not ideal - in production, we'd search from storage
        query_lower = query.lower()

        all_articles = []
        for feed_url in self.feeds[:5]:  # Limit to 5 feeds for search
            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries:
                    article = self._parse_entry(
                        entry,
                        feed.get("feed", {}).get("title", "Unknown Feed"),
                        feed_url
                    )

                    # Check if query matches
                    content_lower = article["content"].lower()
                    title_lower = article["title"].lower()

                    if query_lower in content_lower or query_lower in title_lower:
                        # Calculate relevance
                        relevance = min(1.0, 0.1 + content_lower.count(query_lower) * 0.05)
                        article["relevance"] = relevance
                        all_articles.append(article)

            except Exception as e:
                print(f"Error searching feed {feed_url}: {e}")

        # Sort by relevance and time
        all_articles.sort(key=lambda x: (x["relevance"], x["timestamp"]), reverse=True)

        return all_articles

    def _parse_entry(
        self,
        entry: feedparser.FeedParserDict,
        feed_title: str,
        feed_url: str
    ) -> Dict[str, Any]:
        """Parse RSS entry into standardized format.

        Args:
            entry: Feedparser entry object
            feed_title: Source feed title
            feed_url: Source feed URL

        Returns:
            Standardized article object
        """
        # Extract content
        content = ""
        if hasattr(entry, "content") and entry.content:
            content = entry.content[0].get("value", "")
        elif hasattr(entry, "summary"):
            content = entry.summary
        elif hasattr(entry, "description"):
            content = entry.description

        # Strip HTML tags from content
        content = self._strip_html(content)

        # Extract timestamp
        timestamp = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            timestamp = datetime(*entry.published_parsed[:6]).isoformat()
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            timestamp = datetime(*entry.updated_parsed[:6]).isoformat()

        # Extract author
        author = ""
        if hasattr(entry, "author"):
            author = entry.author
        elif hasattr(entry, "author_detail") and entry.author_detail:
            author = entry.author_detail.get("name", "")

        # Extract URL
        url = ""
        if hasattr(entry, "link"):
            url = entry.link
        elif hasattr(entry, "id"):
            url = entry.id

        # Extract tags/categories
        entities = []
        if hasattr(entry, "tags"):
            entities = [tag.term for tag in entry.tags if hasattr(tag, "term")]

        # Extract enclosure (media)
        media_url = None
        if hasattr(entry, "enclosures") and entry.enclosures:
            media_url = entry.enclosures[0].get("href", "")

        return {
            "id": getattr(entry, "id", url),
            "source": "rss",
            "title": getattr(entry, "title", "No title"),
            "content": content,
            "timestamp": timestamp,
            "author": {
                "name": author,
                "source_feed": feed_title,
            },
            "url": url,
            "media_url": media_url,
            "entities": entities,
            "feed_url": feed_url,
            "collected_at": datetime.now().isoformat(),
        }

    def _strip_html(self, html: str) -> str:
        """Strip HTML tags from string.

        Args:
            html: HTML string

        Returns:
            Plain text string
        """
        import re

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)

        # Remove HTML entities
        text = re.sub(r'&[a-zA-Z]+;', '', text)

        # Clean up whitespace
        text = ' '.join(text.split())

        return text
