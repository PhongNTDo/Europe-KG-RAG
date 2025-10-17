from collections import defaultdict
from retrieval.entity_extraction import EntityExtractor

entity_extractor = EntityExtractor()

def reciprocal_rank_fusion(ranked_lists, k=5):
    scores = defaultdict(float)

    for ranked_list in ranked_lists:
        for i, doc in enumerate(ranked_list):
            scores[doc] += 1.0 /(k + i + 1)

    sorted_item = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [item for item, _ in sorted_item]


def rank_fusion_retrieval(query, kg_querier, vector_retriever):
    context = ""
    entities = entity_extractor.extract_entities(query)
    kg_results = []
    if entities:
        for entity in entities:
            cypher_query = f"MATCH (e)-[r]-(n) WHERE e.name = '{entity}' return e.name, type(r), n.name"
            results = kg_querier.query(cypher_query)
            for result in kg_results:
                kg_results.append(f"[KG] ({result['e.name']}) -[:{result['type(r)']}]-> ({result['n.name']})")
    text_results = [f"[TEXT] {doc['text']}" for doc in vector_retriever.retrieve(query)]
    fused_results = reciprocal_rank_fusion([kg_results, text_results])
    conext = "--- Knowledge Graph Facts ---\n"
    for result in fused_results:
        if result.startswith("[KG]"):
            context += result + "\n"
    context += "\n--- Related Descriptions ---\n"
    for result in fused_results:
        if result.startswith("[TEXT]"):
            context += result + "\n"
    return conext


if __name__ == "__main__":
    ranked_lists = [
        ["Gemany borders Poland", "Germany borders France"],
        ["The capital of France is Paris", "Paris is the capital of France", "Effiel Tower is in Paris"]
    ]
    fused_results = reciprocal_rank_fusion(ranked_lists)
    for i, item in enumerate(fused_results):
        print(f"{i+1}. {item}")
    
