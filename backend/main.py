"""FastAPI entrypoint for Spar with a Friend / DebateBot."""

from __future__ import annotations

import json
import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from coaching import get_practice_card, get_presets_payload
from graph import debate_graph, format_debate_response, live_graph, report_graph
from history import get_session, init_db, list_sessions, save_session
from llm_provider import (
    ProviderNotReadyError,
    get_model_name,
    get_provider_name,
    get_status,
    invoke_llm,
)

app = FastAPI(title="Spar with a Friend", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    init_db()


def _provider_http_error(exc: ProviderNotReadyError) -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={
            "error": exc.message,
            "checklist": exc.checklist,
            "provider": get_provider_name(),
            "model": get_model_name(),
            "local": get_provider_name() == "ollama",
        },
    )


class DebateRequest(BaseModel):
    topic: str
    friend_mode: bool = True
    tone: str = "patient"
    difficulty: str = "beginner"


class LiveDebateRequest(BaseModel):
    topic: str
    user_argument: str
    round: str  # opening | rebuttal | closing
    argument_history: list = Field(default_factory=list)
    friend_mode: bool = True
    tone: str = "patient"
    difficulty: str = "beginner"


class ScoringRequest(BaseModel):
    argument: str
    topic: str
    friend_mode: bool = True


class FeedbackRequest(BaseModel):
    argument: str
    topic: str
    scores: dict
    target_score: int
    friend_mode: bool = True


class RoundReportRequest(BaseModel):
    topic: str
    user_turns: list = Field(default_factory=list)
    argument_history: list = Field(default_factory=list)
    tone: str = "patient"
    difficulty: str = "beginner"
    friend_mode: bool = True


