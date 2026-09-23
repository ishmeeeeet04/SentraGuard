"""
LangGraph orchestration: wires Stage 0 (Pre-Filter), Stage 1 (Vector
Similarity), and Stage 3 (LLM-as-Judge) into a single pipeline.

Routing logic:
- If Stage 0 says BLOCK -> stop immediately, don't waste time on later stages.
- If Stage 1 says BLOCK -> stop immediately.
- If Stage 1 says SUSPICIOUS -> escalate to the LLM-Judge (Stage 3).
- If Stage 1 says SAFE -> done, no need for the expensive judge call.
"""

from typing import TypedDict

from langgraph.graph import StateGraph, END

from app.detection.models import DetectionResult, Verdict
from app.detection.prefilter import run_prefilter
from app.detection.similarity import run_similarity_check
from app.detection.judge import run_llm_judge


class PipelineState(TypedDict):
    text: str
    results: list[DetectionResult]
    final_verdict: Verdict


def _prefilter_node(state: PipelineState) -> PipelineState:
    result = run_prefilter(state["text"])
    state["results"].append(result)
    return state


def _similarity_node(state: PipelineState) -> PipelineState:
    result = run_similarity_check(state["text"])
    state["results"].append(result)
    return state


def _judge_node(state: PipelineState) -> PipelineState:
    result = run_llm_judge(state["text"])
    state["results"].append(result)
    return state


def _finalize_node(state: PipelineState) -> PipelineState:
    # The verdict of the LAST stage that actually ran wins.
    state["final_verdict"] = state["results"][-1].verdict
    return state


def _after_prefilter(state: PipelineState) -> str:
    if state["results"][-1].verdict == Verdict.BLOCK:
        return "finalize"
    return "similarity"


def _after_similarity(state: PipelineState) -> str:
    verdict = state["results"][-1].verdict
    if verdict == Verdict.SUSPICIOUS:
        return "judge"
    return "finalize"


def build_pipeline():
    graph = StateGraph(PipelineState)

    graph.add_node("prefilter", _prefilter_node)
    graph.add_node("similarity", _similarity_node)
    graph.add_node("judge", _judge_node)
    graph.add_node("finalize", _finalize_node)

    graph.set_entry_point("prefilter")

    graph.add_conditional_edges(
        "prefilter", _after_prefilter, {"similarity": "similarity", "finalize": "finalize"}
    )
    graph.add_conditional_edges(
        "similarity", _after_similarity, {"judge": "judge", "finalize": "finalize"}
    )
    graph.add_edge("judge", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()


_pipeline = build_pipeline()


def run_detection_pipeline(text: str) -> PipelineState:
    initial_state: PipelineState = {"text": text, "results": [], "final_verdict": Verdict.SAFE}
    return _pipeline.invoke(initial_state)