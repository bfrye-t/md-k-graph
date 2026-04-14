"""
Step 4: The LangGraph Orchestrator

A state machine that orchestrates hybrid retrieval (vector + graph)
and synthesizes strategic answers.

Nodes:
1. Query Analyzer - Rewrites query, extracts entities, classifies query type
2. Vector Search - Finds semantically relevant document chunks
3. Graph Traversal - Expands context via graph relationships (adaptive hops)
4. Synthesize - Generates the final answer with response mode support
"""

import json
from typing import TypedDict, List, Optional, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

import config
from .prompts import (
    QUERY_ANALYZER_SYSTEM,
    QUERY_ANALYZER_HUMAN,
    QUERY_REWRITER_SYSTEM,
    QUERY_REWRITER_HUMAN,
    SYNTHESIZER_SYSTEM,
    SYNTHESIZER_HUMAN,
    RESPONSE_MODE_INSTRUCTIONS,
    HISTORY_SECTION_TEMPLATE,
    ENTITY_EXTRACTOR_SYSTEM,
    ENTITY_EXTRACTOR_HUMAN,
)
from .graph_storage import GraphStorage


# =============================================================================
# Type Definitions
# =============================================================================

class ChatMessage(TypedDict):
    """A single message in the chat history."""
    role: Literal["user", "assistant"]
    content: str


class QueryAnalysis(TypedDict):
    """Results from query analysis."""
    standalone_query: str
    extracted_entities: List[str]
    query_type: Literal["factual", "comparison", "follow_up", "exploratory"]
    requires_history: bool
    user_context: str


class QueryAnalysisOutput(BaseModel):
    """Pydantic model for structured LLM output during query analysis."""
    standalone_query: str = Field(
        description="Rewritten query resolving pronouns and references from chat history"
    )
    extracted_entities: List[str] = Field(
        default_factory=list,
        description="Entity names that might exist in the knowledge graph"
    )
    query_type: Literal["factual", "comparison", "follow_up", "exploratory"] = Field(
        description="Classification of the query type"
    )
    requires_history: bool = Field(
        default=False,
        description="Whether the answer benefits from prior conversation context"
    )
    user_context: str = Field(
        default="",
        description="Verbatim user-provided context (definitions, requirements, structured data) that should be preserved for synthesis"
    )


# =============================================================================
# State Definition
# =============================================================================

class GraphRAGState(TypedDict):
    """State for the GraphRAG agent."""
    # Input
    question: str                           # Original user question
    chat_history: List[ChatMessage]         # Conversation history for multi-turn
    response_mode: Literal["concise", "standard", "detailed"]  # Response verbosity

    # Query Processing
    query_analysis: QueryAnalysis           # Consolidated analysis results
    standalone_query: str                   # Rewritten query (backward compat)
    extracted_entities: List[str]           # Entities from question (backward compat)

    # Retrieval
    semantic_context: List[dict]            # Results from vector search
    graph_context: List[dict]               # Results from graph traversal
    retrieval_boosted: bool                 # Whether semantic retrieval was boosted due to sparse graph

    # Output
    final_answer: str                       # Synthesized answer
    error: Optional[str]                    # Error message if any


# =============================================================================
# LLM Helpers
# =============================================================================

def get_llm():
    """Get the configured LLM instance."""
    if config.LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=config.LLM_MODEL, temperature=0)
    elif config.LLM_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=config.LLM_MODEL, temperature=0)
    else:
        raise ValueError(f"Unsupported LLM provider: {config.LLM_PROVIDER}")


def format_chat_history(history: List[ChatMessage], max_turns: int = 5) -> str:
    """Format chat history for inclusion in prompts."""
    if not history:
        return "(No prior conversation)"

    # Take last N turns
    recent = history[-max_turns * 2:]  # Each turn is user + assistant

    formatted = []
    for msg in recent:
        role = "User" if msg["role"] == "user" else "Assistant"
        # Truncate long messages
        content = msg["content"][:500] + "..." if len(msg["content"]) > 500 else msg["content"]
        formatted.append(f"{role}: {content}")

    return "\n".join(formatted)


