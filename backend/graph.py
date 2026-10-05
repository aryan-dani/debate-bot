"""
LangGraph debate harness for Spar with a Friend / DebateBot.

Edit node prompts here (and coaching.py for tone/difficulty) to change
agent behavior without rewriting the FastAPI routes.

Graphs:
  - debate_graph: full dual-AI Opening → Rebuttal → Closing
  - live_graph: one counter-argument turn for Live Arena
  - report_graph: short end-of-round coaching report
"""

from __future__ import annotations

import json
import re
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from coaching import coaching_prompt_block, get_practice_card
from llm_provider import invoke_llm


class DebateState(TypedDict, total=False):
    topic: str
    side: str
    friend_mode: bool
    tone: str
    difficulty: str
    prop_opening: str
    opp_opening: str
    prop_rebuttal: str
    opp_rebuttal: str
    prop_closing: str
    opp_closing: str
    argument_history: str
    final_output: str


class LiveState(TypedDict, total=False):
    topic: str
    user_argument: str
    round: str
    argument_history: list
    friend_mode: bool
    tone: str
    difficulty: str
    counter_argument: str
    points: list


class ReportState(TypedDict, total=False):
    topic: str
    user_turns: list
    tone: str
    difficulty: str
    report: dict


def _coach_block(state: dict) -> str:
    if not state.get("friend_mode", True):
        return ""
    return coaching_prompt_block(
        tone=state.get("tone") or "patient",
        difficulty=state.get("difficulty") or "beginner",
    )


def _opening_prompt(topic: str, side: str, coach: str) -> str:
    return f"""You are presenting the {side} position in a formal debate.
Motion: {topic}
{coach}

Write a strong opening statement (max 150 words) with 2-3 distinct arguments.

IMPORTANT RULES:
- Do NOT start with "Ladies and gentlemen" or similar greetings
- Do NOT use phrases like "I believe" or "In my opinion"
- Present arguments as factual claims with evidence
- Use a direct, assertive tone
- Jump straight into your first point

Example format:
"[First key claim]. [Supporting evidence or reasoning]. [Second point with evidence]. [Third point if needed]."
"""


def _rebuttal_prompt(topic: str, side: str, history: str, coach: str) -> str:
    return f"""You are presenting a rebuttal for the {side} position in a formal debate.
Motion: {topic}
{coach}

Arguments to counter:
{history}

Write a sharp rebuttal (max 150 words) addressing the opposing points.

IMPORTANT RULES:
- Do NOT start with "While my opponent" or "My opponent claims"
- Do NOT use "the opposition" or "they argue"
- Instead, directly state why each claim is flawed
- Present counter-evidence factually
- Use phrases like "This overlooks...", "The evidence shows...", "In reality..."

Example format:
"The claim that [X] fails to account for [Y]. [Counter-evidence]. Furthermore, [next counter-point with evidence]."
"""


def _closing_prompt(topic: str, side: str, history: str, coach: str) -> str:
    return f"""You are delivering a closing statement for the {side} position.
Motion: {topic}
{coach}

Debate context:
{history}

Write a powerful closing (max 150 words) summarizing your strongest points.

IMPORTANT RULES:
- Do NOT start with "In conclusion" or "To summarize"
- Do NOT use "Ladies and gentlemen" or "As I have shown"
- Make a final compelling case with your best evidence
- End with a strong declarative statement
- Be assertive and confident

Example format:
"[Restate strongest point]. [Key evidence that proves your case]. [Why this matters]. [Strong final statement]."
"""


def _live_counter_prompt(
    topic: str,
    user_argument: str,
    round_type: str,
    history_context: str,
    coach: str,
) -> str:
    if round_type == "opening":
        return f"""You are presenting the Opposition position in a live debate.
Motion: {topic}
{coach}

Argument to counter:
{user_argument}
{history_context}

Write a counter-argument (max 200 words) that directly challenges this position.

IMPORTANT RULES:
- Do NOT refer to "the user" or "my opponent" or "the speaker"
- Do NOT start with greetings or "I would argue"
- Present counter-points as factual claims
- Use evidence and logical reasoning
- Directly address and refute the specific claims made

Format: Jump straight into your counter-arguments. State facts and evidence."""

    if round_type == "rebuttal":
        return f"""You are presenting a rebuttal in a live debate.
Motion: {topic}
{coach}

Argument to counter:
{user_argument}
{history_context}

Write a rebuttal (max 200 words) that dismantles this argument.

IMPORTANT RULES:
- Do NOT use "the user", "my opponent", "the previous speaker"
- Do NOT start with "While..." or "Although..."
- Identify specific flaws in the reasoning
- Provide counter-evidence directly
- Use phrases like "This fails because...", "The evidence contradicts...", "In fact..."

Format: Directly address each claim with counter-evidence."""

    return f"""You are delivering a closing counter-argument in a live debate.
Motion: {topic}
{coach}

Final argument to counter:
{user_argument}
{history_context}

Write a closing counter-argument (max 200 words).

IMPORTANT RULES:
- Do NOT use "In conclusion" or "To summarize"
- Do NOT refer to "the user" or "my opponent"
- Highlight the key weaknesses exposed in this debate
- Make a final compelling case for your position
- End with a strong declarative statement

Format: Present your strongest counter-points with evidence. End powerfully."""


