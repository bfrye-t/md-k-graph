"""
Configuration and constants for the GraphRAG pipeline.
Loads environment variables and defines the knowledge graph schema.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")  # AuraDB uses instance ID as database name

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# Source documents path
MARKDOWN_DIR = os.path.join(os.path.dirname(__file__), "product md files")

# =============================================================================
# KNOWLEDGE GRAPH SCHEMA (Ontology)
# =============================================================================
# This strict schema prevents the LLM from hallucinating arbitrary node/edge types.

ALLOWED_NODES = [
    "Stakeholder",       # e.g., "Data Teams", "AI Teams", "Marketing Teams"
    "CoreProblem",       # e.g., "The Activation Gap", "The Context Gap"
    "StrategicConcept",  # e.g., "Composability", "Real-Time Activation", "Context Engineering"
    "SolutionDimension", # e.g., "Real-Time Layer", "Context Layer", "Orchestration Layer"
    "ProductFeature",    # e.g., "Moments API", "Living Customer Profiles", "Event Streaming"
]

ALLOWED_RELATIONSHIPS = [
    "EXPERIENCES",  # Stakeholder -> CoreProblem (e.g., Data Teams EXPERIENCES Activation Gap)
    "CAUSES",       # CoreProblem -> CoreProblem (e.g., Latency Problem CAUSES Stale Data)
    "SOLVES",       # ProductFeature -> CoreProblem (e.g., Moments API SOLVES Context Gap)
    "ENABLES",      # SolutionDimension -> StrategicConcept (e.g., Real-Time Layer ENABLES Real-Time Activation)
    "CONTAINS",     # SolutionDimension -> ProductFeature (e.g., Context Layer CONTAINS Moments API)
    "ADDRESSES",    # SolutionDimension -> CoreProblem (e.g., Orchestration Layer ADDRESSES Fragmentation)
]

# Vector index configuration
VECTOR_INDEX_NAME = "document_embeddings"
VECTOR_DIMENSION = 1536  # OpenAI text-embedding-3-small dimension
NODE_LABEL_FOR_VECTORS = "Document"  # We'll also embed chunk nodes
