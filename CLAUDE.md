# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **GraphRAG MVP** that parses strategic Product Marketing markdown files about Tealium and converts them into a Knowledge Graph using Neo4j. A LangGraph-powered agent queries the graph using hybrid retrieval (semantic search + graph traversal).

Tealium is positioned as a "connective layer" solving fragmented execution across Data, AI, and Marketing teams.

## Tech Stack

- **Python 3.14+**
- **LangChain / LangGraph** - Agent orchestration and graph extraction
- **Neo4j AuraDB** - Graph database with vector search capabilities
- **OpenAI** - LLM for extraction and embeddings (gpt-4o, text-embedding-3-small)
- **Streamlit** - Chat interface

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Markdown Files │────▶│  LLM Extraction  │────▶│  Neo4j Graph    │
│  (product docs) │     │  (LLMGraphTransf)│     │  + Vector Index │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
┌─────────────────┐     ┌──────────────────┐              │
│  Streamlit UI   │◀────│  LangGraph Agent │◀─────────────┘
│  (chat interface)     │  (4-node pipeline)│
└─────────────────┘     └──────────────────┘
```

## Knowledge Graph Schema (Ontology)

**Node Types:**
- `Stakeholder` - Data Teams, AI Teams, Marketing Teams
- `CoreProblem` - The Activation Gap, Context Gap, Latency Problem, etc.
- `StrategicConcept` - Composability, Real-Time Activation, Context Engineering
- `SolutionDimension` - Real-Time Layer, Context Layer, Orchestration Layer
- `ProductFeature` - Moments API, Living Customer Profiles, Event Streaming

**Relationship Types:**
- `EXPERIENCES` - Stakeholder → CoreProblem
- `CAUSES` - CoreProblem → CoreProblem
- `SOLVES` - ProductFeature → CoreProblem
- `ENABLES` - SolutionDimension → StrategicConcept
- `CONTAINS` - SolutionDimension → ProductFeature
- `ADDRESSES` - SolutionDimension → CoreProblem

## File Structure

```
md-k-graph/
├── config.py               # Configuration, schema ontology, env loading
├── app.py                  # Streamlit chat interface
├── src/
│   ├── ingestion.py        # Markdown loading & header-based chunking
│   ├── graph_extraction.py # LLMGraphTransformer with strict schema
│   ├── graph_storage.py    # Neo4j connection, loading, vector indexing
│   ├── manifest.py         # Change detection for incremental updates
│   ├── agent.py            # LangGraph state machine (4 nodes)
│   └── prompts.py          # System prompts for rewriting & synthesis
├── scripts/
│   └── build_graph.py      # Graph building script (supports incremental updates)
└── product md files/       # Source strategic documents
```

## Common Commands

### Setup
```bash
python3 -m pip install -r requirements.txt
cp .env.example .env  # Then edit with your credentials
```

### Build the Knowledge Graph
```bash
python3 scripts/build_graph.py              # Incremental update (default)
python3 scripts/build_graph.py --dry-run    # Preview changes without applying
python3 scripts/build_graph.py --full       # Force full rebuild
python3 scripts/build_graph.py --clear      # Clear database and rebuild
```

Options:
- `--dry-run` - Show what would change without making changes
- `--full` - Force full rebuild (ignore manifest)
- `--clear` - Clear database before loading (implies --full)
- `--skip-extraction` - Skip LLM extraction (just load chunks for vector search)
- `--batch-size N` - Batch size for LLM extraction (default: 3)

**Incremental Updates:** The build script uses a manifest (`.manifest.json`) to track processed files via SHA256 content hashing. Only new or modified files are re-processed.

### Run the Streamlit App
```bash
python3 -m streamlit run app.py
```

### Test Neo4j Connection
```bash
python3 -c "from src.graph_storage import GraphStorage; s = GraphStorage(); print(s.get_statistics())"
```

### Test Ingestion Pipeline
```bash
python3 -c "from src.ingestion import load_markdown_files, chunk_documents; docs = load_markdown_files(); chunks = chunk_documents(docs); print(f'{len(chunks)} chunks')"
```

## LangGraph Agent Pipeline

The agent (`src/agent.py`) is a 4-node state machine:

1. **rewrite_query** - Rewrites user question for optimal retrieval, extracts entity mentions
2. **vector_search** - Semantic search on Document nodes via Neo4j vector index
3. **graph_traverse** - 1-hop Cypher traversal from matched entities to find relationships
4. **synthesize** - Combines semantic + graph context to generate final answer

**State Definition:**
```python
class GraphRAGState(TypedDict):
    question: str              # Original user question
    standalone_query: str      # Rewritten query for retrieval
    extracted_entities: List[str]
    semantic_context: List[dict]
    graph_context: List[dict]
    final_answer: str
```

## Environment Variables

Required in `.env`:
```
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
```

## Key Implementation Details

- **Chunking**: Uses `MarkdownHeaderTextSplitter` to split on `#`, `##`, `###` headers, preserving document structure
- **Schema Enforcement**: `LLMGraphTransformer` with `strict_mode=True` and explicit `allowed_nodes`/`allowed_relationships`
- **Hybrid Retrieval**: Vector search finds semantically similar chunks, then Cypher expands to neighboring graph nodes
- **Dual Attribute Model**: High-frequency attributes in Neo4j, enrichment from warehouse via API (conceptually)
- **Incremental Updates**: Manifest-based change detection using SHA256 content hashing; only new/modified files are re-processed
- **Stable Chunk IDs**: Content-based chunk IDs (format: `doc{N}_{hash8}`) that are deterministic across runs

## Troubleshooting

**SSL Certificate Errors with Neo4j:**
```bash
/Applications/Python\ 3.14/Install\ Certificates.command
```

**Database not found error:**
- Ensure `NEO4J_DATABASE` matches your AuraDB instance ID (visible in console)

**Pydantic warnings with Python 3.14:**
- These are cosmetic warnings from langchain_core, can be ignored
