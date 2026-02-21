"""Alert manager for triggering and routing alerts."""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

from ..storage.document_store import DocumentStore


class AlertType(Enum):
    """Types of alerts."""
    TREND_SPIKE = "trend_spike"
    PRICE_CHANGE = "price_change"
    ACP_PROPOSAL = "acp_proposal"
    NEW_SUBNET = "new_subnet"
    INSTITUTIONAL_PARTNERSHIP = "institutional_partnership"
    RWA_LAUNCH = "rwa_launch"
    HIGH_CONFIDENCE = "high_confidence"
    ANOMALY_DETECTED = "anomaly_detected"


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertManager:
    """Manage alert triggering and routing."""

    def __init__(
        self,
        document_store: DocumentStore,
        enabled_channels: List[str] = None,
        min_confidence: float = 0.7
    ):
        """Initialize alert manager.

        Args:
            document_store: Document store for persisting alerts
            enabled_channels: List of enabled channels (discord, signal, etc.)
            min_confidence: Minimum confidence threshold
        """
        self.document_store = document_store
        self.enabled_channels = enabled_channels or []
        self.min_confidence = min_confidence
        self.notifiers = {}

    def add_notifier(self, channel: str, notifier) -> bool:
        """Add a notifier for a channel.

        Args:
            channel: Channel name (discord, signal, etc.)
            notifier: Notifier instance

        Returns:
            Success status
        """
        if channel not in self.enabled_channels:
            return False

        self.notifiers[channel] = notifier
        return True

    def trigger_alert(
        self,
        alert_type: AlertType,
        entity: str,
        confidence: float,
        data: Dict[str, Any],
        severity: AlertSeverity = AlertSeverity.MEDIUM
    ) -> bool:
        """Trigger an alert.

        Args:
            alert_type: Type of alert
            entity: Entity that triggered the alert
            confidence: Confidence score (0-1)
            data: Additional alert data
            severity: Alert severity

        Returns:
            Success status
        """
        # Check confidence threshold
        if confidence < self.min_confidence:
            return False

        # Create alert object
        alert = {
            "id": f"alert_{datetime.now().timestamp()}_{entity.replace(' ', '_')}",
            "type": alert_type.value,
            "entity": entity,
            "confidence": confidence,
            "data": data,
            "severity": severity.value,
            "triggered_at": datetime.now().isoformat(),
        }

        # Store alert
        stored = self.document_store.add_signal(alert)

        if not stored:
            return False

        # Route to notifiers
        self._route_alert(alert)

        return True

    def _route_alert(self, alert: Dict[str, Any]):
        """Route alert to enabled channels.

        Args:
            alert: Alert object
        """
        for channel, notifier in self.notifiers.items():
            if channel in self.enabled_channels:
                try:
                    # Run notifier in background
                    asyncio.create_task(notifier.send_alert(alert))
                except Exception as e:
                    print(f"Error routing alert to {channel}: {e}")

    def check_trend_alerts(
        self,
        trends: Dict[str, List[Dict[str, Any]]],
        threshold_multiplier: float = 3.0
    ) -> int:
        """Check for trend-based alerts.

        Args:
            trends: Trend detection results
            threshold_multiplier: Spike threshold multiplier

        Returns:
            Number of alerts triggered
        """
        alerts_triggered = 0

        # Check for spikes
        for spike in trends.get("spike", []):
            if spike.get("spike_ratio", 0) >= threshold_multiplier:
                # Trigger spike alert
                self.trigger_alert(
                    alert_type=AlertType.TREND_SPIKE,
                    entity=spike.get("entity"),
                    confidence=min(1.0, spike.get("spike_ratio", 0) / 10),
                    data={
                        "current_count": spike.get("current_count"),
                        "prev_count": spike.get("prev_count"),
                        "spike_ratio": spike.get("spike_ratio"),
                        "trend": spike.get("trend"),
                    },
                    severity=AlertSeverity.HIGH if spike.get("spike_ratio", 0) >= 10 else AlertSeverity.MEDIUM,
                )
                alerts_triggered += 1

        return alerts_triggered

    def check_sentiment_alerts(
        self,
        sentiment_results: List[Dict[str, Any]],
        threshold: float = 0.8
    ) -> int:
        """Check for sentiment-based alerts.

        Args:
            sentiment_results: List of sentiment analyses
            threshold: Sentiment threshold

        Returns:
            Number of alerts triggered
        """
        alerts_triggered = 0

        # Check for extreme sentiment
        for result in sentiment_results:
            confidence = result.get("confidence", 0)
            label = result.get("label", "")

            if confidence >= threshold:
                if label == "positive":
                    self.trigger_alert(
                        alert_type=AlertType.HIGH_CONFIDENCE,
                        entity=result.get("content", "")[:50],
                        confidence=confidence,
                        data={"sentiment": label, "text": result.get("content")},
                        severity=AlertSeverity.LOW,
                    )
                    alerts_triggered += 1
                elif label == "negative":
                    self.trigger_alert(
                        alert_type=AlertType.HIGH_CONFIDENCE,
                        entity=result.get("content", "")[:50],
                        confidence=confidence,
                        data={"sentiment": label, "text": result.get("content")},
                        severity=AlertSeverity.MEDIUM,
                    )
                    alerts_triggered += 1

        return alerts_triggered

    def check_anomaly_alerts(
        self,
        anomalies: List[Dict[str, Any]],
        threshold: float = 3.0
    ) -> int:
        """Check for anomaly-based alerts.

        Args:
            anomalies: List of detected anomalies
            threshold: Z-score threshold

        Returns:
            Number of alerts triggered
        """
        alerts_triggered = 0

        for anomaly in anomalies:
            z_score = abs(anomaly.get("z_score", 0))

            if z_score >= threshold:
                self.trigger_alert(
                    alert_type=AlertType.ANOMALY_DETECTED,
                    entity=anomaly.get("entity", ""),
                    confidence=min(1.0, z_score / 10),
                    data={
                        "metric": anomaly.get("metric"),
                        "z_score": z_score,
                        "mean": anomaly.get("mean"),
                        "stdev": anomaly.get("stdev"),
                    },
                    severity=AlertSeverity.HIGH if z_score >= 5 else AlertSeverity.MEDIUM,
                )
                alerts_triggered += 1

        return alerts_triggered

    def get_active_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get active (unacknowledged) alerts.

        Args:
            hours: Hours back from now

        Returns:
            List of active alerts
        """
        return self.document_store.get_signals(hours=hours, acknowledged=False)

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert.

        Args:
            alert_id: Alert ID

        Returns:
            Success status
        """
        return self.document_store.acknowledge_signal(alert_id)
