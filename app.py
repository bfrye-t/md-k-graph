"""
Step 5: Streamlit Interface

A chat interface for querying the GraphRAG knowledge base.
Supports multi-turn conversations with response mode selection.
"""

import streamlit as st

from src.graph_storage import GraphStorage
from src.agent import create_graph_rag_agent, run_query


# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="Tealium Knowledge Graph",
    page_icon="🔗",
    layout="wide",
)

st.title("🔗 Tealium GraphRAG Assistant")
st.markdown("""
Ask questions about Tealium's strategic positioning as a **connective layer**
for Data, AI, and Marketing teams. The assistant uses hybrid retrieval
(semantic search + knowledge graph traversal) to provide contextual answers.
""")


# =============================================================================
# Initialize Components (cached)
# =============================================================================

@st.cache_resource
def init_storage():
    """Initialize Neo4j connection (cached across reruns)."""
    try:
        storage = GraphStorage()
        # Ensure vector store is initialized
        storage.get_vector_store()
        return storage
    except Exception as e:
        st.error(f"Failed to connect to Neo4j: {e}")
        st.info("Make sure your `.env` file contains valid Neo4j credentials.")
        return None


@st.cache_resource
def init_agent(_storage):
    """Initialize the LangGraph agent (cached across reruns)."""
    if _storage is None:
        return None
    return create_graph_rag_agent(_storage)


# Initialize
storage = init_storage()
agent = init_agent(storage)


# =============================================================================
# Sidebar - Settings & Database Info
# =============================================================================

with st.sidebar:
    st.header("⚙️ Settings")

    # Response mode selector
    response_mode = st.radio(
        "Response Mode",
        ["concise", "standard", "detailed"],
        index=1,
        help="Controls response length: concise (2-4 sentences), standard (1-2 paragraphs), detailed (comprehensive)"
    )

    # Store in session state for persistence
    st.session_state.response_mode = response_mode

    st.markdown("---")
    st.header("📊 Knowledge Graph Stats")

    if storage:
        try:
            stats = storage.get_statistics()
            st.metric("Total Nodes", stats["total_nodes"])
            st.metric("Total Relationships", stats["total_relationships"])

            with st.expander("Node Types"):
                for label, count in sorted(stats["node_types"].items(), key=lambda x: -x[1]):
                    st.write(f"**{label}**: {count}")

            with st.expander("Relationship Types"):
                for rel_type, count in sorted(stats["relationship_types"].items(), key=lambda x: -x[1]):
                    st.write(f"**{rel_type}**: {count}")

        except Exception as e:
            st.warning(f"Could not load stats: {e}")

    st.markdown("---")
    st.header("💡 Example Questions")
    example_questions = [
        "What problems do Data Teams experience?",
        "How does Tealium solve the Context Gap for AI?",
        "What is the Moments API and what does it enable?",
        "How does the Real-Time Layer work?",
        "What causes fragmentation in Marketing execution?",
    ]
    for q in example_questions:
        if st.button(q, key=q):
            st.session_state.user_input = q

    # Clear conversation button
    st.markdown("---")
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()


# =============================================================================
# Helper Functions
# =============================================================================

def build_chat_history():
    """Build chat history from session state for the agent."""
    if "messages" not in st.session_state:
        return []

    history = []
    for msg in st.session_state.messages:
        history.append({
            "role": msg["role"],
            "content": msg["content"],
        })
    return history


# =============================================================================
# Chat Interface
# =============================================================================

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show debug info in expander for assistant messages
        if message["role"] == "assistant" and "debug" in message:
            with st.expander("🔍 Retrieval Details"):
                debug = message["debug"]

                # Show query analysis if available
                query_analysis = debug.get("query_analysis", {})
                if query_analysis:
                    st.write(f"**Query Type:** {query_analysis.get('query_type', 'N/A')}")
                    st.write(f"**Requires History:** {query_analysis.get('requires_history', False)}")

                st.write(f"**Rewritten Query:** {debug.get('standalone_query', 'N/A')}")

                # Show preserved user context if present
                user_context = query_analysis.get("user_context", "") if query_analysis else ""
                if user_context:
                    with st.expander("User-Provided Context (preserved)"):
                        st.text(user_context[:2000] + ("..." if len(user_context) > 2000 else ""))

                st.write(f"**Extracted Entities:** {debug.get('extracted_entities', [])}")
                st.write(f"**Semantic Results:** {len(debug.get('semantic_context', []))} chunks")
                st.write(f"**Graph Results:** {len(debug.get('graph_context', []))} relationships")

                if debug.get("graph_context"):
                    st.write("**Graph Relationships:**")
                    for ctx in debug["graph_context"][:10]:
                        st.code(f"({ctx['source']}) -[{ctx['relationship']}]-> ({ctx['target']})")


# Chat input
user_input = st.chat_input("Ask a question about Tealium...")

# Handle example question button clicks
if "user_input" in st.session_state:
    user_input = st.session_state.user_input
    del st.session_state.user_input

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response
    with st.chat_message("assistant"):
        if agent is None:
            st.error("Agent not initialized. Please check your configuration.")
        else:
            with st.spinner("Thinking..."):
                try:
                    # Build chat history from prior messages (excluding current)
                    chat_history = build_chat_history()[:-1]  # Exclude the just-added user message

                    # Get response mode from session state
                    response_mode = st.session_state.get("response_mode", "standard")

                    # Run the query through the agent with history and response mode
                    result = run_query(
                        agent,
                        user_input,
                        chat_history=chat_history,
                        response_mode=response_mode,
                    )

                    # Display the answer
                    st.markdown(result["final_answer"])

                    # Show retrieval details
                    with st.expander("🔍 Retrieval Details"):
                        # Show query analysis
                        query_analysis = result.get("query_analysis", {})
                        if query_analysis:
                            st.write(f"**Query Type:** {query_analysis.get('query_type', 'N/A')}")
                            st.write(f"**Requires History:** {query_analysis.get('requires_history', False)}")

                        st.write(f"**Rewritten Query:** {result.get('standalone_query', 'N/A')}")

                        # Show preserved user context if present
                        user_context = query_analysis.get("user_context", "") if query_analysis else ""
                        if user_context:
                            with st.expander("User-Provided Context (preserved)"):
                                st.text(user_context[:2000] + ("..." if len(user_context) > 2000 else ""))

                        st.write(f"**Extracted Entities:** {result.get('extracted_entities', [])}")
                        st.write(f"**Semantic Results:** {len(result.get('semantic_context', []))} chunks")
                        st.write(f"**Graph Results:** {len(result.get('graph_context', []))} relationships")

                        if result.get("graph_context"):
                            st.write("**Graph Relationships:**")
                            for ctx in result["graph_context"][:10]:
                                st.code(f"({ctx['source']}) -[{ctx['relationship']}]-> ({ctx['target']})")

                    # Store in history with debug info
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["final_answer"],
                        "debug": {
                            "query_analysis": result.get("query_analysis"),
                            "standalone_query": result.get("standalone_query"),
                            "extracted_entities": result.get("extracted_entities"),
                            "semantic_context": result.get("semantic_context"),
                            "graph_context": result.get("graph_context"),
                        }
                    })

                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                    })


# =============================================================================
# Footer
# =============================================================================

st.markdown("---")
st.caption("Built with LangChain, LangGraph, Neo4j, and Streamlit")
