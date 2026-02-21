"""Sentiment analysis using multiple models."""

from typing import Dict, Any, List
from enum import Enum

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

try:
    from transformers import pipeline
    FINBERT_AVAILABLE = True
except ImportError:
    FINBERT_AVAILABLE = False


class SentimentModel(Enum):
    """Available sentiment models."""
    VADER = "vader"
    FINBERT = "finbert"
    LLM = "llm"


class SentimentAnalyzer:
    """Multi-model sentiment analyzer."""

    def __init__(self, model: str = "vader"):
        """Initialize sentiment analyzer.

        Args:
            model: Sentiment model to use (vader, finbert, llm)
        """
        self.model = model

        # Initialize VADER
        if model == "vader" and VADER_AVAILABLE:
            self.vader_analyzer = SentimentIntensityAnalyzer()

        # Initialize FinBERT
        if model == "finbert" and FINBERT_AVAILABLE:
            self.finbert_pipeline = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert"
            )

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text.

        Args:
            text: Input text

        Returns:
            Sentiment analysis with scores
        """
        if not text or not text.strip():
            return {
                "score": 0.0,
                "label": "neutral",
                "confidence": 0.0,
                "model": self.model,
            }

        if self.model == "vader":
            return self._analyze_vader(text)
        elif self.model == "finbert":
            return self._analyze_finbert(text)
        elif self.model == "llm":
            return self._analyze_llm(text)
        else:
            return self._analyze_vader(text)

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of sentiment analyses
        """
        return [self.analyze(text) for text in texts]

    def _analyze_vader(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using VADER.

        Args:
            text: Input text

        Returns:
            VADER sentiment scores
        """
        if not VADER_AVAILABLE:
            return {
                "score": 0.0,
                "label": "neutral",
                "confidence": 0.0,
                "model": "vader",
                "error": "VADER not installed"
            }

        scores = self.vader_analyzer.polarity_scores(text)

        # Determine label
        compound = scores["compound"]
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        # Calculate confidence based on absolute compound score
        confidence = min(1.0, abs(compound))

        return {
            "score": compound,
            "label": label,
            "confidence": confidence,
            "model": "vader",
            "details": {
                "positive": scores["pos"],
                "negative": scores["neg"],
                "neutral": scores["neu"],
            },
        }

    def _analyze_finbert(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using FinBERT.

        Args:
            text: Input text

        Returns:
            FinBERT sentiment scores
        """
        if not FINBERT_AVAILABLE:
            return {
                "score": 0.0,
                "label": "neutral",
                "confidence": 0.0,
                "model": "finbert",
                "error": "FinBERT not installed"
            }

        try:
            result = self.finbert_pipeline(text)[0]

            # Map FinBERT labels to scores
            label_map = {
                "positive": 1.0,
                "negative": -1.0,
                "neutral": 0.0,
            }

            label = result["label"].lower()
            score = label_map.get(label, 0.0)
            confidence = result["score"]

            return {
                "score": score * confidence,
                "label": label,
                "confidence": confidence,
                "model": "finbert",
                "details": {
                    "raw_label": result["label"],
                    "raw_score": result["score"],
                },
            }
        except Exception as e:
            return {
                "score": 0.0,
                "label": "neutral",
                "confidence": 0.0,
                "model": "finbert",
                "error": str(e),
            }

    def _analyze_llm(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using LLM (placeholder).

        Args:
            text: Input text

        Returns:
            LLM sentiment scores
        """
        # Placeholder for LLM integration
        # In production, this would call an LLM API
        return {
            "score": 0.0,
            "label": "neutral",
            "confidence": 0.0,
            "model": "llm",
            "error": "LLM integration not implemented yet",
        }

    def composite_analysis(self, texts: List[str], weights: Dict[str, float] = None) -> Dict[str, Any]:
        """Perform composite sentiment analysis using multiple models.

        Args:
            texts: List of texts to analyze
            weights: Model weights (e.g., {"vader": 0.3, "finbert": 0.4, "llm": 0.3})

        Returns:
            Composite sentiment score
        """
        if weights is None:
            weights = {
                "vader": 0.3,
                "finbert": 0.4,
                "llm": 0.3,
            }

        # Normalize weights
        total_weight = sum(weights.values())
        weights = {k: v / total_weight for k, v in weights.items()}

        # Analyze with each model
        results = {}
        for model in weights.keys():
            if model == "vader" and VADER_AVAILABLE:
                results[model] = [self._analyze_vader(text) for text in texts]
            elif model == "finbert" and FINBERT_AVAILABLE:
                results[model] = [self._analyze_finbert(text) for text in texts]
            elif model == "llm":
                results[model] = [self._analyze_llm(text) for text in texts]

        # Calculate weighted average
        composite_scores = []
        for i in range(len(texts)):
            score = 0.0
            for model, weight in weights.items():
                if model in results:
                    score += results[model][i]["score"] * weight
            composite_scores.append(score)

        # Calculate aggregate sentiment
        avg_score = sum(composite_scores) / len(composite_scores)

        # Determine label
        if avg_score >= 0.05:
            label = "positive"
        elif avg_score <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {
            "score": avg_score,
            "label": label,
            "confidence": min(1.0, abs(avg_score)),
            "model": "composite",
            "details": {
                "weights": weights,
                "model_results": results,
                "individual_scores": composite_scores,
            },
        }
