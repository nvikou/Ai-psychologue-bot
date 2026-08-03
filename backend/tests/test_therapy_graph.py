"""Tests du routage de phases (sans mots-clés)."""

from app.services.therapy_graph import _parse_intent
from app.services.therapy_graph import intent_to_phase


def test_parse_intent_confirm() -> None:
    assert _parse_intent("confirm") == "confirm"
    assert _parse_intent("CONFIRM\n") == "confirm"


def test_parse_intent_unknown_fallback() -> None:
    assert _parse_intent("maybe?") == "continue"


def test_intent_listen_first_turn() -> None:
    assert intent_to_phase("listen", "continue", 0) == "listen"


def test_intent_explore_ready_reflect() -> None:
    assert intent_to_phase("explore", "ready_reflect", 2) == "reflect"


def test_intent_reflect_confirm_advise() -> None:
    assert intent_to_phase("reflect", "confirm", 3) == "advise"


def test_intent_reflect_correct_explore() -> None:
    assert intent_to_phase("reflect", "correct", 3) == "explore"


def test_intent_advise_then_explore() -> None:
    assert intent_to_phase("advise", "continue", 4) == "explore"
