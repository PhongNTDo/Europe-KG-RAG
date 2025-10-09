import google.generativeai as genai
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, EMBEDDING_MODEL, FAISS_INDEX_PATH
from knowledge_graph.kg_querier import KnowledgeGraphQuerier
from retrieval.vector_retriever import VectorRetriever

llm = genai.GenerativeModel('models/gemini-2.5-flash')

kg_querier = KnowledgeGraphQuerier(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

vector_retriever = VectorRetriever(
    model_name=EMBEDDING_MODEL,
    faiss_index_path=FAISS_INDEX_PATH,
    corpus_path="data/text_corpus.json"
)

def generate_answer(context, question):
    prompt = f"""
    Based on the following context, please answer the question.

    Context:
    {context}

    Question:
    {question}
    """
    try:
        response = llm.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"
    

def retrieve_kg_only(entities):
    all_facts = []
    for entity_type, entity_name in entities:
        if entity_type == "country_rivers":
            query = f"MATCH (r:River)-[:FLOWS_THROUGH]->(c:Country {{name: '{entity_name}'}}) RETURN r.name AS river"
            results = kg_querier.query(query)
            facts = [f"The river {res['river']} flows through {entity_name}." for res in results]
            all_facts.extend(facts)

        elif entity_type == "country_landmarks":
            query = f"MATCH (l:Landmark)-[:LOCATED_IN]->(c:Country {{name: '{entity_name}'}}) RETURN l.name AS landmark"
            results = kg_querier.query(query)
            facts = [f"The landmark {res['landmark']} is located in {entity_name}." for res in results]
            all_facts.extend(facts)

        elif entity_type == "country_borther":
            query = f"MATCH (c1:Country)-[:BORDERS_WITH]->(c2:Country {{name: '{entity_name}'}}) RETURN c1.name AS neighbor"
            results = kg_querier.query(query)
            facts = [f"The country {entity_name} borders with {res['neighbor']}." for res in results]
            all_facts.extend(facts)

    return "\n".join(all_facts)


def retrieve_text_only(query):
    retrieved_docs = vector_retriever.retrieve(query, k=5)
    retrieved_docs = [f"{retrieved_doc['id']}: {retrieved_doc['text']}" for retrieved_doc in retrieved_docs]
    return "\n".join(retrieved_docs)


def retrieve_hybrid(kg_queries, query):
    kg_facts = retrieve_kg_only(kg_queries)
    text_facts = retrieve_text_only(query)

    return f"--- Knowledge Graph Facts ---\n{kg_facts}\n\n--- Related Descriptions ---\n{text_facts}"


def run_experiment(question, kg_entities, retrieval_query):
    print(f"\n{'='*30}")
    print(f"QUESTION: {question}")
    print(f"{'='*30}")

    print("--- 1. KG Only ---")
    kg_facts = retrieve_kg_only(kg_entities)
    kg_answer = generate_answer(kg_facts, question)
    print('Context:\n', kg_facts)
    print('Answer:\n', kg_answer)
    print('-' * 15)

    print("\n--- 2. Text Only ---")
    text_facts = retrieve_text_only(retrieval_query)
    text_answer = generate_answer(text_facts, question)
    print('Context:\n', text_facts)
    print('Answer:\n', text_answer)
    print('-' * 15)

    print("\n--- 3. Hybrid KG + Text RAG Answer ---")
    hybrid_context = retrieve_hybrid(kg_entities, retrieval_query)
    hybrid_answer = generate_answer(hybrid_context, question)
    print('Context:\n', hybrid_context)
    print('Answer:\n', hybrid_answer)
    print('-' * 15)


if __name__ == "__main__":
    # Example 1
    run_experiment(
        question="Which rivers flow through Germany? Add a short description of each",
        kg_entities=[("country_rivers", "Germany")],
        retrieval_query="Rivers in Gemany: Danube, Rhine, Elbe"
    )

    # Example 2
    run_experiment(
        question="What landmarks are in France, and why are they important?",
        kg_entities=[("country_landmarks", "France")],
        retrieval_query="Landmarks in France: Eiffel Tower, Louvre Muesum"
    )

    # Example 3
    run_experiment(
        question="List countries bordering Switzerland and describe one cultural fact about each.",
        kg_entities=[("country_borther", "Switzerland")],
        retrieval_query="Cultural facts about Germany, Austria, France"
    )

    kg_querier.close()
