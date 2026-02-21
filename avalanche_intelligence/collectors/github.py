"""GitHub data collector using GitHub API."""

import aiohttp
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta

from .base import BaseCollector


class GitHubCollector(BaseCollector):
    """Collector for GitHub data using REST API."""

    API_BASE = "https://api.github.com"

    def __init__(self, config):
        super().__init__("github", config)
        self.access_token = config.access_token
        self.organizations = config.organizations
        self.repos = config.repositories
        self.rate_limit_per_hour = config.rate_limit_per_hour

    async def collect(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Collect events from monitored repositories.

        Args:
            hours: Number of hours of historical data to collect

        Returns:
            List of GitHub events with metadata
        """
        events = []

        headers = {}
        if self.access_token:
            headers["Authorization"] = f"token {self.access_token}"

        # Collect from organizations
        for org in self.organizations[:10]:
            org_events = await self._fetch_org_events(org, hours, headers)
            events.extend(org_events)

        # Collect from specific repositories
        for repo in self.repos[:20]:
            repo_events = await self._fetch_repo_events(repo, hours, headers)
            events.extend(repo_events)

        # Remove duplicates (by event ID)
        seen_ids = set()
        unique_events = []

        for event in events:
            event_id = event.get("id")
            if event_id and event_id not in seen_ids:
                seen_ids.add(event_id)
                unique_events.append(event)

        return unique_events

    async def _fetch_org_events(
        self,
        org: str,
        hours: int,
        headers: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Fetch events from an organization.

        Args:
            org: Organization name
            hours: Number of hours to fetch
            headers: HTTP headers

        Returns:
            List of events
        """
        events = []
        start_time = datetime.now() - timedelta(hours=hours)

        async with aiohttp.ClientSession() as session:
            try:
                params = {"per_page": 100}

                async with session.get(
                    f"{self.API_BASE}/orgs/{org}/events",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        for item in data:
                            event = self._parse_event(item)
                            # Filter by time
                            event_time = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
                            if event_time > start_time:
                                events.append(event)

                    elif response.status == 404:
                        print(f"Organization not found: {org}")
                    elif response.status == 403:
                        print(f"Rate limit exceeded for org: {org}")
                        await asyncio.sleep(60)

                await asyncio.sleep(1)

            except Exception as e:
                print(f"Error fetching events for org {org}: {e}")

        return events

    async def _fetch_repo_events(
        self,
        repo: str,
        hours: int,
        headers: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Fetch events from a repository.

        Args:
            repo: Repository name (format: owner/repo)
            hours: Number of hours to fetch
            headers: HTTP headers

        Returns:
            List of events
        """
        events = []
        start_time = datetime.now() - timedelta(hours=hours)

        async with aiohttp.ClientSession() as session:
            try:
                params = {"per_page": 100}

                async with session.get(
                    f"{self.API_BASE}/repos/{repo}/events",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        for item in data:
                            event = self._parse_event(item)
                            # Filter by time
                            event_time = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
                            if event_time > start_time:
                                events.append(event)

                    elif response.status == 404:
                        print(f"Repository not found: {repo}")
                    elif response.status == 403:
                        print(f"Rate limit exceeded for repo: {repo}")
                        await asyncio.sleep(60)

                await asyncio.sleep(1)

            except Exception as e:
                print(f"Error fetching events for repo {repo}: {e}")

        return events

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search repositories and code.

        Args:
            query: Search query

        Returns:
            List of matching items
        """
        results = []

        headers = {}
        if self.access_token:
            headers["Authorization"] = f"token {self.access_token}"

        async with aiohttp.ClientSession() as session:
            try:
                # Search repositories
                params = {
                    "q": f"{query} topic:avalanche",
                    "sort": "updated",
                    "per_page": 20
                }

                async with session.get(
                    f"{self.API_BASE}/search/repositories",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        for item in data.get("items", []):
                            repo_data = self._parse_repository(item)
                            # Simple relevance based on stars
                            repo_data["relevance"] = min(1.0, repo_data["stars"] / 1000)
                            results.append(repo_data)

                await asyncio.sleep(1)

            except Exception as e:
                print(f"Error searching GitHub: {e}")

        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)

        return results

    def _parse_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse GitHub event into standardized format.

        Args:
            event: GitHub API event object

        Returns:
            Standardized event object
        """
        event_type = event.get("type", "unknown")
        payload = event.get("payload", {})
        repo = event.get("repo", {})

        # Extract relevant information based on event type
        content = self._extract_event_content(event_type, payload)

        return {
            "id": event.get("id"),
            "source": "github",
            "content": content,
            "timestamp": event["created_at"],
            "type": event_type,
            "author": {
                "id": str(event["actor"]["id"]) if event.get("actor") else None,
                "username": event["actor"]["login"] if event.get("actor") else None,
                "type": event["actor"]["type"] if event.get("actor") else None,
            },
            "repository": {
                "id": str(repo["id"]) if repo else None,
                "name": repo["name"] if repo else None,
                "url": f"https://github.com/{repo['name']}" if repo else None,
            },
            "engagement": self._extract_engagement(event_type, payload),
            "entities": self._extract_entities(event_type, payload),
            "url": event.get("html_url"),
            "collected_at": datetime.now().isoformat(),
        }

    def _parse_repository(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """Parse repository object.

        Args:
            repo: GitHub API repository object

        Returns:
            Standardized repository object
        """
        return {
            "id": str(repo["id"]),
            "source": "github",
            "content": repo.get("description", ""),
            "timestamp": repo["updated_at"],
            "type": "repository",
            "author": {
                "id": str(repo["owner"]["id"]),
                "username": repo["owner"]["login"],
                "type": repo["owner"]["type"],
            },
            "repository": {
                "id": str(repo["id"]),
                "name": repo["full_name"],
                "url": repo["html_url"],
            },
            "engagement": {
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "watchers": repo.get("watchers_count", 0),
                "open_issues": repo.get("open_issues_count", 0),
            },
            "entities": repo.get("topics", []),
            "url": repo["html_url"],
            "stars": repo.get("stargazers_count", 0),  # For relevance calculation
            "collected_at": datetime.now().isoformat(),
        }

    def _extract_event_content(self, event_type: str, payload: Dict[str, Any]) -> str:
        """Extract content from event based on type.

        Args:
            event_type: Event type
            payload: Event payload

        Returns:
            Event content string
        """
        if event_type == "PushEvent":
            commits = payload.get("commits", [])
            if commits:
                commit_messages = [c.get("message", "") for c in commits]
                return f"Pushed {len(commits)} commit(s): {' | '.join(commit_messages[:3])}"
            return "Pushed commits"

        elif event_type == "IssuesEvent":
            action = payload.get("action", "")
            issue = payload.get("issue", {})
            title = issue.get("title", "")
            return f"Issue {action}: {title}"

        elif event_type == "PullRequestEvent":
            action = payload.get("action", "")
            pr = payload.get("pull_request", {})
            title = pr.get("title", "")
            return f"PR {action}: {title}"

        elif event_type == "CreateEvent":
            ref_type = payload.get("ref_type", "")
            ref = payload.get("ref", "")
            return f"Created {ref_type}: {ref}"

        elif event_type == "DeleteEvent":
            ref_type = payload.get("ref_type", "")
            ref = payload.get("ref", "")
            return f"Deleted {ref_type}: {ref}"

        elif event_type == "ReleaseEvent":
            release = payload.get("release", {})
            tag_name = release.get("tag_name", "")
            return f"Released: {tag_name}"

        elif event_type == "WatchEvent":
            return "Starred repository"

        elif event_type == "ForkEvent":
            return "Forked repository"

        else:
            return event_type

    def _extract_engagement(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract engagement metrics from event.

        Args:
            event_type: Event type
            payload: Event payload

        Returns:
            Engagement metrics
        """
        engagement = {}

        if event_type == "PullRequestEvent":
            pr = payload.get("pull_request", {})
            engagement["comments"] = pr.get("comments", 0)
            engagement["reviews"] = pr.get("review_comments", 0)

        elif event_type == "IssuesEvent":
            issue = payload.get("issue", {})
            engagement["comments"] = issue.get("comments", 0)
            engagement["reactions"] = len(issue.get("reactions", {}))

        elif event_type == "WatchEvent":
            # Star counts are tracked at repository level
            pass

        return engagement

    def _extract_entities(self, event_type: str, payload: Dict[str, Any]) -> List[str]:
        """Extract entities from event.

        Args:
            event_type: Event type
            payload: Event payload

        Returns:
            List of entity strings
        """
        entities = []

        # Extract repository name
        repo = payload.get("repository", {})
        if repo:
            entities.append(repo.get("name", ""))

        # Extract issue/PR references
        if event_type == "PullRequestEvent":
            pr = payload.get("pull_request", {})
            labels = [l.get("name", "") for l in pr.get("labels", [])]
            entities.extend(labels)

        elif event_type == "IssuesEvent":
            issue = payload.get("issue", {})
            labels = [l.get("name", "") for l in issue.get("labels", [])]
            entities.extend(labels)

        return entities
