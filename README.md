# NeuroLens
 
**Private, on-device AI for cognitive accessibility, designed for Snapdragon Windows PCs.**
 
> *Understand the moment. Organize the thought. Keep everything private.*
 
Entry for the **Snapdragon® AI Lab Build & Present Challenge 2026** (Qualcomm / Unstop), individual submission.
 
 
## Status (read this first)
 
This repository is a **proposal plus a working, tested prototype of the core logic**. It is not yet the full application, and nothing here has been measured on Snapdragon hardware yet.
 
| Area | State |
|---|---|
| Structured-output schema (Pydantic) | Implemented, tested |
| Rule-based Cognitive Compiler: actions, deadlines, ambiguity scoring, clarifying questions, evidence-linked interpretations | Implemented, tested (CPU) |
| Local-model client (OpenAI-compatible endpoint, JSON validation, automatic fallback) | Implemented; tested with a stubbed model. **Not yet run against a real GenieX server** |
| Speech input (VAD + Whisper-Base), screenshot input (Qwen3-VL), Focus Mode, SQLite memory, Privacy Center UI, Streamlit UI | **Planned**, not started |
| NPU execution, latency and accuracy benchmarks | **Not measured yet** |
 
Every result printed by the prototype states which engine produced it (see `[RUNTIME]` in the sample output below).
 
## The problem
 
Fast, indirect communication ("it would probably be good if you could get that over before Friday...") is hard to turn into clear next steps. That is costly for students in lectures, professionals in meetings, and anyone who benefits from less cognitive load. Cloud assistants can help, but they require sending conversations and screen content to a remote service.
 
NeuroLens is an accessibility and productivity aid. It is **not** a medical tool and does not diagnose or treat any condition.
 
## The idea: a Cognitive Compiler with Known / Inferred / Unknown
 
Instead of a free-form chat reply, NeuroLens compiles messy language into a fixed, validated structure:
 
- **Known**: literal meaning, explicit tasks, and deadlines found by deterministic rules.
- **Inferred**: possible readings of ambiguous wording, each with the words that support it. It never states hidden intent as fact.
- **Unknown**: what is missing (task, deadline, referent), with a clarifying question instead of a guess.
## Architecture
 
```
 Microphone ─► VAD ─► Whisper-Base ─┐                       [planned]
 Screenshot ─► Qwen3-VL-4B ─────────┤                       [planned]
 Typed text ────────────────────────┤                       [implemented]
                                    ▼
                          Cognitive Compiler                [implemented]
              (local model via GenieX  +  rule engines)     model path: written, not yet run on device
                                    ▼
                          Pydantic validation               [implemented]
                                    ▼
             Tasks / Focus Mode / local SQLite / UI         [planned]
```
 
AI inference is intended to run on the Snapdragon NPU where supported. The UI, storage and rule logic run on the CPU.
 
## Snapdragon plan (targets, not results)
 
| Role | Candidate model | Intended runtime | Status |
|---|---|---|---|
| Speech-to-text | Whisper-Base | Qualcomm AI Hub / QAI AppBuilder | Not yet run on my device |
| Reasoning (compiler) | Qwen3-0.6B (Phi-4-Mini as alternative) | GenieX local OpenAI-compatible server | Client written; not yet run on my device |
| Screen understanding | Qwen3-VL-4B-Instruct | GenieX | Planned |
 
These models are listed on Qualcomm AI Hub for Snapdragon X-series devices. Whether each one runs on the NPU of my specific machine, and how fast, will be verified and reported here. No performance numbers are claimed until then.
 
## Privacy design goals
 
Design principles for the full application (not yet implemented):
 
- Raw audio and screenshots are processed in memory and discarded; nothing is saved unless the user chooses to save it.
- Memory holds user-approved preferences, not conversation logs.
- No cloud AI service is required for core inference. Offline behavior will be tested and documented before being claimed.
## Try the prototype
 
