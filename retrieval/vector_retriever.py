import os
import json
import faiss
import numpy as np
# from google import genai
import google.generativeai as genai
from google.generativeai import types
from sklearn.metrics.pairwise import cosine_similarity

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

class VectorRetriever:
    def __init__(self, model_name, faiss_index_path, corpus_path):
        self.faiss_index_path = faiss_index_path
        self.corpus_path = corpus_path
        self.model_name = model_name
        self.corpus = self._load_corpus()
        self.index = self._get_index()

    def _load_corpus(self):
        with open(self.corpus_path, "r") as file:
            return json.load(file)

    def _get_index(self):
        try:
            index = faiss.read_index(self.faiss_index_path)
            print(f"Faiss index loaded from file {self.faiss_index_path}")
        except RuntimeError:
            print("Building FAISS index from scratch...")
            texts = [item['text'] for item in self.corpus]
            embeddings = []
            for text in texts:
                # response = self.gemini_client.models.embed_content(
                #     model=self.model_name,
                #     contents=text)
                response = genai.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type="RETRIEVAL_QUERY")
                
                embeddings.append(np.array(response['embedding']))
            index = faiss.IndexFlatL2(len(embeddings[1]))
            index.add(np.array(embeddings, dtype=np.float32))
            faiss.write_index(index, self.faiss_index_path)
            print(f"Faiss index saved to file {self.faiss_index_path}")
        return index

    def retrieve(self, query_text, k=3):
        query_embedding = genai.embed_content(
            model=self.model_name,
            content=query_text,
            task_type="RETRIEVAL_QUERY"
        )['embedding']
        query_embedding = np.array(query_embedding).reshape(1, -1)
        distances, indices = self.index.search(query_embedding, k)
        
        results = [self.corpus[idx] for idx in indices[0]]
        return results
    

if __name__ == "__main__":
    from config import GEMINI_API_KEY, EMBEDDING_MODEL, FAISS_INDEX_PATH

    vector_retriever = VectorRetriever(
        model_name="gemini-embedding-001",
        faiss_index_path=FAISS_INDEX_PATH,
        corpus_path="data/text_corpus.json"
    )

    query = "description of the Eiffel Tower"
    retrieved_docs = vector_retriever.retrieve(query)
    print(retrieved_docs)