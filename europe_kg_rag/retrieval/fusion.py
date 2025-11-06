from __future__ import annotations

from collections import defaultdict
from typing import Iterable, List, Sequence

from .entity_extraction import EntityExtractor


def reciprocal_rank_fusion(ranked_lists: Sequence[Sequence[str]], k: int = 60) -> list[str]:
    """Combine ranked lists using Reciprocal Rank Fusion."""
    scores = defaultdict(float)
    for ranked_list in ranked_lists:
        for idx, item in enumerate(ranked_list):
            scores[item] += 1.0 / (k + idx + 1)
    return [item for item, _ in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)]


def rank_fusion_retrieval(
    query: str,
    kg_querier,
    vector_retriever,
    extractor: EntityExtractor | None = None,
    k: int = 5,
) -> str:
    extractor = extractor or EntityExtractor()
    entities = extractor.extract_entities(query)
    kg_results = _fetch_kg_results(entities, kg_querier) if entities else []
    text_results = [f"[TEXT] {doc['text']}" for doc in vector_retriever.retrieve(query, k=k)]

    fused = reciprocal_rank_fusion([kg_results, text_results], k=k)

    context_parts: list[str] = ["--- Knowledge Graph Facts ---"]
    context_parts.extend(item for item in fused if item.startswith("[KG]"))
    context_parts.append("\n--- Related Descriptions ---")
    context_parts.extend(item for item in fused if item.startswith("[TEXT]"))

    return "\n".join(context_parts)


def _fetch_kg_results(entities: Iterable[str], kg_querier) -> List[str]:
    kg_results: list[str] = []
    for entity in entities:
        cypher_query = (
            "MATCH (e)-[r]-(n) WHERE e.name = $entity RETURN e.name, type(r), n.name"
        )
        results = kg_querier.query(cypher_query, {"entity": entity})
        for record in results:
            kg_results.append(
                f"[KG] ({record['e.name']}) -[:{record['type(r)']}]-> ({record['n.name']})"
            )
    return kg_results
