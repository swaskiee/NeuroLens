<div align="center">

# 🧠 NeuroLens

### **Private, On-Device AI for Cognitive Accessibility**
#### *Designed, Developed & Optimized for Snapdragon®-Powered Windows PCs*

<p align="center">
  <em>"Understand the moment. Organize the thought. Keep everything private."</em>
</p>

[![Snapdragon AI Lab](https://img.shields.io/badge/Snapdragon%C2%AE_AI_Lab-Challenge_2026-E02020?style=for-the-badge&logo=qualcomm&logoColor=white)](https://unstop.com/competitions/1748893)
[![Platform](https://img.shields.io/badge/Platform-Windows_11_ARM64-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://www.qualcomm.com/laptops/products/snapdragon-x-elite)
[![NPU Target](https://img.shields.io/badge/NPU_Target-Hexagon%E2%84%A2_45_TOPS-00C853?style=for-the-badge)](https://www.qualcomm.com/laptops/products/snapdragon-x-elite)
[![Status](https://img.shields.io/badge/Status-Prototype_Verified_%E2%9C%93-blueviolet?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-Apache_2.0-orange?style=for-the-badge)](LICENSE)

---

**Individual Submission for the Snapdragon® AI Lab Build & Present Challenge 2026 (Qualcomm / Unstop)**

[🚀 Quick Start](#-try-the-prototype) • [💡 The Idea](#-the-idea-a-cognitive-compiler-with-known--inferred--unknown) • [🏗️ Architecture](#%EF%B8%8F-architecture) • [⚡ Snapdragon Plan](#-snapdragon-npu-plan-targets-not-results) • [🔒 Privacy Center](#-privacy-design-goals) • [📊 Real Output](#-real-verified-output-rule-based-engine---no-model)

</div>

<br/>

## 📌 Project Status *(Read This First)*

> [!NOTE]
> This repository is a **rigorous proposal plus a verified, tested prototype of the core logic**. It is not yet the full desktop application, and benchmark numbers will only be reported after direct measurement on physical Snapdragon hardware.

| Area | Implementation State | Execution Path |
| :--- | :--- | :--- |
| **Structured Output Schema** | 🟢 **Implemented & Tested** | Pydantic v2 strict models (`ActionItem`, `DeadlineItem`, `InterpretationItem`, `AmbiguityReport`, `NeuroLensInsight`) |
| **Cognitive Compiler Engine** | 🟢 **Implemented & Tested** | Deterministic deadline extraction, ambiguity signal scoring, clarifying questions, evidence citations (CPU) |
| **Local Model Client Bridge** | 🟢 **Implemented** | Local OpenAI-compatible client endpoint (`http://127.0.0.1:18181/v1`), Pydantic JSON validation & automatic fallback. *Not yet run against a live GenieX server* |
| **Audio Ingestion & ASR** | 🟡 **Planned** | Silero VAD + Qualcomm AI Hub Whisper-Base (NPU) |
| **Vision Ingestion** | 🟡 **Planned** | Screenshot region capture + Qwen3-VL-4B-Instruct via GenieX (NPU) |
| **User Interface & Memory** | 🟡 **Planned** | Streamlit / Windows Calm Accessibility UI, Focus Mode, Ephemeral SQLite store |
| **Hardware Benchmarks** | ⚪ **Not measured yet** | Real ASR latency, TTFT, and CPU vs. NPU measurements will be documented upon hardware validation |

*Every result emitted by the prototype explicitly discloses which engine produced it (`[RUNTIME]`), guaranteeing zero fabricated benchmark claims.*

---

## 🎯 The Problem

Human communication is rapid, implicit, and often overloaded with ambiguity:
- **Indirect & Softened Requests:** Phrases like *"It would probably be good if you could get that over before Friday..."* create severe executive friction for neurodivergent minds (ADHD, social communication processing) and overwhelmed students.
- **The Ambiguity Tax:** Vague comments like *"Maybe we should look into that sometime"* cause mental loops trying to decipher ownership, urgency, and deliverables.
- **The Cloud Privacy Trap:** Cloud assistants (ChatGPT, cloud Whisper APIs) solve comprehension by harvesting voice, video, and screen data to external servers—unacceptable for private lectures, sensitive business meetings, and personal thought.

> **NeuroLens is an accessibility and productivity aid.** It is **not** a medical diagnostic tool and does not claim to diagnose, treat, or mind-read any condition.

---

## 💡 The Idea: A Cognitive Compiler with Known / Inferred / Unknown

Rather than dumping word-by-word transcripts or generating generic conversational chatbot responses, NeuroLens compiles messy human language into a strict, uncertainty-aware structure:

<div align="center">

```
Raw Spoken / Visual Utterance
             │
             ▼
┌────────────────────────────────────────────────────────┐
│               NeuroLens Cognitive Compiler             │
├──────────────────────────┬─────────────────────────────┤
│ 🟢 KNOWN                 │ Literal meaning, explicit   │
│                          │ tasks, deterministic dates  │
├──────────────────────────┼─────────────────────────────┤
│ 🟡 INFERRED              │ Multi-hypothesis readings   │
│                          │ with verbatim text evidence │
├──────────────────────────┼─────────────────────────────┤
│ 🔴 UNKNOWN               │ Missing parameters & direct │
│                          │ non-hallucinated questions  │
└──────────────────────────┴─────────────────────────────┘
```

</div>

* **Known (Factual):** Literal meaning, explicit tasks, and deadlines resolved via deterministic temporal rules (*"Friday"*).
* **Inferred (Possibility-Based):** Plausible interpretations tagged with confidence and matched evidence snippets. *It never asserts hidden psychological intent as fact.*
* **Unknown (Zero-Hallucination Ambiguity):** When key details are missing (unassigned task, vague timing), NeuroLens stops and generates a targeted clarifying question rather than guessing.

---

## 🏗️ Architecture

```
 Microphone ──► VAD ──► Whisper-Base ────────┐                   [Planned - Qualcomm AI Hub]
 Screenshot ──► Qwen3-VL-4B ─────────────────┤                   [Planned - GenieX / QAIRT]
 Typed text ─────────────────────────────────┤                   [Implemented]
                                             ▼
                                  Cognitive Compiler             [Implemented]
                       (Local Model via GenieX + Rule Engines)   Model client written; not yet run on device
                                             ▼
                                   Pydantic Validation           [Implemented]
                                             ▼
                        Tasks / Focus Mode / Local SQLite / UI   [Planned - Ephemeral RAM default]
```

> **Core Architectural Principle:** AI inference is designed to execute locally on the Snapdragon Hexagon™ NPU where supported. Application UI, SQLite storage, and rule validation execute efficiently on the CPU.

---

## ⚡ Snapdragon NPU Plan *(Targets, Not Results)*

| Role | Candidate Model | Intended Runtime | Snapdragon Support Status |
| :--- | :--- | :--- | :--- |
| **Speech-to-Text (ASR)** | **Whisper-Base** | Qualcomm AI Hub / QAI AppBuilder | Verified on AI Hub for Snapdragon X Elite / X Plus / X2 Elite. *Not yet run on my device* |
| **Reasoning (Compiler)** | **Qwen3-0.6B** *(Phi-4-Mini as alt)* | GenieX local OpenAI-compatible server | Model client written; *not yet run on my device* |
| **Screen Understanding** | **Qwen3-VL-4B-Instruct** | GenieX / QAIRT NPU path | Planned for user-selected screen snips |

*These models are listed on Qualcomm AI Hub for Snapdragon X-series devices. Real device execution and latency benchmarks will be measured directly on our Snapdragon laptop and reported honestly.*

---

## 🔒 Privacy Design Goals

* **Ephemeral by Default:** Raw audio streams and captured screenshots are processed in volatile memory (RAM) and immediately destroyed. Nothing is saved unless the user explicitly clicks *"Save Session"*.
* **Local Memory Isolation:** Stores user-approved preferences (*"user prefers concise replies"*), never raw conversation surveillance logs.
* **Offline Lock:** Core models require zero internet connectivity. Network-independent behavior will be thoroughly validated.
* **Zero Cloud Dependence:** Built to eliminate recurring SaaS API subscriptions and cloud privacy leaks.

---

## 🚀 Try the Prototype

The prototype runs out of the box with zero external dependencies or API keys required:

```bash
# 1. Clone & install dependencies
git clone https://github.com/swaskiee/NeuroLens.git
cd NeuroLens
pip install -r requirements.txt

# 2. Run the Rule-Based Engine (No local model required, 100% offline)
python cognitive_compiler.py samples/meeting_01.txt --no-model
python cognitive_compiler.py samples/ambiguous_01.txt --no-model
python cognitive_compiler.py samples/hinglish_01.txt --no-model
python cognitive_compiler.py samples/meeting_01.txt --no-model --json

# 3. With a local OpenAI-compatible server (e.g. GenieX running on Snapdragon NPU at 127.0.0.1:18181)
python cognitive_compiler.py samples/meeting_01.txt --model qwen3-0.6b

# 4. Run automated test suite (5/5 unit tests)
python -m pytest tests -v
```

> **Fail-Safe Mechanism:** If the local model server is unreachable or produces invalid JSON, the compiler automatically falls back to the deterministic rule engine and transparently labels the output source.

---

## 📊 Real Verified Output (Rule-Based Engine, `--no-model`)

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
  missing: which part should change, and how

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

---

## 🧪 Evaluation Plan *(Targets, Not Results)*

* **Empirical Test Dataset:** A controlled, hand-labeled set of 30 conversational samples (explicit actions, deadlines, ambiguous phrasing, multiple sub-tasks, Hinglish requests).
* **Target Metrics:** Task extraction precision & recall (>90%), deadline extraction accuracy (>95%), and ambiguity classification score.
* **On-Device Hardware Profiling:** Real measurements of ASR latency, Time-to-First-Token (TTFT), end-to-end response time, and an authentic CPU vs. NPU latency comparison.
* **Offline Verification:** Full system test executed with Wi-Fi disabled to verify zero cloud leakage.

---

## ⚠️ Known Limitations

* **Rule-Engine Scope:** The rule-based engine relies on regex and linguistic heuristics. It handles standard professional phrasings well but will miss edge cases; that is why the local LLM path exists.
* **Task Granularity:** Action extraction currently mirrors the speaker's phrasing closely rather than performing deep micro-step rewriting.
* **Multilingual Coverage:** Hinglish support currently targets common colloquial verbs (*"kal tak"*, *"bana dena"*).
* **Application Shell:** Speech audio, vision inputs, persistent SQLite memory, and the desktop UI are in the planned phase.

---

## 🗺️ Development Roadmap

- [x] **Milestone 1:** Pydantic schema validation & hybrid deadline/ambiguity rule engine.
- [x] **Milestone 2:** Local OpenAI/GenieX client bridge with fallback handling & automated test suite.
- [ ] **Milestone 3:** Run GenieX with Qwen3-0.6B on Snapdragon laptop; benchmark real NPU latency.
- [ ] **Milestone 4:** Integrate Whisper-Base on NPU via Qualcomm AI Hub for audio files and live mic streams.
- [ ] **Milestone 5:** Build calm Streamlit/Windows accessibility UI with Focus Mode and Cognitive Load slider.
- [ ] **Milestone 6:** Integrate Qwen3-VL for user-initiated screen snips (`ContextLens`).

---

## 📂 Repository Layout

```text
NeuroLens/
│
├── cognitive_compiler.py      # Core Cognitive Compiler prototype (Dual-engine: LLM + Rules)
├── generate_deck.py           # Presentation pitch deck generator (.pptx)
├── requirements.txt           # Minimal dependencies (pydantic, pytest, python-pptx)
├── LICENSE                    # Apache-2.0 open-source license
│
├── samples/                   # Real-world test scenarios
│   ├── meeting_01.txt         # Indirect meeting request with deadline
│   ├── ambiguous_01.txt       # Unassigned, vague request ("look into that sometime")
│   └── hinglish_01.txt        # Bilingual conversational request ("kal tak...")
│
├── tests/
│   └── test_cognitive_compiler.py  # Automated unit test suite (5 passing tests)
│
└── docs/                      # Challenge submission documentation
    ├── project_description.md # 2-page brief proposal for competition submission
    └── NeuroLens_Pitch_Deck.pptx # 10-slide pitch presentation
```

---

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.