"""
Unit tests for NeuroLens Cognitive Compiler.
Verifies schema compliance, deterministic deadline extraction, and uncertainty handling.
"""

import pytest
from cognitive_compiler import (
    CognitiveCompiler,
    NeuroLensInsight,
    extract_deterministic_deadlines,
    detect_ambiguity_signals
)

@pytest.fixture
def compiler():
    return CognitiveCompiler()

def test_meeting_scenario_compilation(compiler):
    text = "It would probably be good if you could get the analysis over to me sometime before Friday. And maybe revisit the first section because I don't think we're quite there yet."
    insight = compiler.compile(text)
    
    assert isinstance(insight, NeuroLensInsight)
    assert len(insight.actions) == 2
    assert any("analysis" in act.task.lower() for act in insight.actions)
    assert any("first section" in act.task.lower() for act in insight.actions)
    assert any(d.deadline.lower() == "friday" for d in insight.deadlines)
    assert insight.ambiguity.level == "medium"
    assert insight.clarifying_question is not None
    assert len(insight.suggested_replies) >= 2

def test_ambiguous_scenario_compilation(compiler):
    text = "Maybe we should look into that sometime soon."
    insight = compiler.compile(text)
    
    assert isinstance(insight, NeuroLensInsight)
    assert len(insight.actions) == 0
    assert insight.ambiguity.level == "high"
    assert "Missing" in str(insight.ambiguity.missing_information) or len(insight.ambiguity.missing_information) > 0
    assert "specifically" in insight.clarifying_question.lower()

def test_hinglish_scenario_compilation(compiler):
    text = "Kal tak presentation ka architecture slide bana dena, aur jo first section hai na usko thoda simple kar dena."
    insight = compiler.compile(text)
    
    assert isinstance(insight, NeuroLensInsight)
    assert len(insight.actions) >= 2
    assert any("architecture slide" in act.task.lower() for act in insight.actions)
    assert insight.ambiguity.level == "medium"
    assert any("kal tak" in d.deadline.lower() for d in insight.deadlines)

def test_deterministic_deadline_extraction():
    assert "Friday" in extract_deterministic_deadlines("Send it by Friday morning")
    assert "Tomorrow" in extract_deterministic_deadlines("Please finish this tomorrow")
    assert "5 Pm" in extract_deterministic_deadlines("Submit report before 5 pm")

def test_ambiguity_signal_detection():
    signals = detect_ambiguity_signals("Maybe we could look into that sometime soon")
    assert "maybe" in signals
    assert "sometime" in signals
    assert "soon" in signals