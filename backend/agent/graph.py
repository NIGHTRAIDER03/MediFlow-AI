"""LangGraph StateGraph for MediFlow AI agent."""

import os
import time
from typing import TypedDict, Annotated, Optional

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

from agent.prompts import SYSTEM_PROMPT
from agent.tools import (
    log_interaction,
    edit_interaction,
    smart_hcp_search,
    interaction_timeline,
    next_best_action,
    compliance_guardian,
)

load_dotenv()


# ── Agent State ──

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    current_hcp: Optional[dict]
    hcp_memory: dict
    current_interaction: Optional[dict]
    current_follow_up: Optional[dict]
    conversation_context: list[str]
    workflow_stage: str
    user_id: int


# ── Tools ──

ALL_TOOLS = [
    log_interaction,
    edit_interaction,
    smart_hcp_search,
    interaction_timeline,
    next_best_action,
    compliance_guardian,
]


# ── LLM ──

def get_llm():
    """Initialize Groq LLM with tools bound."""
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        max_tokens=2048,
        api_key=os.getenv("GROQ_API_KEY"),
    )
    return llm.bind_tools(ALL_TOOLS, parallel_tool_calls=False)


# ── Graph Nodes ──

def agent_node(state: AgentState):
    """Main agent node — calls the LLM with system prompt and conversation history."""
    llm = get_llm()

    messages = state["messages"]

    # Inject system prompt if not present
    if not messages or not isinstance(messages[0], SystemMessage):
        # Build enhanced system prompt with context
        context_parts = [SYSTEM_PROMPT]

        if state.get("current_hcp"):
            hcp = state["current_hcp"]
            context_parts.append(
                f"\n\nCurrent HCP in context: {hcp.get('name', 'Unknown')} "
                f"({hcp.get('specialty', '')}, {hcp.get('institution', '')}). "
                f"Relationship score: {hcp.get('relationship_score', 'N/A')}."
            )

        if state.get("hcp_memory"):
            mem = state["hcp_memory"]
            context_parts.append(
                f"\nHCP Memory: Last product: {mem.get('last_product_discussed', 'N/A')}, "
                f"Buying interest: {mem.get('buying_interest', 'N/A')}, "
                f"Typical objections: {', '.join(mem.get('typical_objections', []))}, "
                f"Engagement trend: {mem.get('engagement_trend', 'N/A')}."
            )

        if state.get("conversation_context"):
            context_parts.append(
                "\nConversation context so far: "
                + "; ".join(state["conversation_context"][-5:])
            )

        system_msg = SystemMessage(content="\n".join(context_parts))
        messages = [system_msg] + list(messages)

    response = llm.invoke(messages)

    return {"messages": [response]}


def should_continue(state: AgentState):
    """Determine if we should call tools or end."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# ── Build Graph ──

def build_graph():
    """Build and compile the LangGraph StateGraph."""
    tool_node = ToolNode(ALL_TOOLS)

    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    # Set entry point
    graph.set_entry_point("agent")

    # Add edges
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    # Compile with checkpointer
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


# ── Singleton ──

_graph = None


def get_graph():
    """Get or create the compiled graph singleton."""
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


async def invoke_agent(message: str, thread_id: str, user_id: int = 1) -> dict:
    """Invoke the agent with a user message and return the response.
    
    Returns:
        dict with keys: response (str), tool_calls (list), elapsed_time (float)
    """
    graph = get_graph()
    start_time = time.time()

    config = {"configurable": {"thread_id": thread_id}}

    input_state = {
        "messages": [HumanMessage(content=message)],
        "current_hcp": None,
        "hcp_memory": {},
        "current_interaction": None,
        "current_follow_up": None,
        "conversation_context": [],
        "workflow_stage": "idle",
        "user_id": user_id,
    }

    result = await graph.ainvoke(input_state, config=config)

    elapsed = round(time.time() - start_time, 2)

    # Extract response and tool calls
    messages = result["messages"]
    response_text = ""
    tool_calls_made = []

    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            if msg.content and not response_text:
                response_text = msg.content
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                tool_calls_made.extend(msg.tool_calls)

    # Extract tool results
    tool_results = []
    for msg in messages:
        if hasattr(msg, "type") and msg.type == "tool":
            tool_results.append({
                "tool_name": msg.name,
                "result": msg.content,
            })

    return {
        "response": response_text,
        "tool_calls": [
            {"name": tc["name"], "args": tc.get("args", {})}
            for tc in tool_calls_made
        ],
        "tool_results": tool_results,
        "elapsed_time": elapsed,
        "model": "llama-3.1-8b-instant",
    }
