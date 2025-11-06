import os
import google.generativeai as genai
from config import (
    EMBEDDING_MODEL,
    FAISS_INDEX_PATH,
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USERNAME,
)
from europe_kg_rag.graph import KnowledgeGraphQuerier
from europe_kg_rag.retrieval import (
    EntityExtractor,
    VectorRetriever,
    entity_driven_retrieval,
    rank_fusion_retrieval,
)

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
llm = genai.GenerativeModel('models/gemini-2.5-flash')

kg_querier = KnowledgeGraphQuerier(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

vector_retriever = VectorRetriever(
    model_name=EMBEDDING_MODEL,
    faiss_index_path=FAISS_INDEX_PATH,
    corpus_path="data/text_corpus.json"
)

entity_extractor = EntityExtractor()


def generate_answer(context, question):
    prompt = f"""
    You are a meticulous and fact-grounded AI assistant. Your task is to answer the user's question with high accuracy and clarity.

    To do this, you must strictly adhere to the following rules:
    1.  Synthesize your answer by drawing information from the provided CONTEXT below.
    2.  Base your entire answer ONLY on the information given in the context. Do not use any external knowledge.
    3.  If you use a fact from the context, you can optionally cite it (e.g., using [KG] or [Text]).
    4.  If the provided context is insufficient to answer the question, you must state that clearly.

    --- CONTEXT ---
    {context}
    --- END OF CONTEXT ---

    QUESTION:
    {question}

    ANSWER:
    """
    try:
        response = llm.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"
    

def retrieve_kg_only(query):
    facts = []
    entities = entity_extractor.extract_entities(query)
    for entity in entities:
        cypher_query = (
            "MATCH (e)-[r]-(n) WHERE e.name = $entity RETURN e.name, type(r), n.name"
        )
        results = kg_querier.query(cypher_query, {"entity": entity})
        for result in results:
            fact = f"[KG] [{result['e.name']}] -[:{result['type(r)']}]-> [{result['n.name']}]"
            facts.append(fact)

    return "\n".join(facts) if facts else "No specific facts found in KG for extracted entities."


def retrieve_text_only(query):
    retrieved_docs = vector_retriever.retrieve(query, k=5)
    retrieved_docs = [f"[TEXT] {retrieved_doc['text']}" for retrieved_doc in retrieved_docs]
    return "\n".join(retrieved_docs)


def retrieve_hybrid_naive(query):
    kg_facts = retrieve_kg_only(query)
    text_facts = retrieve_text_only(query)

    return f"--- Knowledge Graph Facts ---\n{kg_facts}\n\n--- Related Descriptions ---\n{text_facts}"


def run_experiment(model_name, question):
    print(f"\n{'='*20} RUNNING EXPERIMENT: {model_name} {'='*20}\n")
    print(f"QUESTION: {question}")
    print(f"{'-'*50}")

    context = ""
    if model_name == 'KG-Only':
        context = retrieve_kg_only(question)
    elif model_name == 'Text-Only':
        context = retrieve_text_only(question)
    elif model_name == 'Hybrid-Naive':
        context = retrieve_hybrid_naive(question)
    elif model_name == 'Entity-Driven':
        context = entity_driven_retrieval(question, kg_querier, vector_retriever, entity_extractor)
    elif model_name == 'Hybrid-Fusion':
        context = rank_fusion_retrieval(question, kg_querier, vector_retriever, entity_extractor)
    else:
        raise ValueError(f"Unknown model name: {model_name}")

    print(f"--- RETRIEVED CONTEXT ---\n{context}\n{'-'*50}")
    answer = generate_answer(context, question)
    print(f"ANSWER: {answer}\n{'=-'*60}\n")


if __name__ == "__main__":
    test_question = [
        "What is the capital of Spain and can you describe it?",
        "Which countries border Switzerland?",
        "Tell ne about the geography of Italy."
    ]

    models_to_test = [
        "KG-Only",
        "Text-Only",
        "Hybrid-Naive",
        "Entity-Driven",
        "Hybrid-Fusion"
    ]

    for question in test_question:
        for model in models_to_test:
            run_experiment(model, question)

    kg_querier.close()
