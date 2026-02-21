"""Deduplication using various methods."""

from typing import List, Dict, Any, Set, Tuple
import re
from difflib import SequenceMatcher

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class Deduplicator:
    """Deduplicate content using multiple methods."""

    def __init__(self, threshold: float = 0.85, method: str = "vector"):
        """Initialize deduplicator.

        Args:
            threshold: Similarity threshold (0-1)
            method: Deduplication method (exact, fuzzy, vector)
        """
        self.threshold = threshold
        self.method = method

        # Initialize vector model
        if method == "vector" and SENTENCE_TRANSFORMERS_AVAILABLE:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.model = None

    def deduplicate(
        self,
        items: List[Dict[str, Any]],
        content_field: str = "content",
        id_field: str = "id"
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Remove duplicate items.

        Args:
            items: List of items to deduplicate
            content_field: Field name containing content
            id_field: Field name containing item ID

        Returns:
            Tuple of (unique_items, duplicates)
        """
        if not items:
            return [], []

        # Extract content and IDs
        contents = [(item.get(id_field), item.get(content_field, "")) for item in items]

        # Run deduplication
        if self.method == "exact":
            unique_ids, duplicate_ids = self._deduplicate_exact(contents)
        elif self.method == "fuzzy":
            unique_ids, duplicate_ids = self._deduplicate_fuzzy(contents)
        elif self.method == "vector":
            unique_ids, duplicate_ids = self._deduplicate_vector(contents)
        else:
            # Default to exact
            unique_ids, duplicate_ids = self._deduplicate_exact(contents)

        # Filter items
        unique_items = [item for item in items if item.get(id_field) in unique_ids]
        duplicate_items = [item for item in items if item.get(id_field) in duplicate_ids]

        return unique_items, duplicate_items

    def _deduplicate_exact(self, contents: List[Tuple[str, str]]) -> Tuple[Set[str], Set[str]]:
        """Exact string matching deduplication.

        Args:
            contents: List of (id, content) tuples

        Returns:
            Tuple of (unique_ids, duplicate_ids)
        """
        unique_ids = set()
        duplicate_ids = set()
        seen = set()

        for item_id, content in contents:
            # Normalize content
            normalized = self._normalize_content(content)

            if normalized in seen:
                duplicate_ids.add(item_id)
            else:
                seen.add(normalized)
                unique_ids.add(item_id)

        return unique_ids, duplicate_ids

    def _deduplicate_fuzzy(self, contents: List[Tuple[str, str]]) -> Tuple[Set[str], Set[str]]:
        """Fuzzy string matching deduplication.

        Args:
            contents: List of (id, content) tuples

        Returns:
            Tuple of (unique_ids, duplicate_ids)
        """
        unique_ids = set()
        duplicate_ids = set()
        seen_contents = []

        for item_id, content in contents:
            # Normalize content
            normalized = self._normalize_content(content)

            # Check against seen items
            is_duplicate = False
            for seen_id, seen_normalized in seen_contents:
                similarity = self._fuzzy_similarity(normalized, seen_normalized)

                if similarity >= self.threshold:
                    is_duplicate = True
                    duplicate_ids.add(item_id)
                    break

            if not is_duplicate:
                seen_contents.append((item_id, normalized))
                unique_ids.add(item_id)

        return unique_ids, duplicate_ids

    def _deduplicate_vector(self, contents: List[Tuple[str, str]]) -> Tuple[Set[str], Set[str]]:
        """Vector similarity deduplication.

        Args:
            contents: List of (id, content) tuples

        Returns:
            Tuple of (unique_ids, duplicate_ids)
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE or not self.model:
            # Fall back to fuzzy
            return self._deduplicate_fuzzy(contents)

        unique_ids = set()
        duplicate_ids = set()

        # Extract IDs and contents
        ids = [c[0] for c in contents]
        texts = [c[1] for c in contents]

        # Encode texts
        embeddings = self.model.encode(texts, show_progress_bar=False)

        # Calculate similarity matrix
        for i, (item_id, embedding) in enumerate(zip(ids, embeddings)):
            # Compare with all previous items
            is_duplicate = False
            for j in range(i):
                similarity = self._cosine_similarity(embedding, embeddings[j])

                if similarity >= self.threshold:
                    is_duplicate = True
                    duplicate_ids.add(item_id)
                    break

            if not is_duplicate:
                unique_ids.add(item_id)

        return unique_ids, duplicate_ids

    def _normalize_content(self, content: str) -> str:
        """Normalize content for comparison.

        Args:
            content: Input content

        Returns:
            Normalized content string
        """
        if not content:
            return ""

        # Convert to lowercase
        normalized = content.lower()

        # Remove URLs
        normalized = re.sub(r'https?://\S+', '', normalized)

        # Remove extra whitespace
        normalized = ' '.join(normalized.split())

        # Remove special characters (keep alphanumeric and basic punctuation)
        normalized = re.sub(r'[^\w\s\.,!?-]', '', normalized)

        return normalized.strip()

    def _fuzzy_similarity(self, s1: str, s2: str) -> float:
        """Calculate fuzzy similarity between two strings.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Similarity score (0-1)
        """
        if not s1 or not s2:
            return 0.0

        matcher = SequenceMatcher(None, s1, s2)
        ratio = matcher.ratio()

        return ratio

    def _cosine_similarity(self, vec1, vec2) -> float:
        """Calculate cosine similarity between vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity (0-1)
        """
        # Dot product
        dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))

        # Magnitudes
        mag1 = sum(v1 ** 2 for v1 in vec1) ** 0.5
        mag2 = sum(v2 ** 2 for v2 in vec2) ** 0.5

        # Avoid division by zero
        if mag1 == 0 or mag2 == 0:
            return 0.0

        # Cosine similarity
        similarity = dot_product / (mag1 * mag2)

        return similarity

    def deduplicate_urls(
        self,
        items: List[Dict[str, Any]],
        url_field: str = "url",
        id_field: str = "id"
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Deduplicate by URL.

        Args:
            items: List of items
            url_field: Field name containing URL
            id_field: Field name containing item ID

        Returns:
            Tuple of (unique_items, duplicates)
        """
        unique_ids = set()
        duplicate_ids = set()
        seen_urls = set()

        for item in items:
            url = item.get(url_field)

            if not url:
                unique_ids.add(item.get(id_field))
                continue

            # Normalize URL
            normalized_url = self._normalize_url(url)

            if normalized_url in seen_urls:
                duplicate_ids.add(item.get(id_field))
            else:
                seen_urls.add(normalized_url)
                unique_ids.add(item.get(id_field))

        unique_items = [item for item in items if item.get(id_field) in unique_ids]
        duplicate_items = [item for item in items if item.get(id_field) in duplicate_ids]

        return unique_items, duplicate_items

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for comparison.

        Args:
            url: URL to normalize

        Returns:
            Normalized URL
        """
        if not url:
            return ""

        normalized = url.lower()

        # Remove query parameters
        if '?' in normalized:
            normalized = normalized.split('?')[0]

        # Remove fragments
        if '#' in normalized:
            normalized = normalized.split('#')[0]

        # Remove trailing slash
        normalized = normalized.rstrip('/')

        return normalized
