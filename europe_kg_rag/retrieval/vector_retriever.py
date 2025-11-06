from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

import faiss
import google.generativeai as genai
import numpy as np


class VectorRetriever:
    """Wrapper around FAISS and Gemini embeddings."""

    def __init__(
        self,
        model_name: str,
        faiss_index_path: str | Path,
        corpus_path: str | Path,
        api_key: str | None = None,
    ) -> None:
        self.model_name = model_name
        self.faiss_index_path = Path(faiss_index_path)
        self.corpus_path = Path(corpus_path)
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise EnvironmentError("GOOGLE_API_KEY is required for VectorRetriever.")

        genai.configure(api_key=self.api_key)
        self.corpus = self._load_corpus()
        self.index = self._get_or_build_index()

    def _load_corpus(self) -> list[dict]:
        with self.corpus_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _get_or_build_index(self):
        if self.faiss_index_path.exists():
            return faiss.read_index(str(self.faiss_index_path))
        return self._build_index()

    def _build_index(self):
        texts = [item["text"] for item in self.corpus]
        embeddings = [self._embed_text(text) for text in texts]
        if not embeddings:
            raise ValueError("Corpus is empty; cannot build FAISS index.")

        dim = len(embeddings[0])
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings, dtype=np.float32))
        faiss.write_index(index, str(self.faiss_index_path))
        return index

    def _embed_text(self, text: str) -> np.ndarray:
        response = genai.embed_content(
            model=self.model_name,
            content=text,
            task_type="RETRIEVAL_DOCUMENT",
        )
        embedding = np.array(response["embedding"], dtype=np.float32)
        return embedding

    def retrieve(self, query_text: str, k: int = 5) -> List[dict]:
        query_embedding = genai.embed_content(
            model=self.model_name,
            content=query_text,
            task_type="RETRIEVAL_QUERY",
        )["embedding"]
        query_embedding = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_embedding, k)
        return [self.corpus[idx] for idx in indices[0]]
