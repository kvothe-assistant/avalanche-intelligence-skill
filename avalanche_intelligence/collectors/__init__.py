"""Data collectors for Avalanche Intelligence."""

from .base import BaseCollector

# Try to import each collector, skip if dependencies not available
collectors_available = []

try:
    from .twitter_fxtwitter import TwitterCollector
    collectors_available.append("TwitterCollector")
except ImportError:
    print("Warning: Twitter collector not available")

try:
    from .reddit import RedditCollector
    collectors_available.append("RedditCollector")
except ImportError as e:
    print(f"Warning: Reddit collector not available - {e}")

try:
    from .discord import DiscordCollector
    collectors_available.append("DiscordCollector")
except ImportError:
    print("Warning: Discord collector not available")

try:
    from .github import GitHubCollector
    collectors_available.append("GitHubCollector")
except ImportError as e:
    print(f"Warning: GitHub collector not available - {e}")

try:
    from .rss import RSSCollector
    collectors_available.append("RSSCollector")
except ImportError as e:
    print(f"Warning: RSS collector not available - {e}")

try:
    from .onchain import OnchainCollector
    collectors_available.append("OnchainCollector")
except ImportError as e:
    print(f"Warning: On-chain collector not available - {e}")

# Build __all__ dynamically based on what's available
__all__ = ["BaseCollector"] + collectors_available