def _split_points(text: str) -> list[dict]:
    points = []
    paragraphs = text.strip().split("\n\n")
    for i, para in enumerate(paragraphs):
        if para.strip():
            points.append({"id": i + 1, "text": para.strip()})
    if not points:
        points = [{"id": 1, "text": text.strip()}]
    return points


def _parse_json_object(content: str) -> dict:
    match = re.search(r"\{[\s\S]*\}", content)
    if not match:
        raise ValueError("Could not parse JSON from model response")
    return json.loads(match.group())


def run_opening_prop(state: DebateState) -> dict:
    coach = _coach_block(state)
    text = invoke_llm(_opening_prompt(state["topic"], "Proposition", coach))
    return {
        "prop_opening": text,
        "final_output": text,
        "argument_history": f"\n\nOPENING (Proposition):\n{text}",
        "side": "Proposition",
    }


def run_opening_opp(state: DebateState) -> dict:
    coach = _coach_block(state)
    text = invoke_llm(_opening_prompt(state["topic"], "Opposition", coach))
    history = state.get("argument_history", "")
    return {
        "opp_opening": text,
        "final_output": text,
        "argument_history": f"{history}\n\nOPENING (Opposition):\n{text}",
        "side": "Opposition",
    }


def run_rebuttal_prop(state: DebateState) -> dict:
    coach = _coach_block(state)
    text = invoke_llm(
        _rebuttal_prompt(
            state["topic"], "Proposition", state.get("opp_opening", ""), coach
        )
    )
    history = state.get("argument_history", "")
    return {
        "prop_rebuttal": text,
        "final_output": text,
        "argument_history": f"{history}\n\nREBUTTAL (Proposition):\n{text}",
        "side": "Proposition",
    }


def run_rebuttal_opp(state: DebateState) -> dict:
    coach = _coach_block(state)
    text = invoke_llm(
        _rebuttal_prompt(
            state["topic"], "Opposition", state.get("prop_opening", ""), coach
        )
    )
    history = state.get("argument_history", "")
    return {
        "opp_rebuttal": text,
        "final_output": text,
        "argument_history": f"{history}\n\nREBUTTAL (Opposition):\n{text}",
        "side": "Opposition",
    }


def run_closing_prop(state: DebateState) -> dict:
    coach = _coach_block(state)
    hist = (
        f"Your Opening: {state.get('prop_opening', '')}\n"
        f"Opponent's Rebuttal: {state.get('opp_rebuttal', '')}"
    )
    text = invoke_llm(_closing_prompt(state["topic"], "Proposition", hist, coach))
    history = state.get("argument_history", "")
    return {
        "prop_closing": text,
        "final_output": text,
        "argument_history": f"{history}\n\nCLOSING (Proposition):\n{text}",
        "side": "Proposition",
    }


def run_closing_opp(state: DebateState) -> dict:
    coach = _coach_block(state)
    hist = (
        f"Your Opening: {state.get('opp_opening', '')}\n"
        f"Opponent's Rebuttal: {state.get('prop_rebuttal', '')}"
    )
    text = invoke_llm(_closing_prompt(state["topic"], "Opposition", hist, coach))
    history = state.get("argument_history", "")
    return {
        "opp_closing": text,
        "final_output": text,
        "argument_history": f"{history}\n\nCLOSING (Opposition):\n{text}",
        "side": "Opposition",
    }


def run_live_counter(state: LiveState) -> dict:
    history = state.get("argument_history") or []
    history_context = ""
    if history:
        history_context = "\n\nPrevious points in this debate:\n"
        for item in history:
            if item.get("type") == "user":
                history_context += f"PRO: {item.get('text', '')}\n"
            else:
                history_context += f"CON: {item.get('text', '')}\n"

    coach = _coach_block(state)
    prompt = _live_counter_prompt(
        state["topic"],
        state["user_argument"],
        state.get("round") or "opening",
        history_context,
        coach,
    )
    text = invoke_llm(prompt)
    return {"counter_argument": text, "points": _split_points(text)}


