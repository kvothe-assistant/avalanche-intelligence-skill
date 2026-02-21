"""Main intelligence engine that coordinates all components."""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

from .config import Config
from .collectors.twitter import TwitterCollector
from .collectors.reddit import RedditCollector
from .collectors.discord import DiscordCollector
from .collectors.github import GitHubCollector
from .collectors.rss import RSSCollector
from .collectors.onchain import OnchainCollector
from .analyzers.sentiment import SentimentAnalyzer
from .analyzers.entities import EntityExtractor
from .analyzers.trends import TrendDetector
from .analyzers.deduplication import Deduplicator
from .storage.vector_db import VectorDatabase
from .storage.time_series import TimeSeriesDatabase
from .storage.document_store import DocumentStore
from .alerts.alert_manager import AlertManager, AlertType, AlertSeverity
from .alerts.discord_notifier import DiscordNotifier


class IntelligenceEngine:
    """Central intelligence processing engine."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.collectors = {}
        self.analyzers = {}
        self.storage = {}
        self.alerts = None

        # Initialize components
        self._init_collectors()
        self._init_analyzers()
        self._init_storage()
        self._init_alert_manager()

        # Ensure data directories exist
        self._init_directories()

    def _init_collectors(self):
        """Initialize data collectors based on config."""
        # Twitter
        if self.config.twitter.enabled and self.config.twitter.bearer_token:
            self.collectors["twitter"] = TwitterCollector(self.config.twitter)

        # Reddit
        if self.config.reddit.enabled and self.config.reddit.client_id:
            self.collectors["reddit"] = RedditCollector(self.config.reddit)

        # Discord
        if self.config.discord.enabled and self.config.discord.bot_token:
            self.collectors["discord"] = DiscordCollector(self.config.discord)

        # GitHub
        if self.config.github.enabled and self.config.github.access_token:
            self.collectors["github"] = GitHubCollector(self.config.github)

        # RSS
        if self.config.rss.enabled and self.config.rss.feeds:
            self.collectors["rss"] = RSSCollector(self.config.rss)

        # On-chain
        if self.config.onchain.enabled and self.config.onchain.rpc_url:
            self.collectors["onchain"] = OnchainCollector(self.config.onchain)

    def _init_analyzers(self):
        """Initialize analysis components."""
        # Sentiment analyzer
        self.analyzers["sentiment"] = SentimentAnalyzer(
            model=self.config.analysis.sentiment_model
        )

        # Entity extractor
        self.analyzers["entities"] = EntityExtractor()

        # Trend detector
        self.analyzers["trends"] = TrendDetector(
            spike_threshold=3.0,
            window_minutes=60
        )

        # Deduplicator
        self.analyzers["deduplication"] = Deduplicator(
            threshold=self.config.analysis.deduplication_threshold,
            method="vector"
        )

    def _init_storage(self):
        """Initialize storage backends."""
        # Vector database
        self.storage["vector_db"] = VectorDatabase(
            db_path=self.config.storage.vector_db_path
        )

        # Time-series database
        # Note: Only initialize if token is configured
        self.storage["time_series"] = TimeSeriesDatabase()

        # Document store
        self.storage["document_store"] = DocumentStore(
            db_path=os.path.join(
                self.config.storage.document_store_path,
                "intelligence.db"
            )
        )

    def _init_alert_manager(self):
        """Initialize alert manager."""
        self.alerts = AlertManager(
            document_store=self.storage.get("document_store"),
            enabled_channels=self.config.alerts.enabled_channels,
            min_confidence=self.config.alerts.min_confidence
        )

        # Add Discord notifier if configured
        if "discord" in self.config.alerts.enabled_channels and self.config.discord.webhook_url:
            notifier = DiscordNotifier(
                webhook_url=self.config.discord.webhook_url
            )
            self.alerts.add_notifier("discord", notifier)

    def _init_directories(self):
        """Create necessary data directories."""
        dirs = [
            self.config.storage.vector_db_path,
            self.config.storage.document_store_path,
            "data/raw",
            "data/processed",
            "data/reports",
        ]

        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    async def scan(self, hours: int = 24, sources: List[str] = None) -> List[Dict[str, Any]]:
        """Scan all configured sources for recent data.

        Args:
            hours: Number of hours of historical data to collect
            sources: List of sources to scan (None = all)

        Returns:
            List of scan results per source
        """
        if sources is None:
            sources = list(self.collectors.keys())

        results = []
        all_data = []

        for source_name in sources:
            if source_name in self.collectors:
                collector = self.collectors[source_name]

                print(f"Collecting from {source_name}...")
                start_time = datetime.now()

                data = await collector.collect(hours=hours)
                all_data.extend(data)

                duration = (datetime.now() - start_time).total_seconds()

                results.append({
                    "source": source_name,
                    "posts_collected": len(data),
                    "signals_found": 0,  # TODO: Implement signal detection
                    "duration": duration,
                })

                print(f"  ✓ {len(data)} items collected in {duration:.1f}s")

        # Save raw data
        if all_data:
            self._save_raw_data(all_data)

        return results

    async def search(self, query: str, source: str = "all", deep: bool = False) -> List[Dict[str, Any]]:
        """Search across collected data.

        Args:
            query: Search query
            source: Filter by source ('all' = all sources)
            deep: Include additional context

        Returns:
            List of matching items with relevance scores
        """
        results = []

        sources_to_search = [source] if source != "all" else list(self.collectors.keys())

        for source_name in sources_to_search:
            if source_name in self.collectors:
                collector = self.collectors[source_name]
                matches = await collector.search(query)

                # Add relevance score (simple keyword match for now)
                for match in matches:
                    content_lower = match.get("content", "").lower()
                    query_lower = query.lower()

                    # Simple relevance: count keyword matches
                    relevance = min(1.0, content_lower.count(query_lower) * 0.1)

                    match["relevance"] = relevance
                    results.append(match)

        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)

        return results

    async def generate_report(self, timeframe: str = "24h", format: str = "markdown") -> Dict[str, Any]:
        """Generate intelligence report.

        Args:
            timeframe: Time period to report on
            format: Output format (markdown, json, html)

        Returns:
            Report data
        """
        # For now, return a simple report structure
        report = {
            "generated_at": datetime.now().isoformat(),
            "timeframe": timeframe,
            "format": format,
            "summary": {
                "total_sources": len(self.collectors),
                "total_items": 0,
                "total_signals": 0,
            },
            "sections": [
                {
                    "title": "System Status",
                    "content": f"Active collectors: {', '.join(self.collectors.keys())}"
                },
                {
                    "title": "Configuration",
                    "content": f"Analysis model: {self.config.analysis.sentiment_model}"
                }
            ]
        }

        return report

    async def get_status(self) -> Dict[str, Any]:
        """Get current system status.
        Returns:
            System status information"""
        status = {
            "sources_count": len(self.collectors),
            "collectors": {name: collector.is_active() for name, collector in self.collectors.items()},
            "analyzers": list(self.analyzers.keys()),
            "storage": {}
        }

        # Query document store stats
        if "document_store" in self.storage:
            try:
                doc_stats = self.storage["document_store"].get_stats()
                status["storage"]["document_store"] = doc_stats
                status["total_posts"] = doc_stats.get("document_count", 0)
                status["total_signals"] = doc_stats.get("active_signal_count", 0)
            except Exception as e:
                status["storage"]["document_store"] = {"error": str(e)}

        # Query vector database stats
        if "vector_db" in self.storage:
            try:
                vector_stats = self.storage["vector_db"].get_stats()
                status["storage"]["vector_db"] = vector_stats
                status["vector_db_status"] = "initialized" if vector_stats.get("available") else "not_initialized"
            except Exception as e:
                status["storage"]["vector_db"] = {"error": str(e)}
                status["vector_db_status"] = "error"

        # Query time-series stats
        if "time_series" in self.storage:
            try:
                ts_stats = self.storage["time_series"].get_stats()
                status["storage"]["time_series"] = ts_stats
            except Exception as e:
                status["storage"]["time_series"] = {"error": str(e)}

        return status

    async def watch_daemon(self, interval: int = 900):
        """Run continuous watch loop with alerts.

        Args:
            interval: Check interval in seconds
        """
        print(f"Starting watch daemon with {interval}s interval...")
        print("Press Ctrl+C to stop")

        try:
            while True:
                # Collect recent data
                await self.scan(hours=1)

                # TODO: Check for alerts
                # alerts = await self.check_alerts()
                # for alert in alerts:
                #     await self.send_alert(alert)

                print(f"Scan complete. Next scan in {interval}s...")
                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            print("\nWatch daemon stopped")

    def _save_raw_data(self, data: List[Dict[str, Any]]):
        """Save raw collected data to disk.

        Args:
            data: Data to save
        """
        import json
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"data/raw/scan_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"  → Data saved to {filename}")
