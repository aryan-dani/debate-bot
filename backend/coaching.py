"""Friend coaching profile, presets, tone/difficulty, and practice card.

Edit this file to change coach behavior without rewriting the app.
Fill TODO_FRIEND_NAME / TODO_RELATION before the handoff demo.
"""

from __future__ import annotations

# --- Friend brief (fill before handoff; do not invent a biography) ---
TODO_FRIEND_NAME = "TODO_FRIEND_NAME"  # first name only
TODO_RELATION = "TODO_RELATION"  # e.g. roommate / classmate / debate-club mate

FRIEND_PROBLEM = (
    "Freezes in group discussions; needs patient GD/viva practice "
    "to get words out under mild pressure."
)
FRIEND_CONSTRAINTS = (
    "Weak laptop, no paid APIs, no cloud transcripts — local Ollama only for demo."
)
FRIEND_SUCCESS = (
    "Can finish a 10-minute practice round and get kind, specific feedback."
)

PRODUCT_NAME = "Spar with a Friend"
PRODUCT_PITCH = (
    "A local, open-weight practice partner so a friend can rehearse debates "
    "and GDs without sending speech to a cloud chat app."
)

# Campus starter presets (not a personal biography)
PRESET_TOPICS = [
    "Placements matter more than CGPA for campus careers",
    "Mandatory attendance should be abolished in college",
    "Social media makes it harder for shy students to speak up",
    "Viva: Defend one design choice you made in a recent project",
    "A remote internship teaches more than an on-campus one",
]

TONES = ("patient", "firm", "rapid-fire")
DIFFICULTIES = ("beginner", "intermediate")

PRACTICE_CARD_TIPS = [
    'Start with a template: "My point is X because Y."',
    "Say one clear sentence, then add one reason — stop talking after two points.",
    "If you freeze, restate the topic in your own words, then give your first claim.",
]

TONE_INSTRUCTIONS = {
    "patient": (
        "Tone: patient coach-opponent. Keep replies short. Ask at most one "
        "clarifying question. Do not pile on multiple attacks. Leave room for "
        "the speaker to recover."
    ),
    "firm": (
        "Tone: firm but respectful. Challenge claims directly. Stay concise. "
        "No insults or sarcasm."
    ),
    "rapid-fire": (
        "Tone: rapid-fire. Reply in about 80 words max with ONE sharp counter-point. "
        "No long paragraphs."
    ),
}

DIFFICULTY_INSTRUCTIONS = {
    "beginner": (
        "Difficulty: beginner. Use simple wording. Push back on only one claim. "
        "Avoid jargon."
    ),
    "intermediate": (
        "Difficulty: intermediate. Push back on up to two claims and ask for "
        "one piece of evidence."
    ),
}


def get_friend_profile() -> dict:
    return {
        "name": TODO_FRIEND_NAME,
        "relation": TODO_RELATION,
        "problem": FRIEND_PROBLEM,
        "constraints": FRIEND_CONSTRAINTS,
        "success": FRIEND_SUCCESS,
        "product_name": PRODUCT_NAME,
        "pitch": PRODUCT_PITCH,
    }


def get_practice_card(topic: str | None = None) -> dict:
    return {
        "title": "Before you start",
        "topic": topic or "",
        "tips": list(PRACTICE_CARD_TIPS),
        "success": FRIEND_SUCCESS,
    }


def coaching_prompt_block(tone: str = "patient", difficulty: str = "beginner") -> str:
    tone_key = tone if tone in TONE_INSTRUCTIONS else "patient"
    diff_key = difficulty if difficulty in DIFFICULTY_INSTRUCTIONS else "beginner"
    return (
        f"{TONE_INSTRUCTIONS[tone_key]}\n"
        f"{DIFFICULTY_INSTRUCTIONS[diff_key]}\n"
        "You are a practice partner for someone who freezes in group discussions. "
        "Be kind. Be specific. Never mock them."
    )


def get_presets_payload() -> dict:
    return {
        "topics": list(PRESET_TOPICS),
        "tones": list(TONES),
        "difficulties": list(DIFFICULTIES),
        "practice_card": get_practice_card(),
        "friend": get_friend_profile(),
    }
