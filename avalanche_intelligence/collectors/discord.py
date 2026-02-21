"""Discord data collector using Discord.py."""

import asyncio
import discord
from discord.ext import commands
from typing import List, Dict, Any
from datetime import datetime, timedelta

from .base import BaseCollector


class DiscordCollector(BaseCollector):
    """Collector for Discord data using Discord.py."""

    def __init__(self, config):
        super().__init__("discord", config)
        self.bot_token = config.bot_token
        self.webhook_url = config.webhook_url
        self.guilds = config.guilds
        self.channels = config.channels
        self._client = None
        self._messages = []

    def _get_client(self):
        """Get Discord client (lazy initialization)."""
        if self._client is None and self.bot_token:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.guild_messages = True

            self._client = discord.Client(intents=intents)
            self._setup_event_handlers()

        return self._client

    def _setup_event_handlers(self):
        """Setup Discord event handlers."""
        @self._client.event
        async def on_ready():
            print(f"Discord bot connected: {self._client.user}")

        @self._client.event
        async def on_message(message):
            # Ignore own messages
            if message.author == self._client.user:
                return

            # Only collect from configured channels
            if str(message.channel.id) not in self.channels:
                return

            # Parse message
            msg_data = self._parse_message(message)
            self._messages.append(msg_data)

    async def collect(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Collect messages from configured channels.

        Args:
            hours: Number of hours of historical data to collect

        Returns:
            List of message objects with metadata
        """
        if not self.bot_token:
            print("Warning: Discord bot token not configured")
            return []

        client = self._get_client()
        if not client:
            return []

        # Start client
        await client.start(self.bot_token)

        # Wait for messages to accumulate
        await asyncio.sleep(10)  # Collect for 10 seconds

        # Stop client
        await client.close()

        # Filter by time
        filtered = self._filter_by_time(self._messages, hours)

        # Clear buffer
        self._messages = []

        return filtered

    async def listen(self, duration_seconds: int = 3600):
        """Listen to Discord messages for specified duration.

        Args:
            duration_seconds: How long to listen (default: 1 hour)
        """
        if not self.bot_token:
            print("Warning: Discord bot token not configured")
            return

        client = self._get_client()
        if not client:
            return

        print(f"Listening to Discord for {duration_seconds} seconds...")

        # Start client
        await client.start(self.bot_token)

        # Wait for duration
        await asyncio.sleep(duration_seconds)

        # Stop client
        await client.close()

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search collected messages.

        Args:
            query: Search query

        Returns:
            List of matching messages
        """
        query_lower = query.lower()
        matches = []

        for message in self._messages:
            content_lower = message.get("content", "").lower()
            if query_lower in content_lower:
                # Calculate relevance
                relevance = min(1.0, content_lower.count(query_lower) * 0.1)
                message["relevance"] = relevance
                matches.append(message)

        # Sort by relevance
        matches.sort(key=lambda x: x["relevance"], reverse=True)

        return matches

    def _parse_message(self, message: discord.Message) -> Dict[str, Any]:
        """Parse Discord message into standardized format.

        Args:
            message: Discord.py Message object

        Returns:
            Standardized message object
        """
        # Parse content
        content = message.content

        # Extract entities (mentions, emojis, links)
        entities = []

        # Mentions
        for mention in message.mentions:
            entities.append(f"@{mention.display_name}")

        # Links
        for embed in message.embeds:
            if embed.url:
                entities.append(embed.url)

        # Custom emojis
        for emoji in message.custom_emojis:
            entities.append(f":{emoji.name}:")

        return {
            "id": str(message.id),
            "source": "discord",
            "content": content,
            "timestamp": message.created_at.isoformat(),
            "author": {
                "id": str(message.author.id),
                "username": message.author.display_name,
                "discriminator": message.author.discriminator,
                "bot": message.author.bot,
                "roles": [role.name for role in message.author.roles],
            },
            "channel": {
                "id": str(message.channel.id),
                "name": message.channel.name,
                "guild": message.guild.name if message.guild else None,
            },
            "engagement": {
                "reactions": len(message.reactions),
                "mentions": len(message.mentions),
            },
            "entities": entities,
            "url": f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}" if message.guild else None,
            "collected_at": datetime.now().isoformat(),
        }

    async def send_webhook(self, message: str, embed: Dict[str, Any] = None):
        """Send message via webhook.

        Args:
            message: Message content
            embed: Discord embed data
        """
        if not self.webhook_url:
            print("Warning: Discord webhook URL not configured")
            return

        import aiohttp

        payload = {"content": message}

        if embed:
            payload["embeds"] = [embed]

        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_url, json=payload) as response:
                if response.status != 204:
                    print(f"Error sending webhook: {response.status}")
