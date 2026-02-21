"""Twitter/X data collector using Twitter API v2."""

import aiohttp
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta

from .base import BaseCollector


class TwitterCollector(BaseCollector):
    """Collector for Twitter/X data using API v2."""

    API_BASE = "https://api.twitter.com/2"

    def __init__(self, config):
        super().__init__("twitter", config)
        self.bearer_token = config.bearer_token
        self.track_keywords = config.track_keywords
        self.follow_accounts = config.follow_accounts
        self.rate_limit_per_hour = config.rate_limit_per_hour

    async def collect(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Collect tweets from tracked keywords and accounts.

        Args:
            hours: Number of hours of historical data to collect

        Returns:
            List of tweet objects with metadata
        """
        if not self.bearer_token:
            print("Warning: Twitter bearer token not configured")
            return []

        tweets = []

        # Collect tweets from keywords
        if self.track_keywords:
            keyword_tweets = await self._search_by_keywords(hours)
            tweets.extend(keyword_tweets)

        # Collect tweets from followed accounts
        if self.follow_accounts:
            account_tweets = await self._fetch_from_accounts(hours)
            tweets.extend(account_tweets)

        # Remove duplicates (by tweet ID)
        seen_ids = set()
        unique_tweets = []
        for tweet in tweets:
            tweet_id = tweet.get("id")
            if tweet_id and tweet_id not in seen_ids:
                seen_ids.add(tweet_id)
                unique_tweets.append(tweet)

        return unique_tweets

    async def _search_by_keywords(self, hours: int) -> List[Dict[str, Any]]:
        """Search tweets by keywords.

        Args:
            hours: Number of hours to search

        Returns:
            List of tweets
        """
        tweets = []
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            for keyword in self.track_keywords[:10]:  # Limit to first 10 keywords
                try:
                    # Build search query
                    query = f"{keyword} lang:en -is:retweet"

                    params = {
                        "query": query,
                        "start_time": start_time,
                        "max_results": 100,
                        "tweet.fields": "created_at,public_metrics,author_id,entities",
                        "user.fields": "username,name,verified,public_metrics",
                        "expansions": "author_id"
                    }

                    async with session.get(
                        f"{self.API_BASE}/tweets/search/recent",
                        headers=headers,
                        params=params
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            if "data" in data:
                                tweets.extend(self._parse_tweets(data))
                        elif response.status == 429:
                            print(f"Rate limit exceeded for keyword: {keyword}")
                            await asyncio.sleep(60)  # Wait before retry
                        else:
                            print(f"Error fetching tweets for {keyword}: {response.status}")

                    # Rate limiting
                    await asyncio.sleep(1)

                except Exception as e:
                    print(f"Error searching keyword {keyword}: {e}")

        return tweets

    async def _fetch_from_accounts(self, hours: int) -> List[Dict[str, Any]]:
        """Fetch tweets from followed accounts.

        Args:
            hours: Number of hours to fetch

        Returns:
            List of tweets
        """
        tweets = []

        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            for account in self.follow_accounts[:20]:  # Limit to first 20 accounts
                try:
                    # Get user ID from username
                    async with session.get(
                        f"{self.API_BASE}/users/by/username/{account}",
                        headers=headers
                    ) as user_response:
                        if user_response.status == 200:
                            user_data = await user_response.json()
                            user_id = user_data["data"]["id"]

                            # Fetch user's tweets
                            params = {
                                "max_results": 100,
                                "tweet.fields": "created_at,public_metrics,entities",
                                "user.fields": "username,name,verified,public_metrics",
                                "expansions": "author_id"
                            }

                            async with session.get(
                                f"{self.API_BASE}/users/{user_id}/tweets",
                                headers=headers,
                                params=params
                            ) as tweets_response:
                                if tweets_response.status == 200:
                                    tweets_data = await tweets_response.json()
                                    if "data" in tweets_data:
                                        tweets.extend(self._parse_tweets(tweets_data))

                    await asyncio.sleep(1)

                except Exception as e:
                    print(f"Error fetching tweets from {account}: {e}")

        # Filter by time
        return self._filter_by_time(tweets, hours, "created_at")

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search tweets by query.

        Args:
            query: Search query

        Returns:
            List of matching tweets
        """
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }

        tweets = []

        async with aiohttp.ClientSession() as session:
            try:
                params = {
                    "query": f"{query} lang:en",
                    "max_results": 100,
                    "tweet.fields": "created_at,public_metrics,author_id,entities",
                    "user.fields": "username,name,verified,public_metrics",
                    "expansions": "author_id"
                }

                async with session.get(
                    f"{self.API_BASE}/tweets/search/recent",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        tweets = self._parse_tweets(data)

            except Exception as e:
                print(f"Error searching tweets: {e}")

        return tweets

    def _parse_tweets(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Twitter API response into standardized format.

        Args:
            data: Twitter API response data

        Returns:
            List of standardized tweet objects
        """
        tweets = []
        tweet_data = data.get("data", [])
        includes = data.get("includes", {})
        users = {u["id"]: u for u in includes.get("users", [])}

        for tweet in tweet_data:
            tweet_obj = {
                "id": tweet["id"],
                "source": "twitter",
                "content": tweet["text"],
                "timestamp": tweet["created_at"],
                "author": self._parse_author(tweet["author_id"], users),
                "engagement": {
                    "likes": tweet.get("public_metrics", {}).get("like_count", 0),
                    "replies": tweet.get("public_metrics", {}).get("reply_count", 0),
                    "retweets": tweet.get("public_metrics", {}).get("retweet_count", 0),
                    "quotes": tweet.get("public_metrics", {}).get("quote_count", 0),
                },
                "entities": self._parse_entities(tweet.get("entities", {})),
                "url": f"https://twitter.com/i/web/status/{tweet['id']}",
                "collected_at": datetime.now().isoformat(),
            }

            tweets.append(tweet_obj)

        return tweets

    def _parse_author(self, author_id: str, users: Dict) -> Dict[str, Any]:
        """Parse author information.

        Args:
            author_id: Author ID
            users: Dictionary of user data

        Returns:
            Author object
        """
        user = users.get(author_id, {})
        return {
            "id": author_id,
            "username": user.get("username", ""),
            "name": user.get("name", ""),
            "verified": user.get("verified", False),
            "followers": user.get("public_metrics", {}).get("followers_count", 0),
            "influence_score": self._calculate_influence(user),
        }

    def _parse_entities(self, entities: Dict[str, Any]) -> List[str]:
        """Extract entities from tweet entities.

        Args:
            entities: Tweet entities

        Returns:
            List of entity strings
        """
        extracted = []

        # Hashtags
        for tag in entities.get("hashtags", []):
            extracted.append(tag["tag"])

        # Mentions
        for mention in entities.get("mentions", []):
            extracted.append(f"@{mention['username']}")

        # URLs
        for url in entities.get("urls", []):
            extracted.append(url["expanded_url"])

        # Cashtags (stock/crypto symbols)
        for tag in entities.get("cashtags", []):
            extracted.append(f"${tag['tag']}")

        return extracted

    def _calculate_influence(self, user: Dict) -> float:
        """Calculate influence score for a user.

        Args:
            user: User object

        Returns:
            Influence score (0-1)
        """
        followers = user.get("public_metrics", {}).get("followers_count", 0)
        verified = user.get("verified", False)

        # Logarithmic influence score
        influence = 0
        if followers > 0:
            influence = min(0.8, 0.5 + 0.3 * (followers / 1000000) ** 0.5)

        if verified:
            influence += 0.2

        return min(1.0, influence)
