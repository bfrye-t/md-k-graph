"""
MCP (Model Context Protocol) server for the Tealium Knowledge Graph.

This allows AI assistants (Glean, Claude Code, etc.) to query the knowledge
graph directly via the MCP standard.

Run with: python mcp_server.py

For Claude Code integration, add to your MCP config:
{
  "mcpServers": {
    "tealium-knowledge": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
"""

import sys
import json
from typing import Any

from src.graph_storage import GraphStorage
from src.agent import create_graph_rag_agent, run_query


# =============================================================================
# MCP Protocol Implementation (stdio-based)
# =============================================================================

class MCPServer:
    """Simple MCP server using stdio transport."""

    def __init__(self):
        self.storage = None
        self.agent = None
        self.initialized = False

    def initialize(self):
        """Initialize the GraphRAG components."""
        if self.initialized:
            return

        self.storage = GraphStorage()
        self.storage.get_vector_store()
        self.agent = create_graph_rag_agent(self.storage)
        self.initialized = True

    def handle_request(self, request: dict) -> dict:
        """Handle an MCP request and return a response."""
        method = request.get("method", "")
        req_id = request.get("id")

        if method == "initialize":
            return self._handle_initialize(req_id, request.get("params", {}))
        elif method == "tools/list":
            return self._handle_tools_list(req_id)
        elif method == "tools/call":
            return self._handle_tools_call(req_id, request.get("params", {}))
        elif method == "shutdown":
            return self._handle_shutdown(req_id)
        else:
            return self._error_response(req_id, -32601, f"Unknown method: {method}")

    def _handle_initialize(self, req_id: Any, params: dict) -> dict:
        """Handle initialize request."""
        try:
            self.initialize()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "tealium-knowledge-graph",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {}
                    }
                }
            }
        except Exception as e:
            return self._error_response(req_id, -32000, f"Initialization failed: {str(e)}")

    def _handle_tools_list(self, req_id: Any) -> dict:
        """Return available tools."""
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "query_tealium_knowledge",
                        "description": (
                            "Query the Tealium knowledge graph for information about "
                            "Tealium's strategic positioning as a Customer Data Platform (CDP). "
                            "Use for questions about: Data Teams, AI Teams, Marketing Teams, "
                            "the Activation Gap, Context Gap, Latency Problem, Moments API, "
                            "Real-Time Layer, Context Layer, Orchestration Layer, "
                            "Context Engineering, Composability, or Tealium product features."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "question": {
                                    "type": "string",
                                    "description": "The question to ask about Tealium"
                                },
                                "detail_level": {
                                    "type": "string",
                                    "enum": ["concise", "standard", "detailed"],
                                    "default": "concise",
                                    "description": "How detailed the response should be"
                                }
                            },
                            "required": ["question"]
                        }
                    }
                ]
            }
        }

    def _handle_tools_call(self, req_id: Any, params: dict) -> dict:
        """Execute a tool call."""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name != "query_tealium_knowledge":
            return self._error_response(req_id, -32602, f"Unknown tool: {tool_name}")

        try:
            # Ensure initialized
            self.initialize()

            question = arguments.get("question", "")
            detail_level = arguments.get("detail_level", "concise")

            if not question:
                return self._error_response(req_id, -32602, "Missing required parameter: question")

            # Run the query
            result = run_query(
                self.agent,
                question,
                chat_history=[],  # MCP calls are typically stateless
                response_mode=detail_level,
            )

            answer = result.get("final_answer", "No answer generated")

            # Format sources
            sources = []
            for ctx in result.get("semantic_context", [])[:3]:
                title = ctx.get("doc_title", "")
                section = ctx.get("h2_header", "") or ctx.get("h3_header", "")
                if title or section:
                    sources.append(f"{title} > {section}" if title and section else title or section)

            # Build response text
            response_text = answer
            if sources:
                response_text += f"\n\nSources: {', '.join(sources)}"

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": response_text
                        }
                    ]
                }
            }

        except Exception as e:
            return self._error_response(req_id, -32000, f"Query failed: {str(e)}")

    def _handle_shutdown(self, req_id: Any) -> dict:
        """Handle shutdown request."""
        if self.storage:
            self.storage.close()
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": None
        }

    def _error_response(self, req_id: Any, code: int, message: str) -> dict:
        """Build an error response."""
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": code,
                "message": message
            }
        }

    def run(self):
        """Run the server, reading from stdin and writing to stdout."""
        # Log to stderr to avoid interfering with protocol
        print("Tealium Knowledge Graph MCP server starting...", file=sys.stderr)

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError as e:
                error = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
                }
                print(json.dumps(error), flush=True)
            except Exception as e:
                print(f"Server error: {e}", file=sys.stderr)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    server = MCPServer()
    server.run()
