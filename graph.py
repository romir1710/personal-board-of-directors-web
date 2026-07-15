"""
graph.py — LangGraph state machine: The Personal Board of Directors.

Flow (parallelised):
  user_input
      │
      ├──► visionary_node  ──┐
      ├──► pragmatist_node ──┼──► chairperson_node ──► END
      └──► advocate_node   ──┘

The three analyst nodes run in parallel via ThreadPoolExecutor since they
operate independently on the raw user_input — preserving intellectual
independence while cutting response time by ~50%.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Optional, TypedDict

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
    custom_llm: Optional[Any]   # per-request LLM override (Phase 2 — user API keys)


# ── Shared LLM instance ────────────────────────────────────────────────────────

_llm = build_llm(temperature=0.7)


def _invoke(system_prompt: str, user_message: str, llm: Any = None) -> str:
    """Call the LLM with a system prompt + user message and return the text."""
    model = llm if llm is not None else _llm
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]
    response = model.invoke(messages)
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


def _make_dated_prompt(base_prompt: str) -> str:
    """Prepend the current date context to a system prompt."""
    current_date = datetime.now().strftime("%B %d, %Y")
    return (
        f"CRITICAL CONTEXT: The current real-world date is exactly {current_date}. "
        f"All project timelines, academic years, and resume dates must be evaluated "
        f"relative to this date. Anything dated on or before {current_date} is in the "
        f"past or present — do NOT treat it as a future event or hallucination.\n\n"
        + base_prompt
    )


# ── Parallel advisors node ─────────────────────────────────────────────────────

def parallel_advisors_node(state: BoardState) -> dict:
    """Run all three advisors in parallel — same prompts, ~3x faster."""
    user_msg = _build_user_message(state)
    llm = state.get("custom_llm")

    def run_visionary():
        return _invoke(_make_dated_prompt(VISIONARY_SYSTEM_PROMPT), user_msg, llm)

    def run_pragmatist():
        return _invoke(_make_dated_prompt(PRAGMATIST_SYSTEM_PROMPT), user_msg, llm)

    def run_advocate():
        return _invoke(_make_dated_prompt(DEVIL_ADVOCATE_SYSTEM_PROMPT), user_msg, llm)

    with ThreadPoolExecutor(max_workers=3) as pool:
        vis_future  = pool.submit(run_visionary)
        prag_future = pool.submit(run_pragmatist)
        adv_future  = pool.submit(run_advocate)

    return {
        "visionary_response":  vis_future.result(),
        "pragmatist_response": prag_future.result(),
        "advocate_response":   adv_future.result(),
    }


def chairperson_node(state: BoardState) -> dict:
    """The Chairperson — synthesises all three into the final Board Resolution."""
    synthesis_prompt = (
        f"The user submitted the following for Board review:\n\n"
        f'"""\n{state["user_input"]}\n"""\n\n'
        f"Here are the perspectives from your fellow Board members:\n\n"
        f"--- THE VISIONARY ---\n{state['visionary_response']}\n\n"
        f"--- THE PRAGMATIST ---\n{state['pragmatist_response']}\n\n"
        f"--- THE DEVIL'S ADVOCATE ---\n{state['advocate_response']}\n\n"
        f"Now deliver the final Board Resolution."
    )
    response = _invoke(_make_dated_prompt(CHAIRPERSON_SYSTEM_PROMPT), synthesis_prompt, state.get("custom_llm"))
    return {"final_resolution": response}


# ── Graph assembly ─────────────────────────────────────────────────────────────

def build_board_graph() -> StateGraph:
    """Compile and return the Board of Directors LangGraph."""
    builder = StateGraph(BoardState)

    builder.add_node("advisors", parallel_advisors_node)
    builder.add_node("chairperson", chairperson_node)

    builder.set_entry_point("advisors")
    builder.add_edge("advisors", "chairperson")
    builder.add_edge("chairperson", END)

    return builder.compile()


# Singleton compiled graph — imported by main.py
board_graph = build_board_graph()

