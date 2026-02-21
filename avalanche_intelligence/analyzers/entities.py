"""Entity extraction from text."""

import re
from typing import List, Dict, Any, Set
from collections import Counter

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class EntityExtractor:
    """Entity extractor for projects, people, and organizations."""

    # Common Avalanche ecosystem entities
    AVALANCHE_ENTITIES = {
        "projects": [
            "avalanche", "avax", "subnet", "c-chain", "x-chain", "p-chain",
            "spruce", "evergreen", "fuji", "denali", "cortina",
            "aave", "benqi", "pangolin", "joe", "trader joe",
            "curve", "sushi", "uniswap", "gmx", "platypus",
            "defi kingdoms", "lyra", "vesta", "liquid staked avax",
            "yield yak", "beefy", "wonderland", "meridian",
            "gmx", "gale", "delta prime", "banker joe",
        ],
        "organizations": [
            "avalanche labs", "ava labs", "avalanche foundation",
            "t rowe price", "wisdomtree", "fuson wealth",
            "goldman sachs", "jpmorgan", "deloitte", "kpmg",
            "galaxy digital", "coinbase", "binance", "kraken",
            "ftx", "celsius", "blockfi",
        ],
        "technology": [
            "avalanchego", "subnet evm", "coreth", "avalanchejs",
            "teleporter", "pangolin exchange", "woofi", "glacier",
            "rapr", "cbridge", "anyswap", "chainlink",
            "chainabstraction", "wormhole", "layerzero",
        ],
        "tokens": [
            "avax", "wavax", "weth", "usdc", "usdt", "dai",
            "tusd", "usdt.e", "usdc.e", "wbtc", "wbtce",
            "benqi", "q", "png", "joe", "gmx", "plv",
            "gjp", "gsp", "tjoe", "xjoe", "mim",
        ],
    }

    def __init__(self, use_spacy: bool = True):
        """Initialize entity extractor.

        Args:
            use_spacy: Whether to use spaCy NER
        """
        self.use_spacy = use_spacy and SPACY_AVAILABLE

        if self.use_spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                # Model not downloaded, fall back to regex
                print("spaCy model not found, falling back to regex extraction")
                self.use_spacy = False
                self.nlp = None
        else:
            self.nlp = None

    def extract(self, text: str) -> Dict[str, Any]:
        """Extract entities from text.

        Args:
            text: Input text

        Returns:
            Dictionary of extracted entities by category
        """
        entities = {
            "projects": [],
            "organizations": [],
            "technology": [],
            "tokens": [],
            "hashtags": [],
            "mentions": [],
            "urls": [],
            "emails": [],
            "cashtags": [],
        }

        # Extract using spaCy if available
        if self.use_spacy:
            spacy_entities = self._extract_spacy(text)
            entities.update(spacy_entities)

        # Extract using regex patterns
        regex_entities = self._extract_regex(text)
        entities.update(regex_entities)

        # Extract Avalanche ecosystem entities
        ecosystem_entities = self._extract_ecosystem(text)
        entities.update(ecosystem_entities)

        # Deduplicate within categories
        for category in entities:
            entities[category] = list(set(entities[category]))

        return entities

    def _extract_spacy(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using spaCy NER.

        Args:
            text: Input text

        Returns:
            Dictionary of entities by category
        """
        entities = {
            "organizations": [],
            "people": [],
            "locations": [],
        }

        if not self.nlp:
            return entities

        doc = self.nlp(text)

        for ent in doc.ents:
            entity_text = ent.text.lower()

            if ent.label_ == "ORG":
                entities["organizations"].append(entity_text)
            elif ent.label_ == "PERSON":
                entities["people"].append(entity_text)
            elif ent.label_ in ("GPE", "LOC"):
                entities["locations"].append(entity_text)

        return entities

    def _extract_regex(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using regex patterns.

        Args:
            text: Input text

        Returns:
            Dictionary of entities by category
        """
        entities = {
            "hashtags": [],
            "mentions": [],
            "urls": [],
            "emails": [],
            "cashtags": [],
        }

        # Hashtags (#hashtag)
        entities["hashtags"] = re.findall(r'#(\w+)', text)

        # Mentions (@mention)
        entities["mentions"] = re.findall(r'@(\w+)', text)

        # URLs (http/https)
        entities["urls"] = re.findall(r'https?://\S+', text)

        # Emails
        entities["emails"] = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)

        # Cashtags ($ticker)
        entities["cashtags"] = re.findall(r'\$(\w+)', text)

        return entities

    def _extract_ecosystem(self, text: str) -> Dict[str, List[str]]:
        """Extract Avalanche ecosystem entities.

        Args:
            text: Input text

        Returns:
            Dictionary of entities by category
        """
        entities = {
            "projects": [],
            "organizations": [],
            "technology": [],
            "tokens": [],
        }

        text_lower = text.lower()

        # Extract projects
        for project in self.AVALANCHE_ENTITIES["projects"]:
            if project in text_lower:
                entities["projects"].append(project)

        # Extract organizations
        for org in self.AVALANCHE_ENTITIES["organizations"]:
            if org in text_lower:
                entities["organizations"].append(org)

        # Extract technology
        for tech in self.AVALANCHE_ENTITIES["technology"]:
            if tech in text_lower:
                entities["technology"].append(tech)

        # Extract tokens
        for token in self.AVALANCHE_ENTITIES["tokens"]:
            if token in text_lower:
                entities["tokens"].append(token)

        return entities

    def extract_trends(self, texts: List[str], top_n: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Extract trending entities across multiple texts.

        Args:
            texts: List of texts to analyze
            top_n: Number of top trends to return

        Returns:
            Dictionary of trending entities by category
        """
        all_entities = {
            "projects": Counter(),
            "organizations": Counter(),
            "technology": Counter(),
            "tokens": Counter(),
            "hashtags": Counter(),
        }

        # Extract entities from all texts
        for text in texts:
            entities = self.extract(text)

            for category in all_entities:
                if category in entities:
                    all_entities[category].update(entities[category])

        # Get top N for each category
        trends = {}
        for category, counter in all_entities.items():
            trends[category] = [
                {"entity": entity, "count": count}
                for entity, count in counter.most_common(top_n)
            ]

        return trends

    def extract_project_mentions(self, text: str) -> List[str]:
        """Extract only project mentions from text.

        Args:
            text: Input text

        Returns:
            List of project mentions
        """
        entities = self.extract(text)
        return entities.get("projects", [])

    def extract_token_mentions(self, text: str) -> List[str]:
        """Extract only token mentions from text.

        Args:
            text: Input text

        Returns:
            List of token mentions
        """
        entities = self.extract(text)
        return entities.get("tokens", [])

    def link_entities(self, text: str, known_entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Link extracted entities to known entity database.

        Args:
            text: Input text
            known_entities: Dictionary of known entities with metadata

        Returns:
            List of linked entities with metadata
        """
        entities = self.extract(text)
        linked = []

        # Iterate through all entity categories
        for category, entity_list in entities.items():
            for entity in entity_list:
                # Find in known entities
                if category in known_entities:
                    for known in known_entities[category]:
                        if entity.lower() == known.get("name", "").lower():
                            linked.append({
                                "entity": entity,
                                "category": category,
                                "metadata": known,
                            })

        return linked
