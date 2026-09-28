# NeuroLens: Private, Real-Time AI for Cognitive Accessibility

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Platform: Snapdragon Windows ARM64](https://img.shields.io/badge/Platform-Snapdragon%20Windows%20ARM64-red.svg)](https://www.qualcomm.com/laptops/products/snapdragon-x-elite)
[![Status: Prototype In Progress](https://img.shields.io/badge/Status-Proposal%20%2F%20Prototype%20Verified-success.svg)]()

> **"Understand the moment. Organize the thought. Keep everything private."**

---

## 📌 Submission Overview
* **Competition:** Snapdragon® AI Lab Build & Present Challenge 2026 (Qualcomm / Unstop)
* **Target Hardware:** Snapdragon®-powered HP PCs (Snapdragon X Elite, X Plus, X2 Elite)
* **Core Paradigm:** On-Device Cognitive Accessibility Layer (Speech + Vision + Text $\rightarrow$ Structured Actions)
* **Status:** Proposal Phase / Working Functional Prototype Verified

---

## 💡 What is NeuroLens?
NeuroLens sits as a **private, local AI layer between messy human communication and the user’s brain**. 

It is designed for people who benefit from reduced cognitive load (students in fast lectures, professionals in rapid meetings, neurodivergent individuals navigating indirect communication). It **does not** diagnose medical conditions or claim to read minds. Instead, it converts:

$$\text{Speech} + \text{Text} + \text{Visual Context} \longrightarrow \mathbf{Meaning} + \mathbf{Actions} + \mathbf{Deadlines} + \mathbf{Interpretations} + \mathbf{Safe\ Replies}$$

While keeping **all sensitive processing 100% on the Snapdragon PC**.

---

## 🚀 Key Architectural Innovation: The Cognitive Compiler

Instead of generating unstructured conversational paragraphs like a generic chatbot, NeuroLens functions as a **Cognitive Compiler**:

```
                         NEUROLENS
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
        HEAR                 SEE                THINK
          │                   │                   │
    Whisper-Base         Qwen3-VL-4B           Qwen3-0.6B
   (Hexagon NPU)        (GenieX / NPU)       (GenieX / NPU)
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                      CONTEXT ENGINE
                              │
              ┌───────────────┼───────────────┐
              │               │               │
           MEANING         ACTIONS         MEMORY
       Interpretations   Tasks/Deadlines  Preferences
              │               │               │
              └───────────────┼───────────────┘
                              │
                        USER CONTROL
                    Local-Only / Ephemeral
```

### The "Known ≠ Inferred ≠ Unknown" Framework
1. **Known (Factual):** Literal meaning, explicit tasks, and deterministic deadlines (`"before Friday"`).
2. **Inferred (Possibility-Based):** Multi-hypothesis interpretations with confidence scores and explicit textual evidence citations (e.g. *"Priority request: 82% confidence, backed by 'before Friday'"*).
3. **Unknown (Zero-Hallucination Ambiguity):** When instructions lack key parameters (missing deadlines, vague pronouns like *"look into that"*), NeuroLens flags ambiguity and **generates targeted clarifying questions** instead of hallucinating answers.

---

## ⚡ Why Snapdragon & On-Device NPU?
NeuroLens processes intimate verbal conversations, sensitive business meetings, and personal workflow notes. Sending this telemetry to third-party cloud servers violates personal privacy and enterprise security.

### Real Snapdragon NPU Model Pathway
| Capability | Model | Runtime / Execution Path |
| :--- | :--- | :--- |
| **Speech (ASR)** | **Whisper-Base** | Qualcomm AI Hub verified on Snapdragon X Elite / X Plus / X2 Elite via NPU |
| **Cognitive Compiler** | **Qwen3-0.6B** / **Phi-4-Mini** | GenieX / QAIRT local OpenAI-compatible endpoint (`http://127.0.0.1:18181/v1`) |
| **Vision (ContextLens)** | **Qwen3-VL-4B-Instruct** | GenieX / QAIRT visual reasoning on user-selected screen regions |
| **Deterministic Rules** | Rule Engine | Fast regex temporal parsing on local CPU |

> **Architectural Principle:** AI inference is accelerated on the Snapdragon NPU; application logic, local SQLite storage, and UI run seamlessly on the local CPU.

---

## 🔒 Privacy Center: Ephemeral by Default
* **Ephemeral Ingestion:** Raw microphone audio and visual context are processed strictly in RAM and immediately discarded.
* **Offline Lock:** Core models operate with zero network connection.
* **Local Memory Only:** User preferences (*"prefers concise responses"*) are stored in local SQLite; raw conversation transcripts are never permanently logged without explicit consent.
* **One-Click Purge:** Immediate local data destruction on command.

---

## 🛠 Project Structure

```text
NeuroLens/
│
├── cognitive_compiler.py      # Core Pydantic-validated Cognitive Compiler prototype
├── generate_deck.py           # Presentation pitch deck generator (.pptx)
├── requirements.txt           # Project dependencies
├── LICENSE                    # Apache-2.0 open-source license
│
├── samples/                   # Real-world test transcripts
│   ├── meeting_01.txt         # Indirect meeting request with deadline
│   ├── ambiguous_01.txt       # Ambiguous statement ("look into that sometime")
│   └── hinglish_01.txt        # Bilingual conversational request
│
├── tests/
│   └── test_cognitive_compiler.py  # Automated pytest verification suite
│
└── docs/                      # Challenge submission documentation
    ├── project_description.md # 2-page brief proposal for competition submission
    └── NeuroLens_Pitch_Deck.pptx # 10-slide pitch presentation
```

---

## 💻 Quick Start & Running the Prototype

### 1. Installation
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
```

### 2. Run Cognitive Compiler on Sample Transcripts
```bash
# Test on meeting transcript
python cognitive_compiler.py samples/meeting_01.txt

# Test on ambiguous transcript (ambiguity & clarification generation)
python cognitive_compiler.py samples/ambiguous_01.txt

# Test on Hinglish transcript
python cognitive_compiler.py samples/hinglish_01.txt

# Export verified JSON schema output
python cognitive_compiler.py samples/meeting_01.txt --json
```

### 3. Run Automated Tests
```bash
python -m pytest tests/test_cognitive_compiler.py -v
```

---

## 📊 Sample Execution Output

```text
======================================================================
NEUROLENS COGNITIVE COMPILER OUTPUT
======================================================================

[SOURCE UTTERANCE]
"It would probably be good if you could get the analysis over to me sometime before Friday. And maybe revisit the first section because I don't think we're quite there yet."

[1. LITERAL MEANING (KNOWN)]
The speaker requests sending the analysis before the deadline and revisiting the first section.

[2. EXTRACTED ACTIONABLE TASKS]
  1. [ ] Send analysis (Priority: HIGH)
  2. [ ] Revisit and update the first section (Priority: MEDIUM)

[3. DETECTED DEADLINES]
  - Task: Send analysis | Deadline: Friday (deterministic_rule)

[4. POSSIBILITY-BASED INTERPRETATIONS (INFERRED)]
  - Interpretation: The speaker requests that completing this deliverable be prioritized.
    Confidence: 82% | Evidence: "'get the analysis over to me sometime before Friday'"
  - Interpretation: Quality concerns exist regarding the introduction or initial methodology.
    Confidence: 74% | Evidence: "'I don't think we're quite there yet'"

[5. UNCERTAINTY & AMBIGUITY (UNKNOWN)]
  Level:  MEDIUM
  Reason: The exact revisions desired for the first section are unspecified.
  Missing: Specific criteria or sections needing changes in section 1

[6. SUGGESTED CLARIFYING QUESTION]
  "What specific adjustments would you like made to the first section?"

[7. SUGGESTED REPLIES]
  -> "Sure, I'll update the first section and send the analysis over before Friday."
  -> "Understood. Could you clarify what changes you'd like in the first section?"
  -> "Got it. Prioritizing the analysis for Friday delivery."

[RUNTIME PROVENANCE]
NeuroLens Hybrid Rule-Engine (Snapdragon NPU Optimized)
======================================================================
```

---

## 📜 Evaluation Criteria Alignment
* **Technical Implementation:** Hybrid neural + deterministic rule engine; strict Pydantic data modeling; GenieX local OpenAI endpoint integration for Snapdragon NPU acceleration.
* **Application Use Case & Innovation:** Pioneering "Known ≠ Inferred ≠ Unknown" framework with possibility-based interpretations and anti-hallucination ambiguity questioning for cognitive accessibility.
* **Deployment & Accessibility:** Ephemeral-by-default local memory, offline lock, and zero cloud API dependency.
* **Presentation & Documentation:** Comprehensive repository docs, verified test suite, 2-page formal brief, and 10-slide pitch presentation.

---

## 📄 License
This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.