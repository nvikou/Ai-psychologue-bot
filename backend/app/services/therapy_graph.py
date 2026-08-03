"""Graphe LangGraph : écouter → explorer → reformuler → conseiller."""

from __future__ import annotations

import logging
import re
from typing import Literal
from typing import TypedDict

from langgraph.graph import END
from langgraph.graph import START
from langgraph.graph import StateGraph

from app.services.i18n_service import language_instruction
from app.services.openai_service import AIServiceError
from app.services.openai_service import classify_text
from app.services.openai_service import generate_reply_with_system

logger = logging.getLogger(__name__)

Phase = Literal["listen", "explore", "reflect", "advise"]

VALID_PHASES = {"listen", "explore", "reflect", "advise"}
VALID_INTENTS = {"confirm", "correct", "continue", "ready_reflect"}

PHASE_INSTRUCTIONS: dict[str, str] = {
    "listen": """CURRENT STAGE: LISTEN
- Warmly acknowledge what the user shared.
- Do NOT give advice yet.
- Invite them to say a bit more in 1 short open question.
- Keep the reply short (2 short paragraphs max).""",
    "explore": """CURRENT STAGE: EXPLORE
- Help the user express feelings more clearly.
- Ask 1 open, gentle question (not a list of questions).
- Do NOT give solutions or advice yet.
- Focus on emotions, needs, and context.""",
    "reflect": """CURRENT STAGE: REFLECT
- Reformulate what you understood in your own words.
- Check accuracy with one clear question like:
  "If I understand correctly... is that right?"
- Do NOT give advice yet.
- Be concise and warm.""",
    "advise": """CURRENT STAGE: ADVISE
- The user confirmed your understanding.
- Offer 1 to 3 practical, psychologist-style suggestions
  (coping, reframing, small next steps).
- No diagnosis, no medication, no medical claims.
- End with one supportive question to continue if useful.
- Keep it concrete and brief.""",
}

ROUTER_SYSTEM = """You route a therapy-style conversation.
Current session phase: {phase}
Turn count: {turn_count}

Choose ONE intent label only (no punctuation, no explanation):
- confirm : user agrees that the reformulation/understanding is correct
- correct : user says the understanding is wrong, incomplete, or inaccurate
- continue : user adds more feelings/details or wants to keep exploring
- ready_reflect : user shared enough clear emotional content to reformulate now
  (use mainly when current phase is explore or listen)

Rules:
- If phase is reflect and user accepts the summary → confirm
- If phase is reflect and user rejects/corrects → correct
- If phase is reflect and user adds new important content → continue
- If phase is explore/listen and content is rich enough to summarize → ready_reflect
- If phase is explore/listen and still vague/short → continue
- If phase is advise → continue

Reply with exactly one label."""


class TherapyState(TypedDict):
    """État du graphe de thérapie conversationnelle."""

    history: list[dict[str, str]]
    user_message: str
    language: str | None
    goals: str | None
    phase: str
    turn_count: int
    reply: str
    next_phase: str
    intent: str


def _last_assistant(history: list[dict[str, str]]) -> str:
    for msg in reversed(history):
        if msg.get("role") == "assistant":
            return msg.get("content", "")[:500]
    return ""


def _parse_intent(raw: str) -> str:
    cleaned = raw.strip().lower()
    cleaned = re.sub(r"[^a-z_]", "", cleaned.replace(" ", "_"))
    for intent in VALID_INTENTS:
        if intent in cleaned:
            return intent
    return "continue"


async def classify_intent(state: TherapyState) -> str:
    """LLM analyse la réponse user et renvoie un intent au graphe."""
    last_bot = _last_assistant(state["history"])
    user_block = (
        f"Last assistant message:\n{last_bot or '(none)'}\n\n"
        f"User message:\n{state['user_message']}"
    )
    system = ROUTER_SYSTEM.format(
        phase=state["phase"],
        turn_count=state["turn_count"],
    )
    try:
        raw = await classify_text(system, user_block)
        intent = _parse_intent(raw)
        logger.info(
            "router intent=%s raw=%s phase=%s",
            intent,
            raw,
            state["phase"],
        )
        return intent
    except AIServiceError:
        logger.warning("router failed, fallback continue")
        return "continue"


