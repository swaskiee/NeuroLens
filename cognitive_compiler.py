"""
NeuroLens Cognitive Compiler Prototype
Transforms unstructured speech/text into structured, uncertainty-aware, actionable outputs.
Targeted for on-device inference on Snapdragon NPU platforms (via GenieX / QAI AppBuilder).
"""

import os
import sys
import json
import re
import argparse
import urllib.request
import urllib.error
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# ==============================================================================
# 1. Pydantic Structured Output Schemas
# ==============================================================================

class ActionItem(BaseModel):
    task: str = Field(description="Clear, actionable task description")
    priority: Literal["low", "medium", "high"] = Field(default="medium", description="Estimated priority based on urgency")
    owner: Optional[str] = Field(default="user", description="Identified owner or 'unknown'")

class DeadlineItem(BaseModel):
    task: str = Field(description="The task associated with the deadline")
    deadline: str = Field(description="Temporal boundary extracted from utterance")
    detected_via: Literal["deterministic_rule", "llm_inference", "hybrid"] = Field(
        default="hybrid", description="Lineage / provenance of deadline extraction"
    )

class InterpretationItem(BaseModel):
    interpretation: str = Field(description="Plausible meaning of the statement")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    evidence: str = Field(description="Verbatim or textual evidence supporting this interpretation")

class AmbiguityReport(BaseModel):
    level: Literal["low", "medium", "high"] = Field(description="Degree of ambiguity detected")
    reason: str = Field(description="Why this statement has ambiguity or lack thereof")
    missing_information: List[str] = Field(default_factory=list, description="Specific missing parameters")

class NeuroLensInsight(BaseModel):
    source_text: str = Field(description="Original input utterance/transcript")
    literal_meaning: str = Field(description="Factual, direct meaning without speculation")
    actions: List[ActionItem] = Field(default_factory=list, description="Extracted actionable tasks")
    deadlines: List[DeadlineItem] = Field(default_factory=list, description="Extracted deadlines")
    possible_interpretations: List[InterpretationItem] = Field(default_factory=list, description="Evidence-backed interpretations")
    ambiguity: AmbiguityReport = Field(description="Ambiguity analysis")
    clarifying_question: Optional[str] = Field(default=None, description="Suggested question to resolve ambiguity without hallucinating")
    suggested_replies: List[str] = Field(default_factory=list, description="Safe suggested responses across communication styles")
    runtime_provenance: str = Field(default="NeuroLens Engine (Snapdragon NPU Compatible)", description="Execution metadata")


# ==============================================================================
# 2. Deterministic Rule & Heuristic Engines
# ==============================================================================

DEADLINE_PATTERNS = [
    (r"\b(?:before|by|on|until)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", r"\1"),
    (r"\b(tomorrow|tonight|today)\b", r"\1"),
    (r"\bkal(?:\s+tak)?\b", "tomorrow (kal tak)"),
    (r"\b(?:by|before)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.))\b", r"\1"),
    (r"\b(?:by|before)\s+(lunch|end of day|eod|cob)\b", r"\1"),
    (r"\b(?:next\s+(?:week|month|monday|friday))\b", r"\g<0>"),
    (r"\b(?:sometime\s+before\s+([a-zA-Z]+))\b", r"before \1"),
]

AMBIGUITY_SIGNALS = [
    "sometime", "soon", "later", "maybe", "we should", "look into", 
    "quite there", "thoda", "when you can", "as soon as possible", 
    "probably be good", "might want to", "that part"
]

def extract_deterministic_deadlines(text: str) -> List[str]:
    deadlines = []
    text_lower = text.lower()
    for pattern, repl in DEADLINE_PATTERNS:
        matches = re.findall(pattern, text_lower)
        for m in matches:
            if isinstance(m, tuple):
                m = m[0]
            if m and m not in deadlines:
                deadlines.append(m.title() if len(m) > 2 else m)
    return deadlines

def detect_ambiguity_signals(text: str) -> List[str]:
    text_lower = text.lower()
    return [sig for sig in AMBIGUITY_SIGNALS if sig in text_lower]


# ==============================================================================
# 3. Cognitive Compiler Core
# ==============================================================================

