"""
NeuroLens Cognitive Compiler (prototype)

Turns unstructured speech/text into structured, uncertainty-aware output:
literal meaning (Known), evidence-backed interpretations (Inferred), and
ambiguities with clarifying questions (Unknown).

Two execution paths, and the output always says which one produced it:

1. Local model path  - calls an OpenAI-compatible local endpoint (e.g. GenieX)
   and validates the JSON against the Pydantic schema below.
2. Rule-based path   - a deterministic fallback (regex + heuristics). It runs
   on the CPU, needs no model, and is used when the model is unreachable or
   its output fails validation.

STATUS: the model path has NOT yet been run or measured on Snapdragon
hardware. Nothing in this file claims NPU execution.
"""

import argparse
import json
import os
import re
import urllib.request
from typing import List, Literal, Optional, Tuple

from pydantic import BaseModel, Field, ValidationError

# ==============================================================================
# 1. Pydantic structured-output schemas
# ==============================================================================


class ActionItem(BaseModel):
    task: str = Field(description="Actionable task, close to the speaker's words")
    priority: Literal["low", "medium", "high"] = "medium"
    owner: Optional[str] = Field(default="unknown", description="Who should do it, or 'unknown'")


class DeadlineItem(BaseModel):
    task: str
    deadline: str
    detected_via: Literal["deterministic_rule", "llm_inference", "hybrid"] = "hybrid"


class InterpretationItem(BaseModel):
    interpretation: str = Field(description="A plausible reading, phrased as a possibility")
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: str = Field(description="Words from the input that support this reading")
    confidence_basis: str = Field(
        default="model-reported",
        description="Where the number comes from. Rule-based scores are heuristics, not probabilities.",
    )


class AmbiguityReport(BaseModel):
    level: Literal["low", "medium", "high"]
    reason: str
    missing_information: List[str] = Field(default_factory=list)


class NeuroLensInsight(BaseModel):
    source_text: str
    literal_meaning: str
    actions: List[ActionItem] = Field(default_factory=list)
    deadlines: List[DeadlineItem] = Field(default_factory=list)
    possible_interpretations: List[InterpretationItem] = Field(default_factory=list)
    ambiguity: AmbiguityReport
    clarifying_question: Optional[str] = None
    suggested_replies: List[str] = Field(default_factory=list)
    runtime_provenance: str = "unset"


# ==============================================================================
# 2. Deterministic rule engines
# ==============================================================================

_WEEKDAYS = "monday|tuesday|wednesday|thursday|friday|saturday|sunday"
_MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec"


def _cap(s: str) -> str:
    return s[:1].upper() + s[1:]


# (compiled regex, function turning the match into a display label)
DEADLINE_RULES = [
    (re.compile(rf"\b(?:before|by|on|until|till)\s+({_WEEKDAYS})\b"), lambda m: _cap(m.group(1))),
    (re.compile(rf"\bnext\s+(week|month|{_WEEKDAYS})\b"), lambda m: "Next " + _cap(m.group(1))),
    (re.compile(r"\b(tomorrow|tonight|today)\b"), lambda m: _cap(m.group(1))),
    (re.compile(r"\bkal\s+tak\b"), lambda m: "Tomorrow (kal tak)"),
    (
        re.compile(r"\b(?:by|before)\s+(\d{1,2}(?::\d{2})?)\s*(am|pm)\b"),
        lambda m: f"{m.group(1)} {m.group(2).upper()}",
    ),
    (
        re.compile(r"\b(?:by|before)\s+(lunch|end of day|eod|cob)\b"),
        lambda m: m.group(1).upper() if m.group(1) in ("eod", "cob") else _cap(m.group(1)),
    ),
    (
        re.compile(rf"\b(?:by|before|on)\s+((?:{_MONTHS})[a-z]*\.?\s+\d{{1,2}})\b"),
        lambda m: m.group(1).title(),
    ),
]

AMBIGUITY_RE = re.compile(
    r"\b(sometime|soon|later|maybe|we should|look into|quite there|thoda|when you can|"
    r"as soon as possible|probably be good|might want to|that part)\b"
)
SOFTENER_RE = re.compile(
    r"\b(it would probably be good|would be good if|would be great if|might want to|"
    r"could you|can you|you could|maybe|we should)\b"
)
DISSATISFACTION_RE = re.compile(
    r"\b(?:don't|do not|isn't|aren't|not)\b.{0,25}\bquite there\b|"
    r"\bneeds? to be (?:clearer|better|simpler)\b"
)
VAGUE_REFERENT_RE = re.compile(
    r"\b(?:look into|take care of|handle|deal with|sort out)\s+(that|this|it)\b"
)

