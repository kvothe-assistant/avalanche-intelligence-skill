"""Avalanche Intelligence - OpenClaw skill for Avalanche blockchain monitoring."""

__version__ = "0.1.0"
__author__ = "Kvothe"
__description__ = "Real-time Avalanche blockchain ecosystem monitoring and intelligence"

from .config import Config
from .engine import IntelligenceEngine

__all__ = [
    "Config",
    "IntelligenceEngine",
]
