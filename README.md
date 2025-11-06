# Europe-KG-RAG

Europe-KG-RAG is an experiment-friendly knowledge-graph Retrieval-Augmented Generation (RAG) playground focused on European geography. Structured facts (countries, rivers, etc.) are loaded into Neo4j and paired with a text corpus that is searchable through FAISS + Gemini embeddings, enabling flexible retrieval strategies.

## Project Flow

1. **Data**: JSON databases in `data/database/` (currently `europe_countries.json` and `europe_rivers.json`) describe the entities and their attributes/relationships. Crawled/raw sources are stored under `data/crawled_data/` and scripts in `data/` transform them.
2. **Loading**: `europe_kg_rag.data.DatabaseLoader` parses the JSON files into strongly typed dataclasses (`Country`, `River`) while cleaning fields and normalizing names.
3. **Graph Build**: `europe_kg_rag.graph.KnowledgeGraphBuilder` ingests the structured dataset into Neo4j, creating nodes for countries, cities, rivers, and relevant water bodies, and wiring edges such as `HAS_CAPITAL`, `BORDERS_WITH`, `FLOWS_THROUGH`, `TRIBUTES_TO`, and `FLOWS_INTO`.
4. **Retrieval**: 
   - `europe_kg_rag.graph.KnowledgeGraphQuerier` runs Cypher queries against Neo4j for KG-only or entity-driven strategies.
   - `europe_kg_rag.retrieval.VectorRetriever` handles text retrieval using Gemini embeddings and a FAISS index built from `data/text_corpus.json`.
   - `europe_kg_rag.retrieval.entity_driven_retrieval` and `europe_kg_rag.retrieval.rank_fusion_retrieval` merge KG facts with text snippets.
5. **Generation**: `main.py` orchestrates experimental runs (KG-only, Text-only, Hybrid, Entity-driven, Fusion) and feeds the aggregated context to Gemini for answer generation.

## Repository Layout (key paths)

- `config.py` – Neo4j credentials, Gemini/embedding configuration, FAISS path.
- `data/database/` – curated JSON databases that feed the KG.
- `europe_kg_rag/` – reusable package (`data`, `graph`, `retrieval` modules).
- `setup_neo4j_kg.py` – rebuilds the Neo4j database from the JSON sources.
- `main.py` – runs retrieval experiments and answer generation.
- `retrieval/`, `knowledge_graph/` – legacy modules (kept only if needed for reference; new work should rely on `europe_kg_rag/`).
- `data/processing_data_rivers.py`, `data/process_rivers_csv.py`, etc. – helper scripts to refresh the JSON databases from crawled sources when needed.

## Requirements & Setup

1. **Python**: 3.10+ recommended.
2. **Neo4j**: Running instance accessible via the URI configured in `config.py`.
3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **Environment variables**:
   - `GOOGLE_API_KEY` – required for Gemini (embeddings + text generation).

5. **Configure Neo4j credentials**:
   - Update `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` in `config.py`, or load them from env vars if you adapt the config.

## Building the Knowledge Graph

1. Ensure your Neo4j instance is running and accessible.
2. Verify the curated data in `data/database/`. Regenerate from crawled sources if needed (`data/processing_data_rivers.py`, etc.).
3. Run the builder:

   ```bash
   python setup_neo4j_kg.py
   ```

   - The script loads `europe_countries.json` and `europe_rivers.json`, clears the database (configurable), and rebuilds nodes + edges.
4. Inspect Neo4j Browser (or run Cypher queries) to confirm nodes and relationships were created.

## Retrieval & QA Experiments

1. Build or reuse the FAISS index. The first run of `main.py` will embed the text corpus and store the index at `data/vector_db.faiss`.
2. Run experiments:

   ```bash
   GOOGLE_API_KEY=your_key python main.py
   ```

   - The script will iterate over sample questions (`test_question`) and retrieval strategies (`models_to_test`), printing the retrieved context and generated answers.
3. Customize `test_question` or plug `retrieve_kg_only`, `retrieve_text_only`, `entity_driven_retrieval`, or `rank_fusion_retrieval` into other workflows as needed.

## Testing / Validation

This project currently relies on manual validation:

- **KG sanity checks**: run targeted Cypher queries via `KnowledgeGraphQuerier` or Neo4j Browser.
- **Retrieval smoke tests**: execute `python main.py` and review contexts/answers for plausibility.
- **Data loader checks**: using the REPL to instantiate `DatabaseLoader` helps ensure new datasets parse correctly.

Automated tests can be added under a `tests/` directory (e.g., using `pytest`) once stable fixtures or mock services are available.

## Extending the Database (Example: Mountains)

To add a new entity type (e.g., mountains) that should participate in the KG:

1. **Create/curate the data**:
   - Add a new JSON file such as `data/database/europe_mountains.json` with a consistent schema (name, elevation, location, related countries, etc.).
2. **Extend data models**:
   - Add a `Mountain` dataclass in `europe_kg_rag/data/models.py`.
   - Update `DatabaseLoader` to load the new JSON file and populate a `mountains` list in `GraphDataset`.
3. **Update the graph builder**:
   - Teach `KnowledgeGraphBuilder` how to create `(:Mountain)` nodes, attach attributes, and define relationships (`LOCATED_IN`, `NEAR`, etc.) based on your schema.
4. **Adjust retrieval logic (optional)**:
   - Update KG queries or retrieval prompts if you want mountains to be surfaced explicitly.
   - Extend `entity_driven_retrieval` so it recognizes mountain names where relevant.
5. **Regenerate the KG**:
   - Re-run `python setup_neo4j_kg.py` to ingest the new entity type.
6. **Validate**:
   - Query Neo4j (or run `main.py`) to confirm mountains appear in relationships and retrieval outputs.

Following the same pattern lets you plug in additional datasets (landmarks, mountain ranges, lakes, etc.) while keeping ingestion logic organized inside `europe_kg_rag/`.

## TODO / Next Steps

- [ ] **Expand geographic entities** – ingest new datasets (mountains, lakes, landmarks, etc.) and extend the KG builder + dataclasses.
- [ ] **Enrich locations with lat/long** – add latitude/longitude attributes so the project captures geospatial context.
- [ ] **Local UI** – create a lightweight dashboard to trigger retrieval/Q&A runs and visualize KG results locally.
- [ ] **Data validation pipeline** – add schema/consistency checks for raw crawled data before it reaches the curated JSON.
- [ ] **Automated retrieval benchmarks** – build a labeled QA set and evaluation script to measure accuracy across strategies.
- [ ] **Containerized stack** – ship Docker (or Docker Compose) definitions for Neo4j + the app to simplify onboarding.
- [ ] **Observability/logging** – implement structured logging and optional tracing around retrieval + KG calls.
- [ ] **Documentation refresh tooling** – script the generation of data dictionaries/diagrams from the JSON schemas.