ACTION_VERBS = (
    "send|get|update|revisit|revise|review|finish|complete|submit|prepare|create|make|fix|"
    "check|share|schedule|email|write|add|upload|call|book|draft|clean|test|deploy|push"
)
ACTION_RE = re.compile(rf"\b(?:{ACTION_VERBS})\b.*", re.IGNORECASE)
# Stop the task text where the deadline/softener starts.
_TASK_CUT_RE = re.compile(
    r"\s+\b(sometime|before|by|until|till|tomorrow|tonight|today|next|soon|later)\b.*$",
    re.IGNORECASE,
)
HINGLISH_ACTION_RE = re.compile(r"^(.*?\b(?:bana dena|kar dena|bhej dena|de dena|karna hai))\b", re.IGNORECASE)
_CLAUSE_SPLIT_RE = re.compile(r"[.?!]\s+|,\s*|\s+(?:and|aur|because|but)\s+", re.IGNORECASE)
_LEADING_FILLER_RE = re.compile(r"^(?:and|aur|but|also|maybe|please|jo)\s+", re.IGNORECASE)


def extract_deterministic_deadlines(text: str) -> List[str]:
    """Return display labels for obvious time expressions, without duplicates."""
    found: List[str] = []
    lowered = text.lower()
    for pattern, label in DEADLINE_RULES:
        for m in pattern.finditer(lowered):
            value = label(m)
            if value.lower() not in [f.lower() for f in found]:
                found.append(value)
    return found


def detect_ambiguity_signals(text: str) -> List[str]:
    seen: List[str] = []
    for m in AMBIGUITY_RE.finditer(text.lower()):
        if m.group(1) not in seen:
            seen.append(m.group(1))
    return seen


def _split_clauses(text: str) -> List[str]:
    clauses = []
    for raw in _CLAUSE_SPLIT_RE.split(text):
        clause = raw.strip()
        while True:  # peel off stacked filler words ("and maybe ...")
            stripped = _LEADING_FILLER_RE.sub("", clause)
            if stripped == clause:
                break
            clause = stripped
        if clause:
            clauses.append(clause)
    return clauses


def _extract_task(clause: str) -> Optional[str]:
    m = HINGLISH_ACTION_RE.match(clause)
    if m:
        task = m.group(1).strip()
        while True:  # drop a leading time phrase or filler; the deadline rule reads the full clause
            stripped = re.sub(r"^(?:kal tak|jo)\s+", "", task, flags=re.IGNORECASE)
            if stripped == task:
                return task
            task = stripped
    m = ACTION_RE.search(clause)
    if not m:
        return None
    task = _TASK_CUT_RE.sub("", m.group(0)).strip(" ,.;")
    return task or None


# ==============================================================================
# 3. Cognitive Compiler
# ==============================================================================

MODEL_PROMPT = """You convert spoken or written communication into JSON.
Rules: do not diagnose anyone, do not claim to know hidden intent, give evidence quoted
from the input for each interpretation, ask a clarifying question if information is missing,
and never invent a deadline. Return ONLY one JSON object with exactly these keys:
literal_meaning (string),
actions (list of {task, priority: low|medium|high, owner}),
deadlines (list of {task, deadline, detected_via: "llm_inference"}),
possible_interpretations (list of {interpretation, confidence: 0..1, evidence}),
ambiguity ({level: low|medium|high, reason, missing_information: [strings]}),
clarifying_question (string or null),
suggested_replies (list of up to 3 short strings).

Input text (JSON-encoded): %s
/no_think"""


