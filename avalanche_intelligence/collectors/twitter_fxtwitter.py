"""Twitter/X data collector using fxtwitter (free, no auth)."""

import sys
import os
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Add fxtwitter tool to path
sys.path.insert(0, '/home/kvothe/.openclaw/workspace/tools')

try:
    import fxtwitter
    FXTWITTER_AVAILABLE = True
except ImportError:
    FXTWITTER_AVAILABLE = False

from .base import BaseCollector


class TwitterCollector(BaseCollector):
    """Collector for Twitter/X data using fxtwitter (free, no auth required)."""

    def __init__(self, config):
        super().__init__("twitter", config)
        self.track_keywords = getattr(config, 'track_keywords', [])
        self.follow_accounts = getattr(config, 'follow_accounts', [])
        self._tweets = []

    async def collect(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Collect recent tweets from tracked accounts.

        Note: fxtwitter fetches individual tweets/users, not search streams.
        For comprehensive monitoring, we fetch from tracked accounts.

        Args:
            hours: Number of hours of historical data to collect

        Returns:
            List of tweet objects with metadata
        """
        if not FXTWITTER_AVAILABLE:
            print("Warning: fxtwitter not available")
            return []

        tweets = []

        # Fetch from followed accounts
        for account in self.follow_accounts[:20]:  # Limit to 20 accounts
            try:
                # Get user profile
                user_data = fxtwitter.fetch_user(account)
                
                if 'error' not in user_data:
                    # Parse user data
                    tweet = self._parse_user_to_tweet(user_data, account)
                    if tweet:
                        tweets.append(tweet)
                        
            except Exception as e:
                print(f"Error fetching from @{account}: {e}")

        # Filter by time
        filtered = self._filter_by_time(tweets, hours, "timestamp")

        # Remove duplicates
        seen_ids = set()
        unique_tweets = []
        for tweet in filtered:
            tweet_id = tweet.get("id")
            if tweet_id and tweet_id not in seen_ids:
                seen_ids.add(tweet_id)
                unique_tweets.append(tweet)

        return unique_tweets

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search is not available via fxtwitter (requires authenticated API).

        Args:
            query: Search query

        Returns:
            Empty list (feature not available)
        """
        # fxtwitter doesn't support search - would need official Twitter API
        print("Note: Search requires official Twitter API (not available via fxtwitter)")
        return []

    def _parse_user_to_tweet(self, user_data: Dict, username: str) -> Dict[str, Any]:
        """Parse user data into tweet format.

        Args:
            user_data: User data from fxtwitter
            username: Username

        Returns:
            Tweet object
        """
        try:
            # Extract relevant fields
            user_info = user_data.get('user', {})
            
            return {
                "id": f"user_{username}",
                "source": "twitter",
                "content": f"User profile: @{username} - {user_info.get('description', '')}",
                "timestamp": datetime.now().isoformat(),
                "author": {
                    "id": str(user_info.get('id', '')),
                    "username": username,
                    "name": user_info.get('name', ''),
                    "verified": user_info.get('verified', False),
                    "followers": user_info.get('followers_count', 0),
                    "following": user_info.get('friends_count', 0),
                },
                "engagement": {
                    "followers": user_info.get('followers_count', 0),
                    "tweets": user_info.get('statuses_count', 0),
                },
                "entities": [username],
                "url": f"https://twitter.com/{username}",
                "collected_at": datetime.now().isoformat(),
            }
            
        except Exception as e:
            print(f"Error parsing user data: {e}")
            return None

    def fetch_tweet_by_url(self, url: str) -> Dict[str, Any]:
        """Fetch a specific tweet by URL.

        Args:
            url: Twitter/X URL

        Returns:
            Tweet data
        """
        if not FXTWITTER_AVAILABLE:
            return {"error": "fxtwitter not available"}

        try:
            # Parse URL
            parsed = fxtwitter.parse_twitter_url(url)
            
            if parsed:
                # Fetch tweet
                tweet_data = fxtwitter.fetch_tweet(
                    parsed['username'],
                    parsed['status_id']
                )
                
                if 'error' not in tweet_data:
                    return self._parse_tweet_data(tweet_data)
                else:
                    return tweet_data
            else:
                return {"error": "Invalid Twitter URL"}
                
        except Exception as e:
            return {"error": str(e)}

    def _parse_tweet_data(self, tweet_data: Dict) -> Dict[str, Any]:
        """Parse tweet data from fxtwitter.

        Args:
            tweet_data: Tweet data from fxtwitter

        Returns:
            Standardized tweet object
        """
        try:
            tweet = tweet_data.get('tweet', {})
            author = tweet_data.get('author', {})
            
            return {
                "id": tweet.get('id_str', ''),
                "source": "twitter",
                "content": tweet.get('text', ''),
                "timestamp": tweet.get('created_at', ''),
                "author": {
                    "id": str(author.get('id_str', '')),
                    "username": author.get('screen_name', ''),
                    "name": author.get('name', ''),
                    "verified": author.get('verified', False),
                    "followers": author.get('followers_count', 0),
                },
                "engagement": {
                    "likes": tweet.get('favorite_count', 0),
                    "retweets": tweet.get('retweet_count', 0),
                    "replies": tweet.get('reply_count', 0),
                },
                "entities": self._extract_entities(tweet),
                "url": f"https://twitter.com/{author.get('screen_name', '')}/status/{tweet.get('id_str', '')}",
                "collected_at": datetime.now().isoformat(),
            }
            
        except Exception as e:
            print(f"Error parsing tweet: {e}")
            return {"error": str(e)}

    def _extract_entities(self, tweet: Dict) -> List[str]:
        """Extract entities from tweet.

        Args:
            tweet: Tweet object

        Returns:
            List of entities
        """
        entities = []
        
        # Hashtags
        for tag in tweet.get('entities', {}).get('hashtags', []):
            entities.append(f"#{tag.get('text', '')}")
        
        # Mentions
        for mention in tweet.get('entities', {}).get('user_mentions', []):
            entities.append(f"@{mention.get('screen_name', '')}")
        
        # URLs
        for url in tweet.get('entities', {}).get('urls', []):
            entities.append(url.get('expanded_url', ''))
        
        return entities
