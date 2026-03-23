# GraphRAG MVP

A knowledge graph-powered RAG system for querying strategic product documentation using hybrid retrieval (semantic search + graph traversal).

![Python](https://img.shields.io/badge/Python-3.14+-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-green)
![Neo4j](https://img.shields.io/badge/Neo4j-AuraDB-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-1.37+-red)

## Overview

This project parses strategic Product Marketing markdown files and converts them into a Knowledge Graph, then provides a chat interface to query the graph using a LangGraph agent.

**Key Features:**
- **Structured Extraction**: LLM extracts entities and relationships following a strict ontology
- **Hybrid Retrieval**: Combines vector similarity search with graph traversal
- **Interactive Chat**: Streamlit UI with retrieval transparency (shows query rewriting, entities, relationships)

## Architecture

```
Markdown Files → LLM Extraction → Neo4j Graph + Vector Index
                                           ↓
Streamlit UI ← LangGraph Agent ← Hybrid Retrieval
```

**LangGraph Pipeline:**
1. **Query Rewriter** - Optimizes question for retrieval
2. **Vector Search** - Finds semantically similar document chunks
3. **Graph Traversal** - Expands context via relationship hops
4. **Synthesizer** - Generates answer from combined context

## Knowledge Graph Schema

| Node Type | Examples |
|-----------|----------|
| Stakeholder | Data Teams, AI Teams, Marketing Teams |
| CoreProblem | Activation Gap, Context Gap, Latency Problem |
| StrategicConcept | Composability, Real-Time Activation |
| SolutionDimension | Real-Time Layer, Context Layer |
| ProductFeature | Moments API, Living Customer Profiles |

| Relationship | Pattern |
|--------------|---------|
| EXPERIENCES | Stakeholder → CoreProblem |
| CAUSES | CoreProblem → CoreProblem |
| SOLVES | ProductFeature → CoreProblem |
| ENABLES | SolutionDimension → StrategicConcept |

## Quick Start

### 1. Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=your-database
OPENAI_API_KEY=sk-...
```

**Neo4j**: Get a free AuraDB instance at [console.neo4j.io](https://console.neo4j.io)

### 3. Build the Knowledge Graph

```bash
python3 scripts/build_graph.py
```

This will:
- Load and chunk markdown files (by headers)
- Extract entities/relationships via LLM
- Load graph into Neo4j
- Create vector embeddings

**Incremental Updates:** After the initial build, running `build_graph.py` again will only process new or modified files:

```bash
# Preview what would change
python3 scripts/build_graph.py --dry-run

# Force full rebuild (ignore manifest)
python3 scripts/build_graph.py --full

# Clear database and rebuild
python3 scripts/build_graph.py --clear
```

The system uses SHA256 content hashing to detect changes, so only modified files trigger re-extraction.

### 4. Run the Chat Interface

```bash
python3 -m streamlit run app.py
```

Open http://localhost:8501

## Example Questions

- "What problems do Data Teams experience?"
- "How does Tealium solve the Context Gap for AI?"
- "What is the Moments API and what does it enable?"
- "What causes fragmentation in Marketing execution?"
- "How does the Real-Time Layer work?"

## Project Structure

```
├── app.py                  # Streamlit chat interface
├── config.py               # Configuration and schema
├── src/
│   ├── ingestion.py        # Markdown loading & chunking
│   ├── graph_extraction.py # LLM graph extraction
│   ├── graph_storage.py    # Neo4j operations
│   ├── manifest.py         # Change detection for incremental updates
│   ├── agent.py            # LangGraph agent
│   └── prompts.py          # LLM prompts
├── scripts/
│   └── build_graph.py      # Graph building script (supports incremental)
└── product md files/       # Source documents
```

## Tech Stack

- **LangChain** - Document processing & LLM integration
- **LangGraph** - Agent orchestration
- **Neo4j** - Graph database with vector search
- **OpenAI** - GPT-4o for extraction, text-embedding-3-small for vectors
- **Streamlit** - Web interface

## License

MIT