# =============================================================================
# Node Functions
# =============================================================================

def _has_structured_content(text: str) -> bool:
    """Check if text contains structured content that should be preserved."""
    indicators = [
        "\n" in text and len(text) > 200,  # Multi-line and substantial
        "- " in text,                       # Bullet points
        "* " in text,                       # Bullet points
        "\n1." in text or text.startswith("1."),  # Numbered lists
        ":" in text and "\n" in text,       # Definitions
        "```" in text,                      # Code blocks
        "|" in text and "-" in text,        # Tables
    ]
    return any(indicators)


def analyze_query(state: GraphRAGState) -> GraphRAGState:
    """
    Node 1: Analyze the user's question for optimal retrieval.

    Consolidates query rewriting and entity extraction into a single LLM call
    using structured output. Also classifies query type and determines if
    history context is needed for the answer.
    """
    llm = get_llm()
    question = state["question"]
    chat_history = state.get("chat_history", [])

    # Format chat history for the prompt
    history_str = format_chat_history(chat_history)

    # Use structured output for consolidated analysis
    structured_llm = llm.with_structured_output(QueryAnalysisOutput)

    messages = [
        SystemMessage(content=QUERY_ANALYZER_SYSTEM),
        HumanMessage(content=QUERY_ANALYZER_HUMAN.format(
            chat_history=history_str,
            question=question,
        )),
    ]

    try:
        result: QueryAnalysisOutput = structured_llm.invoke(messages)

        # For complex prompts with structured content, always preserve the
        # full original question as user_context (don't rely on LLM extraction)
        if _has_structured_content(question):
            user_context = question
        else:
            user_context = result.user_context

        # Populate query_analysis
        state["query_analysis"] = {
            "standalone_query": result.standalone_query,
            "extracted_entities": result.extracted_entities,
            "query_type": result.query_type,
            "requires_history": result.requires_history,
            "user_context": user_context,
        }

        # Backward compatibility fields
        state["standalone_query"] = result.standalone_query
        state["extracted_entities"] = result.extracted_entities

    except Exception as e:
        # Fallback: use original question
        state["query_analysis"] = {
            "standalone_query": question,
            "extracted_entities": [],
            "query_type": "factual",
            "requires_history": False,
            "user_context": "",
        }
        state["standalone_query"] = question
        state["extracted_entities"] = []
        state["error"] = f"Query analysis fallback: {str(e)}"

    return state


def vector_search(state: GraphRAGState, storage: GraphStorage) -> GraphRAGState:
    """
    Node 2: Perform semantic search on document chunks.

    Uses response_mode to determine how many chunks to retrieve.
    """
    query = state["standalone_query"]
    response_mode = state.get("response_mode", "standard")

    # Get adaptive limit based on response mode
    k = config.VECTOR_SEARCH_LIMITS.get(response_mode, 5)

    try:
        results = storage.vector_search(query, k=k)

        # Format results for context
        semantic_context = []
        for doc in results:
            context_item = {
                "text": doc.page_content[:2000],  # Limit text length
                "doc_title": doc.metadata.get("doc_title", ""),
                "h2_header": doc.metadata.get("h2_header", ""),
                "h3_header": doc.metadata.get("h3_header", ""),
                "similarity_score": doc.metadata.get("similarity_score", 0),
            }
            semantic_context.append(context_item)

        state["semantic_context"] = semantic_context

    except Exception as e:
        state["error"] = f"Vector search error: {str(e)}"
        state["semantic_context"] = []

    return state


