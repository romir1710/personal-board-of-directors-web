"""
graph.py — LangGraph state machine: The Personal Board of Directors.

Flow:
  user_input
      │
      ├──► visionary_node  ──┐
      ├──► pragmatist_node ──┼──► chairperson_node ──► END
      └──► advocate_node   ──┘

The three analyst nodes run sequentially (LangGraph does not yet support
native fan-out without Send API), but they operate independently on the raw
user_input so they do NOT influence each other — preserving intellectual
independence.
"""

from __future__ import annotations

from datetime import datetime
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from llm_factory import build_llm
from prompts import (
    CHAIRPERSON_SYSTEM_PROMPT,
    DEVIL_ADVOCATE_SYSTEM_PROMPT,
    PRAGMATIST_SYSTEM_PROMPT,
    VISIONARY_SYSTEM_PROMPT,
)

# ── State schema ───────────────────────────────────────────────────────────────

class BoardState(TypedDict):
    user_input: str
    conversation_history: str   # accumulated prior turns, empty string on first question
    visionary_response: str
    pragmatist_response: str
    advocate_response: str
    final_resolution: str


# ── Shared LLM instance ────────────────────────────────────────────────────────

_llm = build_llm(temperature=0.7)


def _invoke(system_prompt: str, user_message: str) -> str:
    """Call the LLM with a system prompt + user message and return the text."""
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]
    response = _llm.invoke(messages)
    return str(response.content).strip()


def _build_user_message(state: BoardState) -> str:
    """
    Prepend conversation history to the current user_input so every node
    has full session context. On the first question history is empty so
    this is a no-op.
    """
    history = (state.get("conversation_history") or "").strip()
    current = state["user_input"].strip()
    if history:
        return (
            f"[CONVERSATION HISTORY — earlier turns in this session]\n"
            f"{history}\n\n"
            f"[NEW QUESTION — respond to this in the context of the above]\n"
            f"{current}"
        )
    return current


# ── Board member nodes ─────────────────────────────────────────────────────────

def visionary_node(state: BoardState) -> dict:
    """The Visionary — ambition, scale, creative potential."""
    current_date = datetime.now().strftime("%B %d, %Y")
    dated_prompt = (
        f"CRITICAL CONTEXT: The current real-world date is exactly {current_date}. "
        f"All project timelines, academic years, and resume dates must be evaluated "
        f"relative to this date. Anything dated on or before {current_date} is in the "
        f"past or present — do NOT treat it as a future event or hallucination.\n\n"
        + VISIONARY_SYSTEM_PROMPT
    )
    response = _invoke(dated_prompt, _build_user_message(state))
    return {"visionary_response": response}


def pragmatist_node(state: BoardState) -> dict:
    """The Pragmatist — logistics, time, budget, grounded reality."""
    current_date = datetime.now().strftime("%B %d, %Y")
    dated_prompt = (
        f"CRITICAL CONTEXT: The current real-world date is exactly {current_date}. "
        f"All project timelines, academic years, and resume dates must be evaluated "
        f"relative to this date. Anything dated on or before {current_date} is in the "
        f"past or present — do NOT treat it as a future event or hallucination.\n\n"
        + PRAGMATIST_SYSTEM_PROMPT
    )
    response = _invoke(dated_prompt, _build_user_message(state))
    return {"pragmatist_response": response}


def advocate_node(state: BoardState) -> dict:
    """The Devil's Advocate — flaws, risks, blind spots."""
    current_date = datetime.now().strftime("%B %d, %Y")
    dated_prompt = (
        f"CRITICAL CONTEXT: The current real-world date is exactly {current_date}. "
        f"All project timelines, academic years, and resume dates must be evaluated "
        f"relative to this date. Anything dated on or before {current_date} is in the "
        f"past or present — do NOT treat it as a future event or hallucination.\n\n"
        + DEVIL_ADVOCATE_SYSTEM_PROMPT
    )
    response = _invoke(dated_prompt, _build_user_message(state))
    return {"advocate_response": response}


def chairperson_node(state: BoardState) -> dict:
    """The Chairperson — synthesises all three into the final Board Resolution."""
    current_date = datetime.now().strftime("%B %d, %Y")
    dated_prompt = (
        f"CRITICAL CONTEXT: The current real-world date is exactly {current_date}. "
        f"All project timelines, academic years, and resume dates must be evaluated "
        f"relative to this date. Anything dated on or before {current_date} is in the "
        f"past or present — do NOT treat it as a future event or hallucination.\n\n"
        + CHAIRPERSON_SYSTEM_PROMPT
    )
    synthesis_prompt = (
        f"The user submitted the following for Board review:\n\n"
        f'"""\n{state["user_input"]}\n"""\n\n'
        f"Here are the perspectives from your fellow Board members:\n\n"
        f"--- THE VISIONARY ---\n{state['visionary_response']}\n\n"
        f"--- THE PRAGMATIST ---\n{state['pragmatist_response']}\n\n"
        f"--- THE DEVIL'S ADVOCATE ---\n{state['advocate_response']}\n\n"
        f"Now deliver the final Board Resolution."
    )
    response = _invoke(dated_prompt, synthesis_prompt)
    return {"final_resolution": response}


# ── Graph assembly ─────────────────────────────────────────────────────────────

def build_board_graph() -> StateGraph:
    """Compile and return the Board of Directors LangGraph."""
    builder = StateGraph(BoardState)

    builder.add_node("visionary", visionary_node)
    builder.add_node("pragmatist", pragmatist_node)
    builder.add_node("advocate", advocate_node)
    builder.add_node("chairperson", chairperson_node)

    builder.set_entry_point("visionary")
    builder.add_edge("visionary", "pragmatist")
    builder.add_edge("pragmatist", "advocate")
    builder.add_edge("advocate", "chairperson")
    builder.add_edge("chairperson", END)

    return builder.compile()


# Singleton compiled graph — imported by main.py
board_graph = build_board_graph()