class CognitiveCompiler:
    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: float = 20.0,
        use_model: bool = True,
    ):
        base = endpoint_url or os.environ.get("NEUROLENS_ENDPOINT", "http://127.0.0.1:18181/v1")
        self.endpoint_url = base.rstrip("/")
        # Must match the model id your local server exposes; set NEUROLENS_MODEL to change it.
        self.model_name = model_name or os.environ.get("NEUROLENS_MODEL", "qwen3-0.6b")
        self.timeout = timeout
        self.use_model = use_model

    # ---- public API ----------------------------------------------------------
    def compile(self, text: str) -> NeuroLensInsight:
        text = text.strip()
        reason = "model disabled"
        if self.use_model:
            raw, reason = self._call_model(text)
            if raw is not None:
                try:
                    data = json.loads(self._extract_json(raw))
                    data["source_text"] = text
                    data["runtime_provenance"] = (
                        f"Local model '{self.model_name}' via {self.endpoint_url}; "
                        "deadlines cross-checked by rules. Hardware (CPU/NPU) not verified by this script."
                    )
                    insight = NeuroLensInsight.model_validate(data)
                    self._enrich_with_rules(insight, text)
                    return insight
                except (ValueError, ValidationError):
                    reason = "model output failed schema validation"
        insight = self._rule_compile(text)
        label = "Rule-based engine (no model used)" if not self.use_model else "Rule-based fallback"
        insight.runtime_provenance = f"{label} - {reason}. Runs on CPU."
        return insight

    # ---- local model path ----------------------------------------------------
    def _call_model(self, text: str) -> Tuple[Optional[str], str]:
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": MODEL_PROMPT % json.dumps(text)}],
            "temperature": 0.1,
        }
        req = urllib.request.Request(
            f"{self.endpoint_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"], ""
        except Exception as exc:  # network, HTTP, or malformed response
            return None, f"model unreachable or bad response ({type(exc).__name__})"

    @staticmethod
    def _extract_json(raw: str) -> str:
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
        raw = re.sub(r"```(?:json)?", "", raw)
        start, end = raw.find("{"), raw.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("no JSON object in model output")
        return raw[start : end + 1]

    def _enrich_with_rules(self, insight: NeuroLensInsight, text: str) -> None:
        existing = {d.deadline.lower() for d in insight.deadlines}
        for label in extract_deterministic_deadlines(text):
            if label.lower() not in existing:
                task = insight.actions[0].task if insight.actions else "General request"
                insight.deadlines.append(
                    DeadlineItem(task=task, deadline=label, detected_via="deterministic_rule")
                )

    # ---- rule-based path -----------------------------------------------------
    def _rule_compile(self, text: str) -> NeuroLensInsight:
        actions: List[ActionItem] = []
        deadlines: List[DeadlineItem] = []
        for clause in _split_clauses(text):
            task = _extract_task(clause)
            clause_deadlines = extract_deterministic_deadlines(clause)
            if task:
                actions.append(
                    ActionItem(task=task, priority="high" if clause_deadlines else "medium", owner="unknown")
                )
            for label in clause_deadlines:
                ref = task or (actions[0].task if actions else "General request")
                if not any(d.deadline.lower() == label.lower() and d.task == ref for d in deadlines):
                    deadlines.append(DeadlineItem(task=ref, deadline=label, detected_via="deterministic_rule"))

        markers = detect_ambiguity_signals(text)
        referent = VAGUE_REFERENT_RE.search(text.lower())
        dissatisfied = DISSATISFACTION_RE.search(text.lower())

        # --- uncertainty engine: transparent additive score ---
        score = min(len(markers), 2)
        missing: List[str] = []
        if referent:
            score += 2
            missing.append(f"What '{referent.group(1)}' refers to")
        if markers and not actions:
            score += 2
            missing.append("A specific task")
        if actions and not deadlines:
            score += 1
            missing.append("A deadline")
        if dissatisfied:
            missing.append("Which part should change, and how")
        level = "low" if score <= 1 else "medium" if score == 2 else "high"

        reason_bits = []
        if markers:
            reason_bits.append("vague wording: " + ", ".join(markers))
        reason_bits.extend(f"missing: {m.lower()}" for m in missing)
        reason = "; ".join(reason_bits) if reason_bits else "The request is direct and specific."

        return NeuroLensInsight(
            source_text=text,
            literal_meaning=self._literal_meaning(text, actions, deadlines),
            actions=actions,
            deadlines=deadlines,
            possible_interpretations=self._interpretations(text, actions, deadlines, markers, dissatisfied),
            ambiguity=AmbiguityReport(level=level, reason=reason, missing_information=missing),
            clarifying_question=self._clarifying_question(missing),
            suggested_replies=self._replies(actions, deadlines),
        )

    @staticmethod
    def _literal_meaning(text, actions, deadlines) -> str:
        if not actions:
            return f"No explicit request found. The speaker said: \"{text}\""
        parts = "Requested actions: " + "; ".join(a.task for a in actions) + "."
        if deadlines:
            parts += " Time mentioned: " + ", ".join(sorted({d.deadline for d in deadlines})) + "."
        return parts

    @staticmethod
    def _interpretations(text, actions, deadlines, markers, dissatisfied) -> List[InterpretationItem]:
        basis = "heuristic score from matched signals, not a model probability"
        out: List[InterpretationItem] = []
        softener = SOFTENER_RE.search(text.lower())
        if softener and (actions or deadlines):
            score = 0.5 + (0.1 if deadlines else 0.0) + (0.1 if actions else 0.0)
            evidence = f"'{softener.group(1)}'"
            if deadlines:
                evidence += f" + time '{deadlines[0].deadline}'"
            out.append(
                InterpretationItem(
                    interpretation="This may be a real request phrased politely, not just a suggestion.",
                    confidence=round(score, 2),
                    evidence=evidence,
                    confidence_basis=basis,
                )
            )
        if dissatisfied:
            out.append(
                InterpretationItem(
                    interpretation="The speaker may want improvements, but has not said what to change.",
                    confidence=0.55,
                    evidence=f"'{dissatisfied.group(0).strip()}'",
                    confidence_basis=basis,
                )
            )
        if markers and not actions:
            out.append(
                InterpretationItem(
                    interpretation="This may be a low-urgency idea with no task assigned yet.",
                    confidence=0.5,
                    evidence="vague wording: " + ", ".join(markers),
                    confidence_basis=basis,
                )
            )
        return out

    @staticmethod
    def _clarifying_question(missing: List[str]) -> Optional[str]:
        if not missing:
            return None
        questions = []
        for m in missing:
            if m.startswith("What '"):
                questions.append(f"{m.replace('What', 'What does', 1).replace(' refers to', ' refer to')}?")
            elif m == "A specific task":
                questions.append("What specifically would you like done?")
            elif m == "A deadline":
                questions.append("When would you like this completed?")
            else:
                questions.append("Which part should be changed, and how?")
        return " ".join(questions[:2])

    @staticmethod
    def _replies(actions, deadlines) -> List[str]:
        if not actions:
            return [
                "Could you tell me what specifically you'd like me to do, and by when?",
                "Happy to help - what's the exact task?",
            ]
        replies = ["Understood. Could you confirm the details you'd like me to focus on?"]
        if deadlines:
            when = deadlines[0].deadline.split(" (")[0].lower() if deadlines[0].deadline.startswith("Tomorrow") else deadlines[0].deadline
            replies.insert(0, f"Got it - I'll aim to have this ready by {when}.")
            replies.append(f"Noted, {when}. I'll follow up if anything is unclear.")
        else:
            replies.insert(0, "Got it. When would you like this done by?")
        return replies