def intent_to_phase(
    current: str,
    intent: str,
    turn_count: int,
) -> str:
    """Traduit l'intent LLM en phase active pour ce tour."""
    if current == "listen":
        if turn_count == 0:
            return "listen"
        if intent == "ready_reflect":
            return "reflect"
        return "explore"

    if current == "explore":
        if intent == "ready_reflect":
            return "reflect"
        return "explore"

    if current == "reflect":
        if intent == "confirm":
            return "advise"
        if intent == "correct":
            return "explore"
        # continue / ready_reflect → encore clarifier
        return "explore"

    if current == "advise":
        return "explore"

    return "listen"


async def decide_phase(state: TherapyState) -> TherapyState:
    """Décide la phase via analyse LLM de la réponse utilisateur."""
    intent = await classify_intent(state)
    phase = intent_to_phase(
        state["phase"],
        intent,
        state["turn_count"],
    )
    return {**state, "phase": phase, "intent": intent}


async def generate_node(state: TherapyState) -> TherapyState:
    """Génère la réponse selon la phase."""
    phase = state["phase"]
    stage = PHASE_INSTRUCTIONS.get(phase, PHASE_INSTRUCTIONS["listen"])
    system_extra = (
        f"{language_instruction(state['language'])}\n\n{stage}"
    )
    if state.get("goals"):
        system_extra += f"\nUser goals/context: {state['goals']}"

    reply = await generate_reply_with_system(
        state["history"],
        state["user_message"],
        system_extra=system_extra,
    )
    return {**state, "reply": reply}


def advance_phase(state: TherapyState) -> TherapyState:
    """Calcule la phase à persister pour le prochain message."""
    phase = state["phase"]
    turns = state["turn_count"] + 1

    if phase == "listen":
        next_phase = "explore"
    elif phase == "explore":
        next_phase = "explore"
    elif phase == "reflect":
        # Au prochain message, le router LLM jugera confirm/correct
        next_phase = "reflect"
    elif phase == "advise":
        next_phase = "explore"
    else:
        next_phase = "listen"

    return {
        **state,
        "next_phase": next_phase,
        "turn_count": turns,
    }


def build_therapy_graph():
    """Construit le graphe LangGraph compilé."""
    graph = StateGraph(TherapyState)
    graph.add_node("decide_phase", decide_phase)
    graph.add_node("generate", generate_node)
    graph.add_node("advance_phase", advance_phase)

    graph.add_edge(START, "decide_phase")
    graph.add_edge("decide_phase", "generate")
    graph.add_edge("generate", "advance_phase")
    graph.add_edge("advance_phase", END)
    return graph.compile()


_graph = None


def get_therapy_graph():
    """Singleton du graphe compilé."""
    global _graph
    if _graph is None:
        _graph = build_therapy_graph()
    return _graph


async def run_therapy_turn(
    history: list[dict[str, str]],
    user_message: str,
    language: str | None,
    goals: str | None,
    phase: str,
    turn_count: int,
) -> tuple[str, str, int]:
    """
    Exécute un tour de séance.

    Retourne (reply, next_phase, new_turn_count).
    """
    graph = get_therapy_graph()
    initial: TherapyState = {
        "history": history,
        "user_message": user_message,
        "language": language,
        "goals": goals,
        "phase": phase,
        "turn_count": turn_count,
        "reply": "",
        "next_phase": phase,
        "intent": "continue",
    }
    try:
        result = await graph.ainvoke(initial)
    except AIServiceError:
        raise
    except Exception as exc:
        logger.exception("LangGraph therapy turn failed")
        raise AIServiceError("unknown") from exc

    return (
        result["reply"],
        result["next_phase"],
        result["turn_count"],
    )
