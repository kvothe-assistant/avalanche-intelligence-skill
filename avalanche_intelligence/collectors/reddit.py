"""Reddit data collector using PRAW."""

import asyncio
import praw
from typing import List, Dict, Any
from datetime import datetime, timedelta

from .base import BaseCollector


class RedditCollector(BaseCollector):
    """Collector for Reddit data using PRAW."""

    def __init__(self, config):
        super().__init__("reddit", config)
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.user_agent = config.user_agent
        self.subreddits = config.subreddits
        self._reddit = None

    def _get_reddit_instance(self):
        """Get Reddit instance (lazy initialization)."""
        if self._reddit is None and self.client_id and self.client_secret:
            self._reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
            )
        return self._reddit

    async def collect(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Collect posts from configured subreddits.

        Args:
            hours: Number of hours of historical data to collect

        Returns:
            List of Reddit post objects with metadata
        """
        if not self.client_id or not self.client_secret:
            print("Warning: Reddit credentials not configured")
            return []

        posts = []
        reddit = self._get_reddit_instance()

        if not reddit:
            return []

        for subreddit_name in self.subreddits[:10]:  # Limit to first 10 subreddits
            try:
                subreddit = reddit.subreddit(subreddit_name)

                # Fetch new posts
                for submission in subreddit.new(limit=100):
                    post = self._parse_submission(submission)
                    posts.append(post)

            except Exception as e:
                print(f"Error fetching from r/{subreddit_name}: {e}")

        # Filter by time and remove duplicates
        filtered = self._filter_by_time(posts, hours)
        seen_ids = set()
        unique_posts = []

        for post in filtered:
            post_id = post.get("id")
            if post_id and post_id not in seen_ids:
                seen_ids.add(post_id)
                unique_posts.append(post)

        return unique_posts

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search posts by query.

        Args:
            query: Search query

        Returns:
            List of matching posts
        """
        reddit = self._get_reddit_instance()

        if not reddit:
            return []

        posts = []

        try:
            for subreddit_name in self.subreddits[:5]:
                subreddit = reddit.subreddit(subreddit_name)

                for submission in subreddit.search(query, limit=20, sort="relevance"):
                    post = self._parse_submission(submission)
                    posts.append(post)

        except Exception as e:
            print(f"Error searching Reddit: {e}")

        return posts

    def _parse_submission(self, submission) -> Dict[str, Any]:
        """Parse Reddit submission into standardized format.

        Args:
            submission: PRAW submission object

        Returns:
            Standardized post object
        """
        return {
            "id": submission.id,
            "source": "reddit",
            "content": f"{submission.title}\n\n{submission.selftext if submission.is_self else submission.url}",
            "timestamp": datetime.fromtimestamp(submission.created_utc).isoformat(),
            "author": {
                "id": str(submission.author) if submission.author else "[deleted]",
                "username": str(submission.author) if submission.author else "[deleted]",
                "karma": submission.author.link_karma if submission.author else 0,
            },
            "engagement": {
                "upvotes": submission.score,
                "comments": submission.num_comments,
                "awards": len(submission.all_awardings) if hasattr(submission, 'all_awardings') else 0,
            },
            "entities": self._extract_entities(submission),
            "url": f"https://reddit.com{submission.permalink}",
            "collected_at": datetime.now().isoformat(),
            "subreddit": submission.subreddit.display_name,
        }

    def _extract_entities(self, submission) -> List[str]:
        """Extract entities from submission.

        Args:
            submission: PRAW submission object

        Returns:
            List of entity strings
        """
        entities = []

        # Subreddit
        entities.append(submission.subreddit.display_name)

        # Flairs
        if submission.link_flair_text:
            entities.append(submission.link_flair_text)

        # Tickering (check for cashtags in title/selftext)
        text = f"{submission.title} {submission.selftext if submission.is_self else ''}"
        for word in text.split():
            if word.startswith("$") and len(word) > 1:
                entities.append(word)

        return entities