def _fallback_report(topic: str, user_turns: list) -> dict:
    joined = " ".join(t.get("text", "") for t in user_turns)
    fillers = []
    for word in ("um", "uh", "like", "you know", "basically"):
        if re.search(rf"\b{re.escape(word)}\b", joined, re.I):
            fillers.append(word)
    return {
        "headline": "Solid practice — keep the next round flowing.",
        "did_well": [
            "You showed up and finished the round.",
            "You put at least one clear claim on the table."
            if joined.strip()
            else "You started the practice habit — that counts.",
        ],
        "try_next": [
            'Lead with "My point is X because Y."',
            "Stop after two points so you do not freeze mid-sentence.",
            "Name one piece of evidence (example, number, or story).",
        ],
        "filler_note": (
            f"Watch these fillers: {', '.join(fillers)}."
            if fillers
            else "No heavy filler words spotted — nice."
        ),
        "topic": topic,
    }


def run_round_report(state: ReportState) -> dict:
    topic = state.get("topic") or ""
    user_turns = state.get("user_turns") or []
    turns_text = "\n".join(
        f"- [{t.get('round', '?')}] {t.get('text', '')}" for t in user_turns
    )
    prompt = f"""You are a kind debate coach for someone who freezes in group discussions.
Topic: {topic}
Tone setting: {state.get('tone', 'patient')}
Difficulty: {state.get('difficulty', 'beginner')}

User's turns:
{turns_text or '(no turns recorded)'}

Write a SHORT end-of-round report. Be kind, specific, and actionable.
Respond in this EXACT JSON format:
{{
  "headline": "one encouraging sentence",
  "did_well": ["specific win 1", "specific win 2"],
  "try_next": ["actionable tip 1", "actionable tip 2", "actionable tip 3"],
  "filler_note": "brief note on filler words or 'No heavy fillers spotted'"
}}
Do not write academic essays. Keep each string under 20 words."""

    try:
        content = invoke_llm(prompt)
        report = _parse_json_object(content)
        report.setdefault("did_well", [])
        report.setdefault("try_next", [])
        report.setdefault("headline", "Nice work finishing the round.")
        report.setdefault("filler_note", "No heavy fillers spotted.")
        report["topic"] = topic
        # keep lists short
        report["did_well"] = list(report["did_well"])[:2]
        report["try_next"] = list(report["try_next"])[:3]
        return {"report": report}
    except Exception:
        return {"report": _fallback_report(topic, user_turns)}


def _build_debate_graph():
    builder = StateGraph(DebateState)
    builder.add_node("opening_prop", run_opening_prop)
    builder.add_node("opening_opp", run_opening_opp)
    builder.add_node("rebuttal_prop", run_rebuttal_prop)
    builder.add_node("rebuttal_opp", run_rebuttal_opp)
    builder.add_node("closing_prop", run_closing_prop)
    builder.add_node("closing_opp", run_closing_opp)

    builder.add_edge(START, "opening_prop")
    builder.add_edge("opening_prop", "opening_opp")
    builder.add_edge("opening_opp", "rebuttal_prop")
    builder.add_edge("rebuttal_prop", "rebuttal_opp")
    builder.add_edge("rebuttal_opp", "closing_prop")
    builder.add_edge("closing_prop", "closing_opp")
    builder.add_edge("closing_opp", END)
    return builder.compile()


def _build_live_graph():
    builder = StateGraph(LiveState)
    builder.add_node("counter", run_live_counter)
    builder.add_edge(START, "counter")
    builder.add_edge("counter", END)
    return builder.compile()


def _build_report_graph():
    builder = StateGraph(ReportState)
    builder.add_node("report", run_round_report)
    builder.add_edge(START, "report")
    builder.add_edge("report", END)
    return builder.compile()


debate_graph = _build_debate_graph()
live_graph = _build_live_graph()
report_graph = _build_report_graph()


def get_summary(content: str, max_words: int = 25) -> str:
    sentences = content.split(".")
    if sentences:
        first_sentence = sentences[0].strip()
        words = first_sentence.split()
        if len(words) > max_words:
            return " ".join(words[:max_words]) + "..."
        return first_sentence + "."
    return content[:150] + "..."


def format_debate_response(result: dict) -> dict:
    topic = result["topic"]

    def pack(full: str) -> dict:
        return {"summary": get_summary(full), "full": full}

    return {
        "topic": topic,
        "practice_card": get_practice_card(topic),
        "proposition": {
            "opening": pack(result.get("prop_opening", "")),
            "rebuttal": pack(result.get("prop_rebuttal", "")),
            "closing": pack(result.get("prop_closing", "")),
        },
        "opposition": {
            "opening": pack(result.get("opp_opening", "")),
            "rebuttal": pack(result.get("opp_rebuttal", "")),
            "closing": pack(result.get("opp_closing", "")),
        },
    }


if __name__ == "__main__":
    test_input = {
        "topic": "Mandatory attendance should be abolished in college.",
        "side": "Proposition",
        "friend_mode": True,
        "tone": "patient",
        "difficulty": "beginner",
        "argument_history": "",
        "final_output": "",
    }
    result = debate_graph.invoke(test_input)  # type: ignore
    print(format_debate_response(result)["proposition"]["opening"]["summary"])
