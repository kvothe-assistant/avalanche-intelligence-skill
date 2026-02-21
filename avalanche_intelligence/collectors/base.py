"""Base collector interface for all data sources."""

import abc
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class BaseCollector(abc.ABC):
    """Abstract base class for all data collectors."""

    def __init__(self, name: str, config: Any = None):
        self.name = name
        self.config = config
        self._is_active = True

    @abc.abstractmethod
    async def collect(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Collect data from this source for the past N hours.

        Args:
            hours: Number of hours of historical data to collect

        Returns:
            List of collected data items with metadata
        """
        pass

    @abc.abstractmethod
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search collected data for a specific query.

        Args:
            query: Search query string

        Returns:
            List of matching data items
        """
        pass

    def is_active(self) -> bool:
        """Check if collector is active."""
        return self._is_active

    def activate(self) -> None:
        """Activate this collector."""
        self._is_active = True

    def deactivate(self) -> None:
        """Deactivate this collector."""
        self._is_active = False

    async def get_recent_posts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent posts from this collector.

        Args:
            hours: Number of hours of data to retrieve

        Returns:
            List of recent posts
        """
        return await self.collect(hours=hours)

    def _filter_by_time(
        self,
        items: List[Dict[str, Any]],
        hours: int,
        timestamp_field: str = "timestamp"
    ) -> List[Dict[str, Any]]:
        """Filter items by timestamp.

        Args:
            items: List of items to filter
            hours: Number of hours to include
            timestamp_field: Field name containing timestamp

        Returns:
            Filtered list of items
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        filtered = []
        for item in items:
            timestamp_str = item.get(timestamp_field)
            if timestamp_str:
                try:
                    # Parse various timestamp formats
                    if isinstance(timestamp_str, str):
                        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    else:
                        timestamp = timestamp_str

                    if timestamp > cutoff_time:
                        filtered.append(item)
                except (ValueError, TypeError):
                    # Skip items with invalid timestamps
                    continue

        return filtered