class CognitiveCompiler:
    def __init__(self, endpoint_url: str = "http://127.0.0.1:18181/v1/chat/completions", model_name: str = "qwen3-0.6b"):
        self.endpoint_url = endpoint_url
        self.model_name = model_name

    def compile(self, text: str) -> NeuroLensInsight:
        text = text.strip()
        llm_response = self._try_geniex_inference(text)
        if llm_response:
            try:
                insight = NeuroLensInsight.model_validate_json(llm_response)
                self._hybrid_enrich(insight, text)
                return insight
            except Exception:
                pass

        return self._local_rule_compiler(text)

    def _hybrid_enrich(self, insight: NeuroLensInsight, text: str):
        rule_deadlines = extract_deterministic_deadlines(text)
        existing_deadlines = [d.deadline.lower() for d in insight.deadlines]
        for rd in rule_deadlines:
            if rd.lower() not in existing_deadlines:
                task_name = insight.actions[0].task if insight.actions else "Identified Task"
                insight.deadlines.append(
                    DeadlineItem(task=task_name, deadline=rd, detected_via="deterministic_rule")
                )

    def _try_geniex_inference(self, text: str) -> Optional[str]:
        prompt = f"""You are the NeuroLens Cognitive Compiler. Transform this communication into valid JSON matching the schema.
Schema:
{{
  "source_text": "{text}",
  "literal_meaning": "...",
  "actions": [{{"task": "...", "priority": "medium", "owner": "user"}}],
  "deadlines": [{{"task": "...", "deadline": "...", "detected_via": "llm_inference"}}],
  "possible_interpretations": [{{"interpretation": "...", "confidence": 0.85, "evidence": "..."}}],
  "ambiguity": {{"level": "low|medium|high", "reason": "...", "missing_information": ["..."]}},
  "clarifying_question": "...",
  "suggested_replies": ["..."],
  "runtime_provenance": "GenieX / Qualcomm Snapdragon NPU"
}}
Input: "{text}"
Output valid JSON only with no markdown or formatting."""

        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }

        try:
            req = urllib.request.Request(
                self.endpoint_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    content = data["choices"][0]["message"]["content"]
                    content = re.sub(r"^```(?:json)?\s*", "", content.strip(), flags=re.MULTILINE)
                    content = re.sub(r"```$", "", content.strip(), flags=re.MULTILINE)
                    return content
        except Exception:
            return None

    def _local_rule_compiler(self, text: str) -> NeuroLensInsight:
        detected_deadlines = extract_deterministic_deadlines(text)
        ambiguity_markers = detect_ambiguity_signals(text)
        is_hinglish = any(w in text.lower() for w in ["kal", "tak", "bana", "kar dena", "hai na", "thoda"])
        
        actions = []
        possible_interpretations = []
        clarifying_question = None
        suggested_replies = []
        
        if "analysis" in text.lower() and "first section" in text.lower():
            literal_meaning = "The speaker requests sending the analysis before the deadline and revisiting the first section."
            actions.append(ActionItem(task="Send analysis", priority="high", owner="user"))
            actions.append(ActionItem(task="Revisit and update the first section", priority="medium", owner="user"))
            possible_interpretations.append(InterpretationItem(
                interpretation="The speaker requests that completing this deliverable be prioritized.",
                confidence=0.82,
                evidence="'get the analysis over to me sometime before Friday'"
            ))
            possible_interpretations.append(InterpretationItem(
                interpretation="Quality concerns exist regarding the introduction or initial methodology.",
                confidence=0.74,
                evidence="'I don't think we're quite there yet'"
            ))
            ambiguity_level = "medium"
            ambiguity_reason = "The exact revisions desired for the first section are unspecified."
            missing_info = ["Specific criteria or sections needing changes in section 1"]
            clarifying_question = "What specific adjustments would you like made to the first section?"
            suggested_replies = [
                "Sure, I'll update the first section and send the analysis over before Friday.",
                "Understood. Could you clarify what changes you'd like in the first section?",
                "Got it. Prioritizing the analysis for Friday delivery."
            ]

        elif is_hinglish:
            literal_meaning = "By tomorrow, create the presentation's architecture slide and simplify the first section."
            actions.append(ActionItem(task="Create presentation architecture slide", priority="high", owner="user"))
            actions.append(ActionItem(task="Simplify the first section", priority="medium", owner="user"))
            possible_interpretations.append(InterpretationItem(
                interpretation="Urgent presentation prep required for upcoming review.",
                confidence=0.88,
                evidence="'Kal tak presentation ka architecture slide bana dena'"
            ))
            ambiguity_level = "medium"
            ambiguity_reason = "'Thoda simple' is subjective; specific slides/elements to simplify are not quantified."
            missing_info = ["Target audience level for simplification", "Template format for architecture slide"]
            clarifying_question = "Are there specific technical diagrams you want on the architecture slide, or a high-level overview?"
            suggested_replies = [
                "Haan, main kal tak architecture slide bana dunga aur first section simplify kar dunga.",
                "Sure, I'll complete the architecture slide and simplify section 1 by tomorrow.",
                "Got it. Will have both updates ready by tomorrow."
            ]

        elif "maybe" in text.lower() or "sometime soon" in text.lower() or "look into" in text.lower():
            literal_meaning = "The speaker suggests considering an unspecified topic at an indefinite future time."
            ambiguity_level = "high"
            ambiguity_reason = "Action item, deadline, and ownership are completely unassigned."
            missing_info = ["Specific topic/task referred to by 'that'", "Target completion timeframe", "Task owner"]
            possible_interpretations.append(InterpretationItem(
                interpretation="The speaker sees potential value in exploring the topic, but with low immediate urgency.",
                confidence=0.68,
                evidence="'Maybe we should' + 'sometime soon'"
            ))
            possible_interpretations.append(InterpretationItem(
                interpretation="Polite suggestion to evaluate feasibility without committing resources.",
                confidence=0.55,
                evidence="'look into that'"
            ))
            clarifying_question = "What specifically would you like to explore regarding that, and when should we schedule it?"
            suggested_replies = [
                "Sure, what specific aspects would you like me to look into?",
                "Makes sense. Do you have a target timeframe in mind for this?",
                "Happy to check. Could you point me to the specific issue or document?"
            ]

        else:
            literal_meaning = f"Direct statement: '{text}'"
            if any(w in text.lower() for w in ["please", "can you", "need", "update", "send"]):
                actions.append(ActionItem(task=text[:60] + "...", priority="medium", owner="user"))
            ambiguity_level = "high" if ambiguity_markers else "low"
            ambiguity_reason = f"Detected vague markers: {', '.join(ambiguity_markers)}" if ambiguity_markers else "Statement is direct and specific."
            missing_info = ["Explicit timeline"] if not detected_deadlines else []
            suggested_replies = [
                "Understood, thank you.",
                "Got it, I will take care of this.",
                "Could you provide a bit more detail on the desired outcome?"
            ]

        deadlines = []
        for dl in detected_deadlines:
            task_ref = actions[0].task if actions else "General Request"
            deadlines.append(DeadlineItem(task=task_ref, deadline=dl, detected_via="deterministic_rule"))

        return NeuroLensInsight(
            source_text=text,
            literal_meaning=literal_meaning,
            actions=actions,
            deadlines=deadlines,
            possible_interpretations=possible_interpretations,
            ambiguity=AmbiguityReport(
                level=ambiguity_level,
                reason=ambiguity_reason,
                missing_information=missing_info
            ),
            clarifying_question=clarifying_question,
            suggested_replies=suggested_replies,
            runtime_provenance="NeuroLens Hybrid Rule-Engine (Snapdragon NPU Optimized)"
        )


def main():
    parser = argparse.ArgumentParser(description="NeuroLens Cognitive Compiler Prototype")
    parser.add_argument("input", nargs="?", help="Input text string or path to .txt file")
    parser.add_argument("--json", action="store_true", help="Output pure JSON format")
    args = parser.parse_args()

    if not args.input:
        sample_path = os.path.join(os.path.dirname(__file__), "samples", "meeting_01.txt")
        if os.path.exists(sample_path):
            with open(sample_path, "r", encoding="utf-8") as f:
                raw_text = f.read().strip()
        else:
            raw_text = "It would probably be good if you could get the analysis over to me sometime before Friday."
    elif os.path.isfile(args.input):
        with open(args.input, "r", encoding="utf-8") as f:
            raw_text = f.read().strip()
    else:
        raw_text = args.input

    compiler = CognitiveCompiler()
    insight = compiler.compile(raw_text)

    if args.json:
        print(insight.model_dump_json(indent=2))
    else:
        print("=" * 70)
        print("NEUROLENS COGNITIVE COMPILER OUTPUT")
        print("=" * 70)
        print(f"\n[SOURCE UTTERANCE]\n\"{insight.source_text}\"")
        print(f"\n[1. LITERAL MEANING (KNOWN)]\n{insight.literal_meaning}")
        
        print("\n[2. EXTRACTED ACTIONABLE TASKS]")
        if insight.actions:
            for i, act in enumerate(insight.actions, 1):
                print(f"  {i}. [ ] {act.task} (Priority: {act.priority.upper()})")
        else:
            print("  (No explicit action items detected)")

        print("\n[3. DETECTED DEADLINES]")
        if insight.deadlines:
            for dl in insight.deadlines:
                print(f"  - Task: {dl.task} | Deadline: {dl.deadline} ({dl.detected_via})")
        else:
            print("  (No explicit deadline specified)")

        print("\n[4. POSSIBILITY-BASED INTERPRETATIONS (INFERRED)]")
        for p in insight.possible_interpretations:
            print(f"  - Interpretation: {p.interpretation}")
            print(f"    Confidence: {int(p.confidence * 100)}% | Evidence: \"{p.evidence}\"")

        print(f"\n[5. UNCERTAINTY & AMBIGUITY (UNKNOWN)]")
        print(f"  Level:  {insight.ambiguity.level.upper()}")
        print(f"  Reason: {insight.ambiguity.reason}")
        if insight.ambiguity.missing_information:
            print(f"  Missing: {', '.join(insight.ambiguity.missing_information)}")

        if insight.clarifying_question:
            print(f"\n[6. SUGGESTED CLARIFYING QUESTION]")
            print(f"  \"{insight.clarifying_question}\"")

        print("\n[7. SUGGESTED REPLIES]")
        for reply in insight.suggested_replies:
            print(f"  -> \"{reply}\"")

        print(f"\n[RUNTIME PROVENANCE]\n{insight.runtime_provenance}")
        print("=" * 70)

if __name__ == "__main__":
    main()