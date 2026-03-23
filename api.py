"""
FastAPI wrapper for GraphRAG agent.

Exposes the knowledge graph Q&A as a REST API for integration with
Glean MCP, Slack bots, or other services.

Run with: uvicorn api:app --reload --port 8000
"""

from contextlib import asynccontextmanager
from typing import Optional, Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.graph_storage import GraphStorage
from src.agent import create_graph_rag_agent, run_query, ChatMessage


# =============================================================================
# Models
# =============================================================================

class QueryRequest(BaseModel):
    """Request body for /query endpoint."""
    question: str = Field(..., description="The question to ask about Tealium")
    session_id: Optional[str] = Field(
        None,
        description="Session ID for multi-turn conversations. Omit for single queries."
    )
    response_mode: Literal["concise", "standard", "detailed"] = Field(
        "standard",
        description="Response verbosity level"
    )


class QueryResponse(BaseModel):
    """Response from /query endpoint."""
    answer: str = Field(..., description="The generated answer")
    session_id: str = Field(..., description="Session ID for follow-up questions")
    query_analysis: dict = Field(default_factory=dict, description="Query processing details")
    sources: list = Field(default_factory=list, description="Source documents used")


class HealthResponse(BaseModel):
    """Response from /health endpoint."""
    status: str
    graph_stats: dict


# =============================================================================
# Session Management (in-memory for simplicity)
# =============================================================================

# In production, use Redis or a database for session storage
sessions: dict[str, list[ChatMessage]] = {}

MAX_SESSIONS = 1000  # Limit memory usage
MAX_HISTORY_LENGTH = 20  # Max messages per session


def get_or_create_session(session_id: Optional[str]) -> tuple[str, list[ChatMessage]]:
    """Get existing session or create a new one."""
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]

    # Create new session
    new_id = session_id or str(uuid4())

    # Evict oldest session if at capacity
    if len(sessions) >= MAX_SESSIONS:
        oldest = next(iter(sessions))
        del sessions[oldest]

    sessions[new_id] = []
    return new_id, sessions[new_id]


def update_session(session_id: str, question: str, answer: str):
    """Add a Q&A turn to the session history."""
    if session_id not in sessions:
        sessions[session_id] = []

    history = sessions[session_id]
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})

    # Trim if too long
    if len(history) > MAX_HISTORY_LENGTH:
        sessions[session_id] = history[-MAX_HISTORY_LENGTH:]


# =============================================================================
# Application Setup
# =============================================================================

# Global references (initialized on startup)
storage: Optional[GraphStorage] = None
agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup, cleanup on shutdown."""
    global storage, agent

    print("Initializing GraphRAG API...")
    storage = GraphStorage()
    storage.get_vector_store()  # Ensure vector index exists
    agent = create_graph_rag_agent(storage)
    print("GraphRAG API ready.")

    yield

    # Cleanup
    if storage:
        storage.close()
    print("GraphRAG API shutdown.")


app = FastAPI(
    title="Tealium GraphRAG API",
    description="Knowledge graph-powered Q&A about Tealium's strategic positioning",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for browser-based clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Endpoints
# =============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and return graph statistics."""
    if storage is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        stats = storage.get_statistics()
        return HealthResponse(status="healthy", graph_stats=stats)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Ask a question about Tealium.

    Supports multi-turn conversations via session_id. Include the returned
    session_id in subsequent requests to maintain conversation context.
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    # Get or create session
    session_id, chat_history = get_or_create_session(request.session_id)

    try:
        # Run the query through the agent
        result = run_query(
            agent,
            request.question,
            chat_history=chat_history,
            response_mode=request.response_mode,
        )

        answer = result.get("final_answer", "")

        # Update session history
        update_session(session_id, request.question, answer)

        # Format sources from semantic context
        sources = []
        for ctx in result.get("semantic_context", [])[:5]:
            source = {
                "title": ctx.get("doc_title", ""),
                "section": ctx.get("h2_header", "") or ctx.get("h3_header", ""),
            }
            if source["title"] or source["section"]:
                sources.append(source)

        return QueryResponse(
            answer=answer,
            session_id=session_id,
            query_analysis=result.get("query_analysis", {}),
            sources=sources,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear a conversation session."""
    if session_id in sessions:
        del sessions[session_id]
        return {"status": "cleared"}
    raise HTTPException(status_code=404, detail="Session not found")


# =============================================================================
# MCP Tool Definition (for Glean/Claude Code integration)
# =============================================================================

MCP_TOOL_DEFINITION = {
    "name": "tealium_knowledge_graph",
    "description": (
        "Query the Tealium knowledge graph for information about Tealium's "
        "strategic positioning as a Customer Data Platform (CDP). Use this tool "
        "when questions are about: Data Teams, AI Teams, Marketing Teams, "
        "the Activation Gap, Context Gap, Moments API, Real-Time Layer, "
        "Context Engineering, or Tealium product capabilities."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question to ask about Tealium"
            },
            "response_mode": {
                "type": "string",
                "enum": ["concise", "standard", "detailed"],
                "default": "concise",
                "description": "Response verbosity (concise for quick answers)"
            }
        },
        "required": ["question"]
    }
}


@app.get("/mcp/tool-definition")
async def get_mcp_tool_definition():
    """Return the MCP tool definition for this API."""
    return MCP_TOOL_DEFINITION


# =============================================================================
# CLI for testing
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
