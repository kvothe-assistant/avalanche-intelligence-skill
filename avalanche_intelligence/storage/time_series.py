"""Time-series database for metrics using InfluxDB."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import os

try:
    from influxdb_client import InfluxDBClient, Point
    INFLUXDB_AVAILABLE = True
except ImportError:
    INFLUXDB_AVAILABLE = False


class TimeSeriesDatabase:
    """Time-series database for metrics storage."""

    def __init__(
        self,
        url: str = "http://localhost:8086",
        token: str = "",
        org: str = "avalanche-intelligence",
        bucket: str = "intelligence"
    ):
        """Initialize time-series database.

        Args:
            url: InfluxDB URL
            token: Authentication token
            org: Organization name
            bucket: Bucket name
        """
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.client = None

        if INFLUXDB_AVAILABLE:
            self._init_db()

    def _init_db(self):
        """Initialize InfluxDB client."""
        if self.token:
            self.client = InfluxDBClient(
                url=self.url,
                token=self.token,
                org=self.org
            )
        else:
            # Unauthenticated client
            self.client = InfluxDBClient(url=self.url, org=self.org)

    def write_point(self, measurement: str, fields: Dict[str, Any], tags: Dict[str, str] = None, timestamp: datetime = None) -> bool:
        """Write a single data point.

        Args:
            measurement: Measurement name
            fields: Field values (required)
            tags: Tag values (optional)
            timestamp: Timestamp (optional, uses current time if None)

        Returns:
            Success status
        """
        if not INFLUXDB_AVAILABLE or not self.client:
            return False

        try:
            point = Point(measurement)

            # Add fields
            for key, value in fields.items():
                point.field(key, value)

            # Add tags
            if tags:
                for key, value in tags.items():
                    point.tag(key, value)

            # Add timestamp
            if timestamp:
                point.time(timestamp)

            # Write point
            write_api = self.client.write_api()
            write_api.write(bucket=self.bucket, record=point)

            return True
        except Exception as e:
            print(f"Error writing point to InfluxDB: {e}")
            return False

    def write_points(
        self,
        points: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> int:
        """Write multiple data points.

        Args:
            points: List of points
            batch_size: Batch size for writing

        Returns:
            Number of points written
        """
        if not INFLUXDB_AVAILABLE or not self.client:
            return 0

        written = 0
        write_api = self.client.write_api()

        # Create Point objects
        point_objects = []
        for point_data in points:
            measurement = point_data.get("measurement", "")
            fields = point_data.get("fields", {})
            tags = point_data.get("tags", {})
            timestamp = point_data.get("timestamp")

            point = Point(measurement)

            for key, value in fields.items():
                point.field(key, value)

            if tags:
                for key, value in tags.items():
                    point.tag(key, value)

            if timestamp:
                point.time(timestamp)

            point_objects.append(point)

        # Write in batches
        for i in range(0, len(point_objects), batch_size):
            batch = point_objects[i:i + batch_size]

            try:
                write_api.write(bucket=self.bucket, record=batch)
                written += len(batch)
            except Exception as e:
                print(f"Error writing batch to InfluxDB: {e}")

        return written

    def query(
        self,
        query: str,
        time_range: str = "-24h"
    ) -> List[Dict[str, Any]]:
        """Query time-series data.

        Args:
            query: Flux query string
            time_range: Time range (e.g., "-24h", "-7d", "-30d")

        Returns:
            List of query results
        """
        if not INFLUXDB_AVAILABLE or not self.client:
            return []

        results = []

        try:
            query_api = self.client.query_api()

            # Add time range to query
            full_query = f'''
            {query}
            |> range(start: {time_range})
            '''

            # Execute query
            tables = query_api.query(org=self.org, query=full_query)

            # Parse results
            for table in tables:
                for record in table.records:
                    results.append({
                        "time": record.get_time(),
                        "measurement": record.get_measurement(),
                        "field": record.get_field(),
                        "value": record.get_value(),
                        "tags": record.values,
                    })

        except Exception as e:
            print(f"Error querying InfluxDB: {e}")

        return results

    def query_metrics(
        self,
        measurement: str,
        field: str,
        time_range: str = "-24h",
        aggregation: str = "mean"
    ) -> Dict[str, Any]:
        """Query aggregated metrics.

        Args:
            measurement: Measurement name
            field: Field name
            time_range: Time range
            aggregation: Aggregation function (mean, sum, count, min, max)

        Returns:
            Dictionary of aggregated metrics
        """
        query = f'''
        from(bucket: "{self.bucket}")
          |> rangeFilter(fn: (r) => r["_measurement"] == "{measurement}")
          |> filter(fn: (r) => r["_field"] == "{field}")
          |> aggregateWindow(every: 1h, fn: {aggregation}, createEmpty: false)
        '''

        results = self.query(query, time_range)

        if not results:
            return {
                "measurement": measurement,
                "field": field,
                "values": [],
                "aggregation": aggregation,
                "count": 0,
            }

        values = [r["value"] for r in results if r["value"] is not None]

        return {
            "measurement": measurement,
            "field": field,
            "values": values,
            "aggregation": aggregation,
            "count": len(values),
            "min": min(values) if values else None,
            "max": max(values) if values else None,
            "mean": sum(values) / len(values) if values else None,
        }

    def delete_old_data(self, time_range: str = "-90d") -> int:
        """Delete old data beyond time range.

        Args:
            time_range: Delete data older than this (e.g., "-90d")

        Returns:
            Number of records deleted (estimated)
        """
        if not INFLUXDB_AVAILABLE or not self.client:
            return 0

        try:
            delete_api = self.client.delete_api()

            # Delete old data
            delete_api.delete(
                org=self.org,
                bucket=self.bucket,
                predicate='_time < now() - 90d'
            )

            return -1  # InfluxDB doesn't return count

        except Exception as e:
            print(f"Error deleting from InfluxDB: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.

        Returns:
            Statistics dictionary
        """
        stats = {
            "available": INFLUXDB_AVAILABLE,
            "url": self.url,
            "org": self.org,
            "bucket": self.bucket,
        }

        if not INFLUXDB_AVAILABLE:
            stats["error"] = "InfluxDB client not installed"

        return stats
