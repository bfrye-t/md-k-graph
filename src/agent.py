"""
Step 4: The LangGraph Orchestrator

A state machine that orchestrates hybrid retrieval (vector + graph)
and synthesizes strategic answers.

Nodes:
1. Query Rewriter - Optimizes the user question for retrieval
2. Vector Search - Finds semantically relevant document chunks
3. Graph Traversal - Expands context via graph relationships
4. Synthesize - Generates the final answer
"""

import json
from typing import TypedDict, List, Optional, Annotated

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END

import config
from .prompts import (
    QUERY_REWRITER_SYSTEM,
    QUERY_REWRITER_HUMAN,
    SYNTHESIZER_SYSTEM,
    SYNTHESIZER_HUMAN,
    ENTITY_EXTRACTOR_SYSTEM,
    ENTITY_EXTRACTOR_HUMAN,
)
from .graph_storage import GraphStorage


# =============================================================================
# State Definition
# =============================================================================

class GraphRAGState(TypedDict):
    """State for the GraphRAG agent."""
    question: str                           # Original user question
    standalone_query: str                   # Rewritten query for retrieval
    extracted_entities: List[str]           # Entities extracted from question
    semantic_context: List[dict]            # Results from vector search
    graph_context: List[dict]               # Results from graph traversal
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


# =============================================================================
# Node Functions
# =============================================================================

def rewrite_query(state: GraphRAGState) -> GraphRAGState:
    """
    Node 1: Rewrite the user's question for optimal retrieval.
    Also extracts entity mentions for graph lookup.
    """
    llm = get_llm()
    question = state["question"]

    # Rewrite query for vector search
    rewrite_messages = [
        SystemMessage(content=QUERY_REWRITER_SYSTEM),
        HumanMessage(content=QUERY_REWRITER_HUMAN.format(question=question)),
    ]
    rewritten = llm.invoke(rewrite_messages)
    state["standalone_query"] = rewritten.content.strip()

    # Extract entities for graph lookup
    extract_messages = [
        SystemMessage(content=ENTITY_EXTRACTOR_SYSTEM),
        HumanMessage(content=ENTITY_EXTRACTOR_HUMAN.format(question=question)),
    ]
    extracted = llm.invoke(extract_messages)

    try:
        # Parse JSON array of entities
        entities = json.loads(extracted.content.strip())
        state["extracted_entities"] = entities if isinstance(entities, list) else []
    except json.JSONDecodeError:
        state["extracted_entities"] = []

    return state


def vector_search(state: GraphRAGState, storage: GraphStorage) -> GraphRAGState:
    """
    Node 2: Perform semantic search on document chunks.
    """
    query = state["standalone_query"]

    try:
        results = storage.vector_search(query, k=5)

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
    """
    graph_context = []

    # Collect node IDs to traverse from
    node_ids = []

    # Add extracted entities
    if state.get("extracted_entities"):
        node_ids.extend(state["extracted_entities"])

    # Also try to find entities matching terms from semantic results
    if state.get("semantic_context"):
        for ctx in state["semantic_context"][:3]:  # Top 3 semantic matches
            # Extract potential entity names from headers
            for key in ["h2_header", "h3_header"]:
                header = ctx.get(key, "")
                if header:
                    # Search for matching entities
                    matches = storage.get_entity_by_text(header, limit=2)
                    node_ids.extend([m["id"] for m in matches])

    # Remove duplicates
    node_ids = list(set(node_ids))

    if node_ids:
        try:
            # Perform 1-hop traversal
            traversal_results = storage.graph_traverse(node_ids, hops=1)

            for result in traversal_results:
                if result.get("target"):  # Has a neighbor
                    context_item = {
                        "source": result.get("source", ""),
                        "relationship": result.get("relationship", ""),
                        "target": result.get("target", ""),
                        "target_description": result.get("target_description", ""),
                        "target_labels": result.get("target_labels", []),
                    }
                    graph_context.append(context_item)

        except Exception as e:
            state["error"] = f"Graph traversal error: {str(e)}"

    state["graph_context"] = graph_context
    return state


def synthesize_answer(state: GraphRAGState) -> GraphRAGState:
    """
    Node 4: Synthesize final answer from semantic and graph context.
    """
    llm = get_llm()

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

    # Generate answer
    messages = [
        SystemMessage(content=SYNTHESIZER_SYSTEM),
        HumanMessage(content=SYNTHESIZER_HUMAN.format(
            question=state["question"],
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

    Args:
        storage: Initialized GraphStorage instance for database access.

    Returns:
        Compiled LangGraph application.
    """
    # Create the state graph
    workflow = StateGraph(GraphRAGState)

    # Add nodes with storage bound via closures
    workflow.add_node("rewrite_query", rewrite_query)
    workflow.add_node("vector_search", lambda state: vector_search(state, storage))
    workflow.add_node("graph_traverse", lambda state: graph_traverse(state, storage))
    workflow.add_node("synthesize", synthesize_answer)

    # Define the flow
    workflow.set_entry_point("rewrite_query")
    workflow.add_edge("rewrite_query", "vector_search")
    workflow.add_edge("vector_search", "graph_traverse")
    workflow.add_edge("graph_traverse", "synthesize")
    workflow.add_edge("synthesize", END)

    # Compile and return
    return workflow.compile()


def run_query(agent, question: str) -> dict:
    """
    Run a query through the agent and return the full state.

    Args:
        agent: Compiled LangGraph agent.
        question: User's question.

    Returns:
        Final state dictionary with all results.
    """
    initial_state = {
        "question": question,
        "standalone_query": "",
        "extracted_entities": [],
        "semantic_context": [],
        "graph_context": [],
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

    # Test query
    test_question = "What problems do Data Teams experience with their data cloud infrastructure?"

    print(f"\nQuestion: {test_question}")
    print("-" * 50)

    result = run_query(agent, test_question)

    print(f"\nRewritten Query: {result['standalone_query']}")
    print(f"Extracted Entities: {result['extracted_entities']}")
    print(f"Semantic Results: {len(result['semantic_context'])} chunks")
    print(f"Graph Results: {len(result['graph_context'])} relationships")
    print(f"\n=== ANSWER ===\n{result['final_answer']}")
