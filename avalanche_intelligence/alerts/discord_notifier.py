"""Discord webhook notifier for alerts."""

import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime


class DiscordNotifier:
    """Send alerts to Discord via webhook."""

    def __init__(self, webhook_url: str, username: str = "Avalanche Intelligence", avatar_url: str = None):
        """Initialize Discord notifier.

        Args:
            webhook_url: Discord webhook URL
            username: Bot username
            avatar_url: Avatar image URL
        """
        self.webhook_url = webhook_url
        self.username = username
        self.avatar_url = avatar_url

    async def send_alert(self, alert: Dict[str, Any]) -> bool:
        """Send an alert to Discord.

        Args:
            alert: Alert object

        Returns:
            Success status
        """
        if not self.webhook_url:
            return False

        # Build webhook payload
        payload = self._build_webhook_payload(alert)

        # Send webhook
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.webhook_url, json=payload) as response:
                    return response.status == 204
            except Exception as e:
                print(f"Error sending Discord alert: {e}")
                return False

    def _build_webhook_payload(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Build Discord webhook payload.

        Args:
            alert: Alert object

        Returns:
            Webhook payload
        """
        # Determine color based on severity
        severity = alert.get("severity", "medium")
        color = self._get_severity_color(severity)

        # Build embed
        embed = {
            "title": self._format_title(alert),
            "description": self._format_description(alert),
            "color": color,
            "fields": self._build_fields(alert),
            "timestamp": alert.get("triggered_at"),
            "footer": {
                "text": f"Confidence: {alert.get('confidence', 0):.2f}"
            },
        }

        # Add URL if available
        url = alert.get("data", {}).get("url")
        if url:
            embed["url"] = url

        return {
            "username": self.username,
            "avatar_url": self.avatar_url,
            "embeds": [embed],
        }

    def _format_title(self, alert: Dict[str, Any]) -> str:
        """Format alert title.

        Args:
            alert: Alert object

        Returns:
            Formatted title
        """
        alert_type = alert.get("type", "alert")
        entity = alert.get("entity", "")

        # Format based on type
        type_titles = {
            "trend_spike": f"🚀 Trend Spike: {entity}",
            "price_change": f"💰 Price Change: {entity}",
            "acp_proposal": f"📋 ACP Proposal: {entity}",
            "new_subnet": f"🌐 New Subnet: {entity}",
            "institutional_partnership": f"🤝 Partnership: {entity}",
            "rwa_launch": f"🏦 RWA Launch: {entity}",
            "high_confidence": f"📊 High Confidence Signal: {entity}",
            "anomaly_detected": f"⚠️ Anomaly: {entity}",
        }

        return type_titles.get(alert_type, f"🔔 {alert_type.title()}: {entity}")

    def _format_description(self, alert: Dict[str, Any]) -> str:
        """Format alert description.

        Args:
            alert: Alert object

        Returns:
            Formatted description
        """
        data = alert.get("data", {})

        # Build description based on alert type
        alert_type = alert.get("type", "")

        if alert_type == "trend_spike":
            ratio = data.get("spike_ratio", 0)
            current = data.get("current_count", 0)
            prev = data.get("prev_count", 0)
            return f"**Spike Ratio:** {ratio:.1f}x\n**Current:** {current} mentions\n**Previous:** {prev} mentions"

        elif alert_type == "price_change":
            return f"Price change detected for {data.get('symbol', '')}"

        elif alert_type == "acp_proposal":
            return f"New ACP proposal detected"

        elif alert_type == "new_subnet":
            return f"New subnet launched: {data.get('name', '')}"

        elif alert_type == "high_confidence":
            sentiment = data.get("sentiment", "")
            text = data.get("text", "")
            return f"**Sentiment:** {sentiment}\n**Text:** {text[:200]}"

        elif alert_type == "anomaly_detected":
            metric = data.get("metric", "")
            z_score = data.get("z_score", 0)
            return f"**Metric:** {metric}\n**Z-Score:** {z_score:.2f}"

        else:
            # Generic description
            return str(data)

    def _build_fields(self, alert: Dict[str, Any]) -> list:
        """Build embed fields.

        Args:
            alert: Alert object

        Returns:
            List of field objects
        """
        fields = []
        data = alert.get("data", {})

        # Common fields
        fields.append({
            "name": "Entity",
            "value": alert.get("entity", ""),
            "inline": True,
        })

        fields.append({
            "name": "Type",
            "value": alert.get("type", "").replace("_", " ").title(),
            "inline": True,
        })

        fields.append({
            "name": "Severity",
            "value": alert.get("severity", "medium").upper(),
            "inline": True,
        })

        # Add data-specific fields
        for key, value in data.items():
            if key not in ["url", "text"]:
                fields.append({
                    "name": key.replace("_", " ").title(),
                    "value": str(value),
                    "inline": False,
                })

        return fields[:10]  # Limit to 10 fields

    def _get_severity_color(self, severity: str) -> int:
        """Get color for severity level.

        Args:
            severity: Severity string

        Returns:
            Discord color (decimal)
        """
        colors = {
            "low": 0x00ff00,      # Green
            "medium": 0xffff00,   # Yellow
            "high": 0xff9900,    # Orange
            "critical": 0xff0000, # Red
        }

        return colors.get(severity.lower(), 0xffff00)

    def send_simple_message(self, message: str) -> bool:
        """Send a simple text message.

        Args:
            message: Text message

        Returns:
            Success status
        """
        if not self.webhook_url:
            return False

        async def _send():
            async with aiohttp.ClientSession() as session:
                try:
                    payload = {"content": message}
                    async with session.post(self.webhook_url, json=payload) as response:
                        return response.status == 204
                except Exception as e:
                    print(f"Error sending Discord message: {e}")
                    return False

        return asyncio.run(_send())

    def send_embed(self, title: str, description: str, color: int = 0x00ff00, fields: list = None, url: str = None) -> bool:
        """Send a formatted embed.

        Args:
            title: Embed title
            description: Embed description
            color: Embed color
            fields: List of field objects
            url: Embed URL

        Returns:
            Success status
        """
        if not self.webhook_url:
            return False

        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.now().isoformat(),
        }

        if fields:
            embed["fields"] = fields

        if url:
            embed["url"] = url

        payload = {
            "username": self.username,
            "avatar_url": self.avatar_url,
            "embeds": [embed],
        }

        async def _send():
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(self.webhook_url, json=payload) as response:
                        return response.status == 204
                except Exception as e:
                    print(f"Error sending Discord embed: {e}")
                    return False

        return asyncio.run(_send())
