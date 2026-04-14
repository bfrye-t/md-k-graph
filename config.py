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
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5.4")
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

# =============================================================================
# RETRIEVAL CONFIGURATION
# =============================================================================
# Adaptive retrieval parameters based on query type and response mode.

# Vector search limits by response mode
VECTOR_SEARCH_LIMITS = {
    "concise": 3,    # Fewer chunks for brief answers
    "standard": 5,   # Default behavior
    "detailed": 8,   # More chunks for comprehensive answers
}

# Graph traversal config: (query_type, response_mode) -> {hops, limit}
GRAPH_TRAVERSAL_CONFIG = {
    # Factual queries - focused retrieval
    ("factual", "concise"): {"hops": 1, "limit": 10},
    ("factual", "standard"): {"hops": 1, "limit": 25},
    ("factual", "detailed"): {"hops": 1, "limit": 50},
    # Exploratory queries - broader context
    ("exploratory", "concise"): {"hops": 2, "limit": 20},
    ("exploratory", "standard"): {"hops": 2, "limit": 50},
    ("exploratory", "detailed"): {"hops": 2, "limit": 100},
    # Comparison queries - moderate depth, higher limit
    ("comparison", "concise"): {"hops": 1, "limit": 15},
    ("comparison", "standard"): {"hops": 2, "limit": 40},
    ("comparison", "detailed"): {"hops": 2, "limit": 75},
    # Follow-up queries - similar to factual
    ("follow_up", "concise"): {"hops": 1, "limit": 10},
    ("follow_up", "standard"): {"hops": 1, "limit": 25},
    ("follow_up", "detailed"): {"hops": 2, "limit": 50},
}
DEFAULT_GRAPH_TRAVERSAL = {"hops": 1, "limit": 25}

# Whether to filter traversal to only schema-defined relationship types
FILTER_RELATIONSHIP_TYPES = True

# Traversal direction: "bidirectional", "outgoing_only", "incoming_only"
TRAVERSAL_DIRECTION = "bidirectional"
