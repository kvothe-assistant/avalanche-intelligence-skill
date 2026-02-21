"""Analyzers for processing collected data."""

from .sentiment import SentimentAnalyzer
from .entities import EntityExtractor
from .trends import TrendDetector
from .deduplication import Deduplicator

__all__ = [
    "SentimentAnalyzer",
    "EntityExtractor",
    "TrendDetector",
    "Deduplicator",
]
