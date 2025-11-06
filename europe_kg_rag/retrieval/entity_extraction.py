from __future__ import annotations

from typing import Iterable, List

import spacy


class EntityExtractor:
    """Wrapper around spaCy for lightweight entity extraction."""

    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        self.model_name = model_name
        self.nlp = spacy.load(model_name)

    def extract_entities(self, text: str) -> List[str]:
        if not text:
            return []
        doc = self.nlp(text)
        allowed_labels = {"GPE", "LOC", "PERSON", "FAC", "ORG"}
        return [ent.text for ent in doc.ents if ent.label_ in allowed_labels]


def _format_kg_fact(record: dict) -> str:
    return f"[KG] [{record['e.name']}] -[:{record['type(r)']}]-> [{record['n.name']}]"


def entity_driven_retrieval(
    query: str,
    kg_querier,
    vector_retriever,
    extractor: EntityExtractor | None = None,
    k: int = 5,
) -> str:
    extractor = extractor or EntityExtractor()
    entities = extractor.extract_entities(query)
    if not entities:
        docs = vector_retriever.retrieve(query, k=k)
        return "--- Related Descriptions ---\n" + "\n".join(f"[TEXT] {doc['text']}" for doc in docs)

    kg_facts = _fetch_kg_facts(entities, kg_querier)
    retrieved_entity_names = _collect_entities_from_facts(kg_facts)

    augmented_query = query + " " + " ".join(sorted(retrieved_entity_names))
    docs = vector_retriever.retrieve(augmented_query, k=k)
    text_context = "\n".join(f"[TEXT] {doc['text']}" for doc in docs)

    kg_context = "\n".join(kg_facts) if kg_facts else "No specific facts found in KG for extracted entities."
    return f"--- Knowledge Graph Facts ---\n{kg_context}\n\n--- Related Descriptions (Entities focussed) ---\n{text_context}"


def _fetch_kg_facts(entities: Iterable[str], kg_querier) -> list[str]:
    facts: list[str] = []
    for entity in entities:
        cypher_query = (
            "MATCH (e)-[r]-(n) WHERE e.name = $entity RETURN e.name, type(r), n.name"
        )
        results = kg_querier.query(cypher_query, {"entity": entity})
        facts.extend(_format_kg_fact(result) for result in results)
    return facts


def _collect_entities_from_facts(facts: Iterable[str]) -> set[str]:
    entity_names: set[str] = set()
    for fact in facts:
        segments = fact.split("[")
        for segment in segments:
            if "]" in segment:
                entity_names.add(segment.split("]", 1)[0])
    return entity_names