def graph_traverse(state: GraphRAGState, storage: GraphStorage) -> GraphRAGState:
    """
    Node 3: Traverse the graph from extracted entities and vector results.

    Uses adaptive hop depth and limits based on query type and response mode.
    """
    graph_context = []

    # Get query analysis for adaptive retrieval
    query_analysis = state.get("query_analysis", {})
    query_type = query_analysis.get("query_type", "factual")
    response_mode = state.get("response_mode", "standard")

    # Look up traversal configuration
    traversal_config = config.GRAPH_TRAVERSAL_CONFIG.get(
        (query_type, response_mode),
        config.DEFAULT_GRAPH_TRAVERSAL
    )
    hops = traversal_config["hops"]
    limit = traversal_config["limit"]

    # Collect node IDs to traverse from
    node_ids = []

    # Add extracted entities (with resolution)
    if state.get("extracted_entities"):
        for entity in state["extracted_entities"]:
            # Try to resolve entity to actual graph nodes
            resolved = storage.resolve_entities([entity])
            if resolved:
                # Add high-confidence matches
                for match in resolved:
                    if match.get("confidence", 0) >= 0.5:
                        node_ids.append(match["id"])
            else:
                # Fallback: use entity name directly
                node_ids.append(entity)

    # Also try to find entities matching terms from semantic results
    if state.get("semantic_context"):
        for ctx in state["semantic_context"][:3]:  # Top 3 semantic matches
            # Extract potential entity names from headers
            for key in ["h2_header", "h3_header"]:
                header = ctx.get(key, "")
                if header:
                    # Use resolve_entities for precise matching (avoids description matches)
                    resolved = storage.resolve_entities([header])
                    for match in resolved:
                        if match.get("confidence", 0) >= 0.7:  # Higher threshold for headers
                            node_ids.append(match["id"])

    # Remove duplicates
    node_ids = list(set(node_ids))

    if node_ids:
        try:
            # Perform traversal with adaptive parameters
            traversal_results = storage.graph_traverse(
                node_ids,
                hops=hops,
                limit=limit,
                filter_relationship_types=config.FILTER_RELATIONSHIP_TYPES,
                direction=config.TRAVERSAL_DIRECTION,
            )

            for result in traversal_results:
                if result.get("target"):  # Has a neighbor
                    # Handle both 1-hop (relationship) and 2-hop (relationships array)
                    rel = result.get("relationship")
                    if rel is None:
                        rels = result.get("relationships", [])
                        rel = " -> ".join(rels) if rels else ""

                    context_item = {
                        "source": result.get("source", ""),
                        "relationship": rel,
                        "target": result.get("target", ""),
                        "target_description": result.get("target_description", ""),
                        "target_labels": result.get("target_labels", []),
                    }
                    graph_context.append(context_item)

        except Exception as e:
            state["error"] = f"Graph traversal error: {str(e)}"

    state["graph_context"] = graph_context
    return state