# ==============================================================================
# 4. Command-line interface
# ==============================================================================


def _print_report(insight: NeuroLensInsight) -> None:
    line = "=" * 70
    print(line)
    print("NEUROLENS COGNITIVE COMPILER OUTPUT")
    print(line)
    print(f'\n[SOURCE]\n"{insight.source_text}"')
    print(f"\n[1. LITERAL MEANING - KNOWN]\n{insight.literal_meaning}")
    print("\n[2. ACTIONS]")
    if insight.actions:
        for i, a in enumerate(insight.actions, 1):
            print(f"  {i}. [ ] {a.task} (priority: {a.priority})")
    else:
        print("  (no explicit action found)")
    print("\n[3. DEADLINES]")
    if insight.deadlines:
        for d in insight.deadlines:
            print(f"  - {d.deadline} <- {d.task} ({d.detected_via})")
    else:
        print("  (none stated)")
    print("\n[4. POSSIBLE INTERPRETATIONS - INFERRED]")
    if insight.possible_interpretations:
        for p in insight.possible_interpretations:
            print(f"  - {p.interpretation}")
            print(f'    score {int(p.confidence * 100)}% ({p.confidence_basis}) | evidence: {p.evidence}')
    else:
        print("  (none)")
    print("\n[5. AMBIGUITY - UNKNOWN]")
    print(f"  level: {insight.ambiguity.level.upper()}")
    print(f"  why:   {insight.ambiguity.reason}")
    if insight.clarifying_question:
        print(f'\n[6. CLARIFYING QUESTION]\n  "{insight.clarifying_question}"')
    print("\n[7. SUGGESTED REPLIES]")
    for r in insight.suggested_replies:
        print(f'  -> "{r}"')
    print(f"\n[RUNTIME]\n{insight.runtime_provenance}")
    print(line)


def main() -> None:
    parser = argparse.ArgumentParser(description="NeuroLens Cognitive Compiler prototype")
    parser.add_argument("input", nargs="?", help="Text, or path to a .txt file (default: samples/meeting_01.txt)")
    parser.add_argument("--json", action="store_true", help="Print the validated JSON instead of the report")
    parser.add_argument("--no-model", action="store_true", help="Skip the local model; use rule-based engine only")
    parser.add_argument("--endpoint", help="OpenAI-compatible base URL (default http://127.0.0.1:18181/v1)")
    parser.add_argument("--model", help="Model id exposed by the local server")
    parser.add_argument("--timeout", type=float, default=20.0, help="Seconds to wait for the model")
    args = parser.parse_args()

    if not args.input:
        args.input = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples", "meeting_01.txt")
    if os.path.isfile(args.input):
        with open(args.input, "r", encoding="utf-8") as f:
            raw_text = f.read().strip()
    else:
        raw_text = args.input

    compiler = CognitiveCompiler(
        endpoint_url=args.endpoint, model_name=args.model, timeout=args.timeout, use_model=not args.no_model
    )
    insight = compiler.compile(raw_text)
    if args.json:
        print(insight.model_dump_json(indent=2))
    else:
        _print_report(insight)


if __name__ == "__main__":
    main()
