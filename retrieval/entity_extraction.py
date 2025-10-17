import spacy

class EntityExtractor:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')

    def extract_entities(self, text):
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC', 'PERSON', 'FAC', 'ORG']:
                entities.append((ent.text))
        return entities
    
entity_extractor = EntityExtractor()

def entity_driven_retrieval(query, kg_querier, vector_retriever):
    entities = entity_extractor.extract_entities(query)
    if not entities:
        return f"--- Related Descriptions ---\n" + "\n".join(vector_retriever.retrieve(query))
    
    kg_facts = []
    retrieved_entity_names = set()
    for entity in entities:
        cypher_query = f"MATCH (e)-[r]-(n) WHERE e.name = '{entity}' return e.name, type(r), n.name"
        results = kg_querier.query(cypher_query)
        for result in results:
            fact = f"[KG] [{result['e.name']}] -[:{result['type(r)']}]-> [{result['n.name']}]"
            kg_facts.append(fact)
            retrieved_entity_names.add(result['e.name'])
            retrieved_entity_names.add(result['n.name'])

    kg_context = "No specific facts found in KG for extracted entities."
    if kg_facts:
        kg_context = "\n".join(kg_facts)

    augmented_query = query + " " + " ".join(retrieved_entity_names)
    results_text = vector_retriever.retrieve(augmented_query)
    results_text = [f"[TEXT] {doc['text']}" for doc in results_text]
    text_context = "\n".join(results_text)

    return f"--- Knowledge Graph Facts ---\n{kg_context}\n\n--- Related Descriptions (Entities focussed) ---\n{text_context}"


if __name__ == '__main__':
    extractor = EntityExtractor()
    text = "What is the capital of France? Which rivers flow through Germany and Austria? The Eiffel Tower is in Paris."
    
    entities = extractor.extract_entities(text)
    print("Entities:", entities)