def adaptive_boost(state: GraphRAGState, storage: GraphStorage) -> GraphRAGState:
    """
    Node 3.5: Boost semantic retrieval if graph context is sparse.

    When graph traversal returns few or no relationships, this indicates
    either the query doesn't map well to graph entities or the entities
    are poorly connected. In these cases, we compensate by fetching
    additional semantic chunks to ensure adequate context for synthesis.
    """
    graph_context = state.get("graph_context", [])
    semantic_context = state.get("semantic_context", [])
    response_mode = state.get("response_mode", "standard")

    # Check if graph context is sparse
    is_sparse = len(graph_context) < config.SPARSE_GRAPH_THRESHOLD

    if not is_sparse:
        state["retrieval_boosted"] = False
        return state

    # Calculate how many additional chunks to fetch
    boost_k = config.SEMANTIC_BOOST_LIMITS.get(response_mode, 3)

    # We need to fetch more than our original k to get new results
    original_k = config.VECTOR_SEARCH_LIMITS.get(response_mode, 5)
    new_k = original_k + boost_k

    try:
        query = state["standalone_query"]
        results = storage.vector_search(query, k=new_k)

        # Get existing chunk IDs to avoid duplicates
        existing_texts = {ctx.get("text", "")[:100] for ctx in semantic_context}

        # Add only new chunks
        new_chunks = []
        for doc in results:
            text = doc.page_content[:2000]
            text_preview = text[:100]

            # Skip if we already have this chunk
            if text_preview in existing_texts:
                continue

            context_item = {
                "text": text,
                "doc_title": doc.metadata.get("doc_title", ""),
                "h2_header": doc.metadata.get("h2_header", ""),
                "h3_header": doc.metadata.get("h3_header", ""),
                "similarity_score": doc.metadata.get("similarity_score", 0),
                "boosted": True,  # Mark as boosted for debugging
            }
            new_chunks.append(context_item)

            # Stop when we've added enough
            if len(new_chunks) >= boost_k:
                break

        # Merge boosted chunks with existing context
        if new_chunks:
            state["semantic_context"] = semantic_context + new_chunks
            state["retrieval_boosted"] = True
        else:
            state["retrieval_boosted"] = False

    except Exception as e:
        # Don't fail the pipeline on boost errors, just log and continue
        state["retrieval_boosted"] = False
        if state.get("error"):
            state["error"] += f"; Boost error: {str(e)}"
        else:
            state["error"] = f"Boost error: {str(e)}"

    return state


def synthesize_answer(state: GraphRAGState) -> GraphRAGState:
    """
    Node 4: Synthesize final answer from semantic and graph context.

    Supports response modes (concise/standard/detailed) and includes
    conversation history for coherent follow-ups.
    """
    llm = get_llm()

    # Get response mode instructions
    response_mode = state.get("response_mode", "standard")
    mode_instructions = RESPONSE_MODE_INSTRUCTIONS.get(response_mode, RESPONSE_MODE_INSTRUCTIONS["standard"])

    # Build history section if needed
    query_analysis = state.get("query_analysis", {})
    chat_history = state.get("chat_history", [])
    history_section = ""

    if query_analysis.get("requires_history") and chat_history:
        # Include last 3 turns for context
        history_str = format_chat_history(chat_history, max_turns=3)
        history_section = HISTORY_SECTION_TEMPLATE.format(history=history_str)

    # Build user context section if provided
    user_context = query_analysis.get("user_context", "")
    user_context_section = ""
    if user_context:
        user_context_section = f"=== USER-PROVIDED CONTEXT ===\n{user_context}\n\n"

    # Format semantic context
    semantic_str = ""
    for i, ctx in enumerate(state.get("semantic_context", []), 1):
        header_path = " > ".join(filter(None, [
            ctx.get("doc_title", ""),
            ctx.get("h2_header", ""),
            ctx.get("h3_header", ""),
        ]))
        semantic_str += f"\n[{i}] {header_path}\n{ctx.get('text', '')}\n"

    # Format graph context
    graph_str = ""
    if state.get("graph_context"):
        for ctx in state["graph_context"]:
            labels = ", ".join(ctx.get("target_labels", [])) if ctx.get("target_labels") else "Entity"
            graph_str += f"- ({ctx['source']}) -[{ctx['relationship']}]-> ({ctx['target']} [{labels}])\n"
            if ctx.get("target_description"):
                graph_str += f"  Description: {ctx['target_description']}\n"
    else:
        graph_str = "No graph relationships found for the extracted entities."

    # Generate answer with response mode
    system_prompt = SYNTHESIZER_SYSTEM.format(response_mode_instructions=mode_instructions)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=SYNTHESIZER_HUMAN.format(
            question=state["question"],
            history_section=history_section,
            user_context_section=user_context_section,
            semantic_context=semantic_str or "No semantic matches found.",
            graph_context=graph_str,
        )),
    ]

    response = llm.invoke(messages)
    state["final_answer"] = response.content

    return state


# =============================================================================
# Graph Builder
# =============================================================================