```bash
pip install -r requirements.txt
 
# Rule-based engine only (no model needed)
python cognitive_compiler.py samples/meeting_01.txt --no-model
python cognitive_compiler.py samples/ambiguous_01.txt --no-model
python cognitive_compiler.py samples/hinglish_01.txt --no-model
python cognitive_compiler.py samples/meeting_01.txt --no-model --json
 
# With a local OpenAI-compatible server (for example GenieX at http://127.0.0.1:18181/v1)
python cognitive_compiler.py samples/meeting_01.txt --model <model-id-your-server-exposes>
 
# Tests (no network or model required)
python -m pytest tests -v
```
 
If the model is unreachable or returns output that fails validation, the compiler falls back to the rule-based engine and says so in the output.
 
## Real output (rule-based engine, `--no-model`)
 
```text
======================================================================
NEUROLENS COGNITIVE COMPILER OUTPUT
======================================================================
 
[SOURCE]
"It would probably be good if you could get the analysis over to me sometime before Friday. And maybe revisit the first section because I don't think we're quite there yet."
 
[1. LITERAL MEANING - KNOWN]
Requested actions: get the analysis over to me; revisit the first section. Time mentioned: Friday.
 
[2. ACTIONS]
  1. [ ] get the analysis over to me (priority: high)
  2. [ ] revisit the first section (priority: medium)
 
[3. DEADLINES]
  - Friday <- get the analysis over to me (deterministic_rule)
 
[4. POSSIBLE INTERPRETATIONS - INFERRED]
  - This may be a real request phrased politely, not just a suggestion.
    score 70% (heuristic score from matched signals, not a model probability) | evidence: 'it would probably be good' + time 'Friday'
  - The speaker may want improvements, but has not said what to change.
    score 55% (heuristic score from matched signals, not a model probability) | evidence: 'don't think we're quite there'
 
[5. AMBIGUITY - UNKNOWN]
  level: MEDIUM
  why:   vague wording: probably be good, sometime, maybe, quite there; missing: which part should change, and how
 
[6. CLARIFYING QUESTION]
  "Which part should be changed, and how?"
 
[7. SUGGESTED REPLIES]
  -> "Got it - I'll aim to have this ready by Friday."
  -> "Understood. Could you confirm the details you'd like me to focus on?"
  -> "Noted, Friday. I'll follow up if anything is unclear."
 
[RUNTIME]
Rule-based engine (no model used) - model disabled. Runs on CPU.
======================================================================
```
 
The interpretation scores from the rule engine are heuristic signals, not model probabilities, and are labelled that way.
 
## Evaluation plan (targets, not results)
 
- A small hand-labelled set of about 30 utterances (explicit tasks, deadlines, ambiguous statements, multiple tasks, Hinglish).
- Metrics: task precision and recall, deadline accuracy, ambiguity classification accuracy.
- On-device measurements once the models run: ASR latency, time to first token, end-to-end latency, and CPU versus NPU comparison.
- Offline test: disable the network and confirm core processing still works.
## Known limitations
 
- The rule-based engine is pattern matching. It handles common phrasings and will miss many others. That is why the model path exists.
- Task text is extracted close to the speaker's wording, not rewritten.
- Hinglish support is minimal (a few common verb patterns).
- No speech, vision, memory or UI yet.
## Roadmap
 
1. Run GenieX with Qwen3-0.6B on the Snapdragon laptop and record real output and timings.
2. Add Whisper-Base transcription from an audio file, then live microphone input.
3. Simple UI, task creation, and Focus Mode.
4. Local memory and Privacy Center.
5. Screenshot understanding with Qwen3-VL.
## Repository layout
 
```
cognitive_compiler.py   core prototype
generate_deck.py        builds docs/NeuroLens_Pitch_Deck.pptx
samples/                three example inputs
tests/                  pytest suite
docs/                   project description and pitch deck
```
 
## License
 
See [LICENSE](LICENSE).
 
