"""Trend detection using statistical analysis."""

from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics


class TrendDetector:
    """Detect trends in time-series data."""

    def __init__(self, spike_threshold: float = 3.0, window_minutes: int = 60):
        """Initialize trend detector.

        Args:
            spike_threshold: Multiplier for spike detection (default: 3x)
            window_minutes: Time window for trend analysis (default: 60 min)
        """
        self.spike_threshold = spike_threshold
        self.window_minutes = window_minutes

    def detect_spikes(
        self,
        data_points: List[Dict[str, Any]],
        entity_field: str = "entities",
        timestamp_field: str = "timestamp"
    ) -> List[Dict[str, Any]]:
        """Detect spike trends (sudden increase in mentions).

        Args:
            data_points: List of data points with timestamps
            entity_field: Field name containing entities
            timestamp_field: Field name containing timestamps

        Returns:
            List of detected spikes
        """
        spikes = []

        # Group entities by time windows
        time_windows = self._group_by_time_windows(data_points, timestamp_field)

        # Count mentions per entity in each window
        for i, window in enumerate(time_windows):
            entity_counts = Counter()

            for point in window:
                entities = point.get(entity_field, [])
                for entity in entities:
                    entity_counts[entity] += 1

            # Compare with previous window
            if i > 0:
                prev_counts = self._get_entity_counts(time_windows[i-1], entity_field)
                spikes.extend(self._compare_counts(
                    entity_counts, prev_counts, window
                ))

        return spikes

    def _group_by_time_windows(
        self,
        data_points: List[Dict[str, Any]],
        timestamp_field: str
    ) -> List[List[Dict[str, Any]]]:
        """Group data points into time windows.

        Args:
            data_points: List of data points
            timestamp_field: Field name containing timestamps

        Returns:
            List of time windows
        """
        # Sort by timestamp
        sorted_points = sorted(
            data_points,
            key=lambda x: x.get(timestamp_field, "")
        )

        # Group into windows
        windows = []
        current_window = []
        window_start = None

        for point in sorted_points:
            timestamp_str = point.get(timestamp_field)
            if not timestamp_str:
                continue

            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

            if window_start is None:
                window_start = timestamp
                current_window.append(point)
            else:
                # Check if within current window
                if (timestamp - window_start).total_seconds() < (self.window_minutes * 60):
                    current_window.append(point)
                else:
                    # Start new window
                    windows.append(current_window)
                    current_window = [point]
                    window_start = timestamp

        # Add final window
        if current_window:
            windows.append(current_window)

        return windows

    def _get_entity_counts(
        self,
        window: List[Dict[str, Any]],
        entity_field: str
    ) -> Counter:
        """Get entity counts for a window.

        Args:
            window: List of data points
            entity_field: Field name containing entities

        Returns:
            Counter of entity counts
        """
        counts = Counter()

        for point in window:
            entities = point.get(entity_field, [])
            for entity in entities:
                counts[entity] += 1

        return counts

    def _compare_counts(
        self,
        current_counts: Counter,
        prev_counts: Counter,
        window: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Compare entity counts between windows.

        Args:
            current_counts: Current window entity counts
            prev_counts: Previous window entity counts
            window: Current window data

        Returns:
            List of detected spikes
        """
        spikes = []

        for entity, current_count in current_counts.items():
            prev_count = prev_counts.get(entity, 0)

            # Avoid division by zero
            if prev_count == 0:
                # New entity, consider as spike if count > 5
                if current_count > 5:
                    spike_ratio = float('inf')
                else:
                    continue
            else:
                spike_ratio = current_count / prev_count

            # Check if exceeds threshold
            if spike_ratio >= self.spike_threshold:
                spikes.append({
                    "entity": entity,
                    "type": "spike",
                    "current_count": current_count,
                    "prev_count": prev_count,
                    "spike_ratio": spike_ratio,
                    "trend": self._classify_trend(spike_ratio),
                    "window_start": self._get_window_time(window[0]),
                    "window_end": self._get_window_time(window[-1]),
                })

        return spikes

    def _classify_trend(self, spike_ratio: float) -> str:
        """Classify trend based on spike ratio.

        Args:
            spike_ratio: Ratio of current to previous count

        Returns:
            Trend classification
        """
        if spike_ratio >= 10:
            return "viral"
        elif spike_ratio >= 5:
            return "explosive"
        elif spike_ratio >= self.spike_threshold:
            return "emerging"
        else:
            return "normal"

    def _get_window_time(self, data_point: Dict[str, Any]) -> str:
        """Get timestamp from data point.

        Args:
            data_point: Data point

        Returns:
            Timestamp string
        """
        return data_point.get("timestamp", "")

    def detect_momentum(
        self,
        data_points: List[Dict[str, Any]],
        entity_field: str = "entities",
        num_windows: int = 6
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Detect momentum trends (sustained increase/decrease).

        Args:
            data_points: List of data points
            entity_field: Field name containing entities
            num_windows: Number of windows to analyze

        Returns:
            Dictionary of momentum trends by direction
        """
        momentum = {
            "upward": [],
            "downward": [],
            "stable": [],
        }

        # Group into windows
        time_windows = self._group_by_time_windows(data_points, "timestamp")

        # Use last N windows
        recent_windows = time_windows[-num_windows:]

        if len(recent_windows) < 3:
            return momentum

        # Count entities per window
        window_counts = []
        for window in recent_windows:
            counts = self._get_entity_counts(window, entity_field)
            window_counts.append(counts)

        # Analyze trends per entity
        all_entities = set()
        for counts in window_counts:
            all_entities.update(counts.keys())

        for entity in all_entities:
            counts_over_time = [counts.get(entity, 0) for counts in window_counts]

            # Calculate trend line (linear regression)
            if len(counts_over_time) >= 3:
                slope = self._calculate_slope(counts_over_time)

                if slope > 0.5:
                    # Upward momentum
                    momentum["upward"].append({
                        "entity": entity,
                        "slope": slope,
                        "start_count": counts_over_time[0],
                        "end_count": counts_over_time[-1],
                        "change_pct": self._calculate_change_pct(counts_over_time),
                    })
                elif slope < -0.5:
                    # Downward momentum
                    momentum["downward"].append({
                        "entity": entity,
                        "slope": slope,
                        "start_count": counts_over_time[0],
                        "end_count": counts_over_time[-1],
                        "change_pct": self._calculate_change_pct(counts_over_time),
                    })
                else:
                    # Stable
                    momentum["stable"].append({
                        "entity": entity,
                        "slope": slope,
                        "avg_count": statistics.mean(counts_over_time),
                    })

        return momentum

    def _calculate_slope(self, values: List[float]) -> float:
        """Calculate slope of trend line (simple linear regression).

        Args:
            values: List of values

        Returns:
            Slope of trend line
        """
        n = len(values)
        if n < 2:
            return 0.0

        x = list(range(n))
        y = values

        # Calculate slope
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return slope

    def _calculate_change_pct(self, values: List[float]) -> float:
        """Calculate percentage change from start to end.

        Args:
            values: List of values

        Returns:
            Percentage change
        """
        if len(values) < 2:
            return 0.0

        start = values[0]
        end = values[-1]

        if start == 0:
            return 0.0

        change_pct = ((end - start) / start) * 100
        return change_pct

    def detect_anomalies(
        self,
        data_points: List[Dict[str, Any]],
        metric_field: str,
        z_threshold: float = 3.0
    ) -> List[Dict[str, Any]]:
        """Detect anomalies using Z-score method.

        Args:
            data_points: List of data points
            metric_field: Field name containing metric value
            z_threshold: Z-score threshold (default: 3.0)

        Returns:
            List of detected anomalies
        """
        anomalies = []

        # Extract metric values
        values = []
        for point in data_points:
            metric = point.get(metric_field)
            if metric is not None:
                values.append(float(metric))

        if len(values) < 10:
            return anomalies

        # Calculate statistics
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)

        if stdev == 0:
            return anomalies

        # Detect anomalies (Z-score > threshold)
        for i, point in enumerate(data_points):
            metric = point.get(metric_field)
            if metric is not None:
                z_score = (float(metric) - mean) / stdev

                if abs(z_score) > z_threshold:
                    anomalies.append({
                        "entity": point.get("content", "")[:50],
                        "metric": metric,
                        "z_score": z_score,
                        "mean": mean,
                        "stdev": stdev,
                        "timestamp": point.get("timestamp"),
                        "type": "anomaly",
                    })

        return anomalies

    def calculate_trend_score(
        self,
        data_points: List[Dict[str, Any]],
        entity: str,
        entity_field: str = "entities"
    ) -> Dict[str, Any]:
        """Calculate trend score for a specific entity.

        Args:
            data_points: List of data points
            entity: Entity to analyze
            entity_field: Field name containing entities

        Returns:
            Trend score and metadata
        """
        # Filter data points containing entity
        entity_points = [
            p for p in data_points
            if entity in p.get(entity_field, [])
        ]

        if len(entity_points) < 3:
            return {
                "entity": entity,
                "score": 0.0,
                "trend": "insufficient_data",
                "sample_size": len(entity_points),
            }

        # Count mentions over time
        time_windows = self._group_by_time_windows(entity_points, "timestamp")
        counts = [len(w) for w in time_windows]

        # Calculate metrics
        avg_count = statistics.mean(counts)
        slope = self._calculate_slope(counts)
        change_pct = self._calculate_change_pct(counts)

        # Calculate trend score (0-100)
        trend_score = min(100, max(0, 50 + slope * 10 + change_pct / 2))

        # Classify trend
        if change_pct > 50:
            trend = "strong_upward"
        elif change_pct > 20:
            trend = "upward"
        elif change_pct < -50:
            trend = "strong_downward"
        elif change_pct < -20:
            trend = "downward"
        else:
            trend = "stable"

        return {
            "entity": entity,
            "score": trend_score,
            "trend": trend,
            "slope": slope,
            "avg_mentions_per_window": avg_count,
            "change_pct": change_pct,
            "sample_size": len(entity_points),
        }