@app.get("/")
def read_root():
    status = get_status()
    return {
        "message": "Spar with a Friend — DebateBot local coach online",
        "provider": status["provider"],
        "model": status["model"],
        "local": status["local"],
        "ready": status["ready"],
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/status")
def api_status():
    return get_status()


@app.get("/api/presets")
def api_presets():
    return get_presets_payload()


@app.get("/api/history")
def api_history(limit: int = 20):
    return {"sessions": list_sessions(limit=limit)}


@app.get("/api/history/{session_id}")
def api_history_detail(session_id: int):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.post("/api/debate")
async def run_debate(request: DebateRequest):
    """Run a full dual-AI debate via LangGraph."""
    try:
        result = debate_graph.invoke(
            {
                "topic": request.topic,
                "side": "Proposition",
                "friend_mode": request.friend_mode,
                "tone": request.tone,
                "difficulty": request.difficulty,
                "argument_history": "",
                "final_output": "",
            }
        )
    except ProviderNotReadyError as exc:
        raise _provider_http_error(exc) from exc

    return format_debate_response(result)


@app.post("/api/live-counter")
async def generate_counter(request: LiveDebateRequest):
    """Generate AI counter-argument for Live Arena via LangGraph."""
    try:
        result = live_graph.invoke(
            {
                "topic": request.topic,
                "user_argument": request.user_argument,
                "round": request.round,
                "argument_history": request.argument_history,
                "friend_mode": request.friend_mode,
                "tone": request.tone,
                "difficulty": request.difficulty,
            }
        )
    except ProviderNotReadyError as exc:
        raise _provider_http_error(exc) from exc

    return {
        "counter_argument": result.get("counter_argument", ""),
        "points": result.get("points") or [],
    }


@app.post("/api/round-report")
async def round_report(request: RoundReportRequest):
    """Short end-of-round coaching report + local SQLite save."""
    try:
        result = report_graph.invoke(
            {
                "topic": request.topic,
                "user_turns": request.user_turns,
                "tone": request.tone,
                "difficulty": request.difficulty,
            }
        )
    except ProviderNotReadyError as exc:
        raise _provider_http_error(exc) from exc

    report = result.get("report") or {}
    session_id = save_session(
        provider=get_provider_name(),
        model=get_model_name(),
        topic=request.topic,
        tone=request.tone,
        difficulty=request.difficulty,
        transcript={
            "user_turns": request.user_turns,
            "argument_history": request.argument_history,
        },
        report=report,
    )
    return {
        "report": report,
        "session_id": session_id,
        "practice_card": get_practice_card(request.topic),
    }


@app.post("/api/score-argument")
async def score_argument(request: ScoringRequest):
    """Score a debate argument based on multiple metrics using AI analysis."""
    argument = request.argument
    topic = request.topic

    friend_note = ""
    if request.friend_mode:
        friend_note = (
            "Also note filler words and structure. Keep reasons kind and specific."
        )

    scoring_prompt = f"""You are an expert debate judge. Analyze this argument IN DETAIL.

TOPIC: {topic}

ARGUMENT TO ANALYZE:
"{argument}"

Provide a thorough analysis with SPECIFIC QUOTES from the argument. For each metric, cite exactly which phrases led to your score.
{friend_note}

Respond in this EXACT JSON format:
{{
    "coherence": 0.XX,
    "coherence_reason": "Quote the specific phrases that show good/poor flow. Example: 'The transition from X to Y was abrupt' or 'The phrase \\"therefore\\" effectively connects ideas'",
    "relevance": 0.XX,
    "relevance_reason": "Quote which parts directly address the topic and which parts drift off-topic",
    "evidence_strength": 0.XX,
    "evidence_reason": "List the specific evidence/facts cited. If none: 'No concrete evidence provided - claims like \\"X\\" lack supporting data'",
    "fallacy_penalty": 0.XX,
    "fallacy_reason": "Quote the exact phrases containing fallacies, or say 'No fallacies detected'",
    "sentence_count": N,
    "evidence_count": N,
    "fallacies": ["specific fallacy with quote"] or [],
    "strongest_point": "Quote the single best sentence/argument",
    "weakest_point": "Quote the sentence that needs most improvement and explain why"
}}

Be specific. Quote exact phrases. Don't give generic feedback."""

    try:
        content = invoke_llm(scoring_prompt)
        json_match = re.search(r"\{[\s\S]*\}", str(content))
        if json_match:
            scores = json.loads(json_match.group())
        else:
            raise ValueError("Could not parse scoring response")

        scores["coherence"] = max(0, min(1, float(scores.get("coherence", 0.7))))
        scores["relevance"] = max(0, min(1, float(scores.get("relevance", 0.7))))
        scores["evidence_strength"] = max(
            0, min(1, float(scores.get("evidence_strength", 0.6)))
        )
        scores["fallacy_penalty"] = max(
            0, min(1, float(scores.get("fallacy_penalty", 0.1)))
        )

        w1, w2, w3, w4 = 0.25, 0.30, 0.30, 0.15
        argument_strength = (
            w1 * scores["coherence"]
            + w2 * scores["relevance"]
            + w3 * scores["evidence_strength"]
            - w4 * scores["fallacy_penalty"]
        )
        argument_strength = max(0, min(1, argument_strength))

        return {
            "coherence": scores["coherence"],
            "coherenceReason": scores.get("coherence_reason", ""),
            "relevance": scores["relevance"],
            "relevanceReason": scores.get("relevance_reason", ""),
            "evidenceStrength": scores["evidence_strength"],
            "evidenceReason": scores.get("evidence_reason", ""),
            "fallacyPenalty": scores["fallacy_penalty"],
            "fallacyReason": scores.get("fallacy_reason", ""),
            "argumentStrength": argument_strength,
            "strongestPoint": scores.get("strongest_point", ""),
            "weakestPoint": scores.get("weakest_point", ""),
            "details": {
                "sentenceCount": scores.get(
                    "sentence_count", len(argument.split("."))
                ),
                "evidenceCount": scores.get("evidence_count", 0),
                "fallaciesDetected": scores.get("fallacies", []),
            },
        }

    except ProviderNotReadyError as exc:
        raise _provider_http_error(exc) from exc
    except Exception as e:
        print(f"Error scoring argument: {e}")
        return {
            "coherence": 0.7,
            "coherenceReason": "Unable to analyze - please try again",
            "relevance": 0.7,
            "relevanceReason": "Unable to analyze - please try again",
            "evidenceStrength": 0.6,
            "evidenceReason": "Unable to analyze - please try again",
            "fallacyPenalty": 0.1,
            "fallacyReason": "Unable to analyze - please try again",
            "argumentStrength": 0.72,
            "strongestPoint": "",
            "weakestPoint": "",
            "details": {
                "sentenceCount": len(argument.split(".")),
                "evidenceCount": 0,
                "fallaciesDetected": [],
            },
        }


@app.post("/api/get-feedback")
async def get_feedback(request: FeedbackRequest):
    """Get AI feedback on how to improve an argument to reach the target score."""
    argument = request.argument
    topic = request.topic
    scores = request.scores
    target_score = request.target_score
    current_score = int(scores.get("argumentStrength", 0.7) * 100)
    gap = target_score - current_score

    style = (
        "Be kind, specific, and actionable. Short tips only."
        if request.friend_mode
        else "Be concise and practical."
    )

    feedback_prompt = f"""You are an expert debate coach helping someone improve their argumentation skills.
{style}

TOPIC: {topic}

STUDENT'S ARGUMENT:
{argument}

CURRENT SCORES:
- Coherence: {scores.get('coherence', 0.7):.0%}
- Relevance: {scores.get('relevance', 0.7):.0%}
- Evidence Strength: {scores.get('evidenceStrength', 0.6):.0%}
- Fallacy Penalty: -{scores.get('fallacyPenalty', 0.1):.0%}
- Overall Score: {current_score}%
- Target Score: {target_score}%
- Gap to close: {gap} points

Provide specific, actionable feedback to help them improve. Focus on their weakest areas.

Respond in this EXACT JSON format:
{{
    "type": "improvement",
    "message": "A brief encouraging message about their gap to the target (1 sentence)",
    "tips": [
        {{
            "metric": "Name of metric to improve",
            "tip": "Specific, actionable advice (2-3 sentences max)"
        }}
    ]
}}

Provide 2-3 tips focusing on the metrics with the lowest scores. Be concise and practical."""

    try:
        content = invoke_llm(feedback_prompt)
        json_match = re.search(r"\{[\s\S]*\}", str(content))
        if json_match:
            return json.loads(json_match.group())
        raise ValueError("Could not parse feedback")

    except ProviderNotReadyError as exc:
        raise _provider_http_error(exc) from exc
    except Exception as e:
        print(f"Error getting feedback: {e}")
        tips = []
        if scores.get("coherence", 1) < 0.75:
            tips.append(
                {
                    "metric": "Coherence",
                    "tip": "Connect your ideas more clearly. Use transition words like 'therefore', 'however', 'furthermore' to link sentences.",
                }
            )
        if scores.get("relevance", 1) < 0.8:
            tips.append(
                {
                    "metric": "Relevance",
                    "tip": "Stay focused on the debate topic. Make sure each point directly addresses the motion.",
                }
            )
        if scores.get("evidenceStrength", 1) < 0.7:
            tips.append(
                {
                    "metric": "Evidence",
                    "tip": "Add specific examples, statistics, or expert citations to strengthen your claims.",
                }
            )
        if scores.get("fallacyPenalty", 0) > 0.1:
            tips.append(
                {
                    "metric": "Logic",
                    "tip": "Avoid emotional appeals and stick to evidence-based reasoning. Check for common fallacies.",
                }
            )

        if not tips:
            tips.append(
                {
                    "metric": "Overall",
                    "tip": "Add more depth and specificity to your arguments. Consider addressing potential counterarguments.",
                }
            )

        return {
            "type": "improvement",
            "message": f"You need {gap} more points to reach your target. Here's how:",
            "tips": tips[:3],
        }