def create_graph_rag_agent(storage: GraphStorage):
    """
    Build and compile the LangGraph state machine.

    Pipeline: analyze_query -> vector_search -> graph_traverse -> adaptive_boost -> synthesize

    The adaptive_boost node compensates for sparse graph results by fetching
    additional semantic context, ensuring adequate information for synthesis.

    Args:
        storage: Initialized GraphStorage instance for database access.

    Returns:
        Compiled LangGraph application.
    """
    # Create the state graph
    workflow = StateGraph(GraphRAGState)

    # Add nodes with storage bound via closures
    workflow.add_node("analyze_query", analyze_query)
    workflow.add_node("vector_search", lambda state: vector_search(state, storage))
    workflow.add_node("graph_traverse", lambda state: graph_traverse(state, storage))
    workflow.add_node("adaptive_boost", lambda state: adaptive_boost(state, storage))
    workflow.add_node("synthesize", synthesize_answer)

    # Define the flow
    workflow.set_entry_point("analyze_query")
    workflow.add_edge("analyze_query", "vector_search")
    workflow.add_edge("vector_search", "graph_traverse")
    workflow.add_edge("graph_traverse", "adaptive_boost")
    workflow.add_edge("adaptive_boost", "synthesize")
    workflow.add_edge("synthesize", END)

    # Compile and return
    return workflow.compile()


def run_query(
    agent,
    question: str,
    chat_history: Optional[List[ChatMessage]] = None,
    response_mode: Literal["concise", "standard", "detailed"] = "standard",
) -> dict:
    """
    Run a query through the agent and return the full state.

    Args:
        agent: Compiled LangGraph agent.
        question: User's question.
        chat_history: Optional list of prior chat messages for multi-turn context.
        response_mode: Response verbosity ("concise", "standard", or "detailed").

    Returns:
        Final state dictionary with all results.
    """
    initial_state = {
        "question": question,
        "chat_history": chat_history or [],
        "response_mode": response_mode,
        "query_analysis": {},
        "standalone_query": "",
        "extracted_entities": [],
        "semantic_context": [],
        "graph_context": [],
        "retrieval_boosted": False,
        "final_answer": "",
        "error": None,
    }

    # Run the graph
    final_state = agent.invoke(initial_state)

    return final_state


# =============================================================================
# CLI Testing
# =============================================================================

if __name__ == "__main__":
    print("Initializing GraphRAG agent...")

    # Connect to storage
    storage = GraphStorage()

    # Ensure vector index exists
    storage.get_vector_store()

    # Create agent
    agent = create_graph_rag_agent(storage)

    # Test single query
    test_question = "What problems do Data Teams experience with their data cloud infrastructure?"

    print(f"\nQuestion: {test_question}")
    print("-" * 50)

    result = run_query(agent, test_question)

    print(f"\nQuery Analysis: {result.get('query_analysis', {})}")
    print(f"Rewritten Query: {result['standalone_query']}")
    print(f"Extracted Entities: {result['extracted_entities']}")
    print(f"Semantic Results: {len(result['semantic_context'])} chunks")
    print(f"Graph Results: {len(result['graph_context'])} relationships")
    print(f"\n=== ANSWER ===\n{result['final_answer']}")

    # Test multi-turn conversation
    print("\n" + "=" * 50)
    print("Testing multi-turn conversation...")
    print("=" * 50)

    history = [
        {"role": "user", "content": test_question},
        {"role": "assistant", "content": result["final_answer"]},
    ]

    follow_up = "How does Tealium solve that?"
    print(f"\nFollow-up: {follow_up}")
    print("-" * 50)

    result2 = run_query(agent, follow_up, chat_history=history)
    print(f"\nQuery Analysis: {result2.get('query_analysis', {})}")
    print(f"Rewritten Query: {result2['standalone_query']}")
    print(f"\n=== ANSWER ===\n{result2['final_answer']}")
