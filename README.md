# Vietnamese Legal Judgment Prediction System (LJP-Graph-Augmented-RAG)

A Graph-Augmented Retrieval-Augmented Generation (RAG) system for predicting legal outcomes and penalties from criminal act descriptions in Vietnamese. The system integrates hybrid search (BM25 + vector cosine distance) with a structured legal reference graph (Graph Law Reference Expansion) to augment the LLM's context with logically related laws.

---

## Pipeline Architecture

The system consists of two main stages: the Data Ingestion Pipeline and the Inference Pipeline.

### 1. Data Ingestion Pipeline

The graph construction phase occurs during ingestion, where legal article cross-references are analyzed to build the reference map. (The graph components are highlighted in blue).

```mermaid
graph TD
    A["Raw luat.doc"] -->|"win32com"| B["luat.docx"]
    B -->|"Parser"| C["Law Metadata JSON"]
    C -->|"Text Splitter"| D["Chunking"]
    D -->|"PyVi Tokenizer"| E["Word Segmentation"]
    E -->|"Bi-Encoder"| F["Generate Embeddings"]
    C -->|"Gemini 2.5 Flash"| G["Graph Builder"]
    G -->|"Reference Map"| H["related_article.json"]
    F -->|"DB Writer"| I["Store in PostgreSQL"]

    classDef graphNode fill:#1f77b4,stroke:#333,stroke-width:1px,color:#fff;
    class G,H graphNode;
```

- **Document Conversion:** Raw `.doc` files are automated and converted to `.docx` format using Microsoft Word Automation (`win32com.client`).
- **Text Chunking:** Article contents are segmented using LangChain's `RecursiveCharacterTextSplitter` to keep the chunk size optimal and under the token limit of the embedding model.
- **Word Segmentation:** Text chunks are segmented into Vietnamese terms using the `pyvi` library (`ViTokenizer`) to format compound words with underscores (e.g., `giáo_viên`, `cố_ý_gây_thương_tích`).
- **Vector Embeddings Generation:** Chunks are converted into 768-dimensional dense vector embeddings using the `bkai-foundation-models/vietnamese-bi-encoder` model.
- **Graph Law Reference Extraction (Graph Construction):** The `gemini-2.5-flash` model, using structured JSON output via a Pydantic schema definition, analyzes the batch of law articles to detect cross-references between different articles. The result is stored in `related_article.json` as an **adjacency list** (where keys are source articles and values are lists of referenced target articles) to construct the **Legal Reference Graph**.
- **Database Storage:** Raw articles, word-segmented chunks, and their vector embeddings are stored in a PostgreSQL database enabled with `pgvector` and Full-Text Search indexes.

---

### 2. Inference Pipeline

The graph augmentation phase occurs during retrieval expansion, pulling in contextually adjacent articles via graph traversal. (The graph expansion node is highlighted in blue).

```mermaid
graph TD
    A["User Query"] --> B["Gemma 4 (Rewrite)"]
    B --> C["Query Embedding"]
    C --> D["Hybrid Search"]
    D --> E["RRF Ranking"]
    E --> F["Reranking (BGE)"]
    F --> G["Graph BFS Expansion"]
    G --> H["Assemble Context"]
    H --> I["Response Gen (Gemma 4)"]
    I --> J["Outcome & Penalty"]

    classDef graphNode fill:#1f77b4,stroke:#333,stroke-width:1px,color:#fff;
    class G graphNode;
```

- **Query Rewriting:** The natural language query is translated into legal terms in the Vietnamese Penal Code using the `gemma-4-31b-it` model.
- **Normalization & Query Embedding:** The rewritten query is segmented using `pyvi` and vectorized using the `vietnamese-bi-encoder`.
- **Hybrid Search:** 
  - **Full-Text Search (FTS):** Searches for keywords using unaccented terms via `unidecode` and `OR` query logic.
  - **Vector Search:** Calculates the cosine distance between the query vector and chunk embeddings in the database using the `<=>` operator from `pgvector`.
- **Reciprocal Rank Fusion (RRF):** Blends the rankings of BM25 (FTS) and semantic vector search in PostgreSQL to produce the best candidate articles.
- **Neural Reranking:** The cross-encoder `BAAI/bge-reranker-v2-m3` scores the candidate chunks against the user query, selecting the top candidates.
- **Graph Lookup Expansion (Graph Augmentation / Context Expansion):** Runs a **Breadth-First Search (BFS)** traversal starting from the top reranked article IDs, querying the graph represented by the **adjacency list** (`related_article.json`). This dynamically retrieves all connected/referenced legal articles, **augmenting the RAG context** with adjacent, mandatory regulations that standard keyword or semantic search alone would miss.
- **Response Generation:** The `gemma-4-31b-it` model generates the final legal analysis (violator status, violation acts, charges, aggravating/mitigating factors, and predicted penalty) in Vietnamese based on the query and retrieved context.

---

## Tech Stack

### 1. AI Models & NLP
- **gemma-4-31b-it:** Used for query rewriting and legal judgment generation.
- **gemini-2.5-flash:** Used for structured JSON law graph extraction.
- **bkai-foundation-models/vietnamese-bi-encoder:** Used for generating semantic embeddings.
- **BAAI/bge-reranker-v2-m3:** Used for neural reranking of retrieved candidates.
- **PyVi (ViTokenizer):** Vietnamese word segmentation tool.
- **Unidecode:** ASCII transliterations of Unicode text for Full-Text Search.

### 2. Database & Vector Storage
- **PostgreSQL:** Relational database for storing raw texts and metadata.
- **pgvector:** PostgreSQL extension for storing and performing vector similarity searches.
- **Full-Text Search:** Native PostgreSQL FTS using `tsvector` and `tsquery`.

### 3. Development Libraries
- **PyTorch:** Underlying framework for running deep learning models.
- **Transformers & Sentence-Transformers:** Hugging Face libraries for executing models and tokenizers.
- **LangChain:** Used for recursive text splitting.
- **Psycopg2-binary:** PostgreSQL client interface for Python.
- **Pydantic:** Data validation and structured schema outputs for the Gemini API.

### 4. Graph & Traversal Algorithms
- **Graph Representation:** Adjacency List (`related_article.json`).
- **Traversal Algorithm:** Breadth-First Search (BFS) using a queue and a visited set to expand contextually-linked articles without cycles.


---

## Getting Started

### 1. Requirements
- Python 3.12 or Python 3.13 (Standard).
- PostgreSQL database with `pgvector` enabled.

### 2. Configuration
Create a `.env` file in the root directory:
```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=rag
DB_USER=postgres
DB_PASSWORD=your_password
GOOGLE_API_KEY=your_gemini_api_key
```

### 3. Installation
Install all dependencies using pip:
```bash
pip install -r requirements.txt
```

### 4. Running the Pipeline
Run the main script using the standard Python environment:
```powershell
py -3.13 main.py
```
