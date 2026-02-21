"""Configuration management for Avalanche Intelligence."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class TwitterConfig:
    """Twitter API configuration."""
    enabled: bool = False
    bearer_token: str = ""
    track_keywords: List[str] = field(default_factory=list)
    follow_accounts: List[str] = field(default_factory=list)
    rate_limit_per_hour: int = 300


@dataclass
class RedditConfig:
    """Reddit API configuration."""
    enabled: bool = False
    client_id: str = ""
    client_secret: str = ""
    user_agent: str = "avalanche-intelligence/0.1.0"
    subreddits: List[str] = field(default_factory=list)
    rate_limit_per_hour: int = 100


@dataclass
class DiscordConfig:
    """Discord configuration."""
    enabled: bool = False
    bot_token: str = ""
    webhook_url: str = ""
    guilds: List[str] = field(default_factory=list)
    channels: List[str] = field(default_factory=list)


@dataclass
class RSSConfig:
    """RSS feed configuration."""
    enabled: bool = True
    feeds: List[str] = field(default_factory=list)
    rate_limit_per_hour: int = 20


@dataclass
class StorageConfig:
    """Storage configuration."""
    retention_days: int = 90
    vector_db_path: str = "data/vector_db"
    document_store_path: str = "data/documents"
    # Optional: time_series_db_path: str = "data/time_series"


@dataclass
class AnalysisConfig:
    """Analysis configuration."""
    sentiment_model: str = "vader"  # Options: vader, finbert, llm
    entity_extraction: bool = True
    trend_detection: bool = True
    deduplication_threshold: float = 0.85


@dataclass
class AlertsConfig:
    """Alert configuration."""
    enabled_channels: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    min_confidence: float = 0.7


@dataclass
class Config:
    """Main configuration class."""

    # Sources
    twitter: TwitterConfig = field(default_factory=TwitterConfig)
    reddit: RedditConfig = field(default_factory=RedditConfig)
    discord: DiscordConfig = field(default_factory=DiscordConfig)
    rss: RSSConfig = field(default_factory=RSSConfig)

    # Systems
    storage: StorageConfig = field(default_factory=StorageConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    alerts: AlertsConfig = field(default_factory=AlertsConfig)

    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """Load configuration from YAML file."""
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create Config from dictionary."""
        config = cls()

        # Load source configs
        if "sources" in data:
            sources = data["sources"]
            config.twitter = TwitterConfig(**sources.get("twitter", {}))
            config.reddit = RedditConfig(**sources.get("reddit", {}))
            config.discord = DiscordConfig(**sources.get("discord", {}))
            config.rss = RSSConfig(**sources.get("news", sources.get("rss", {})))

        # Load system configs
        if "storage" in data:
            config.storage = StorageConfig(**data["storage"])
        if "analysis" in data:
            config.analysis = AnalysisConfig(**data["analysis"])
        if "alerts" in data:
            config.alerts = AlertsConfig(**data["alerts"])

        # Expand environment variables
        config._expand_env_vars()

        return config

    def _expand_env_vars(self) -> None:
        """Expand environment variables in config values."""
        # Twitter
        if self.twitter.bearer_token.startswith("${"):
            env_var = self.twitter.bearer_token[2:-1]
            self.twitter.bearer_token = os.environ.get(env_var, "")

        # Reddit
        if self.reddit.client_id.startswith("${"):
            env_var = self.reddit.client_id[2:-1]
            self.reddit.client_id = os.environ.get(env_var, "")
        if self.reddit.client_secret.startswith("${"):
            env_var = self.reddit.client_secret[2:-1]
            self.reddit.client_secret = os.environ.get(env_var, "")

        # Discord
        if self.discord.bot_token.startswith("${"):
            env_var = self.discord.bot_token[2:-1]
            self.discord.bot_token = os.environ.get(env_var, "")
        if self.discord.webhook_url.startswith("${"):
            env_var = self.discord.webhook_url[2:-1]
            self.discord.webhook_url = os.environ.get(env_var, "")


class ConfigManager:
    """Configuration manager with default paths."""

    DEFAULT_CONFIG_PATHS = [
        "config/config.yaml",
        "~/.avalanche-intelligence/config.yaml",
        "/etc/avalanche-intelligence/config.yaml",
    ]

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> Config:
        """Load configuration from first available path."""
        paths_to_try = [config_path] + cls.DEFAULT_CONFIG_PATHS if config_path else cls.DEFAULT_CONFIG_PATHS

        for path in paths_to_try:
            if path and os.path.exists(path):
                expanded_path = os.path.expanduser(path)
                print(f"Loading config from: {expanded_path}")
                return Config.from_file(expanded_path)

        # No config found, return default
        print("No config file found, using defaults")
        return Config()

    @classmethod
    def create_default(cls) -> str:
        """Create default configuration file."""
        example_path = "config/config.example.yaml"
        config_path = "config/config.yaml"

        if os.path.exists(example_path):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            import shutil
            shutil.copy(example_path, config_path)
            print(f"Created config file: {config_path}")
            return config_path
        else:
            raise FileNotFoundError(f"Example config not found: {example_path}")
