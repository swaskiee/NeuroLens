# NeuroLens: Private, Real-Time AI for Cognitive Accessibility
**Project Proposal — Snapdragon® AI Lab Build & Present Challenge 2026**

---

## 1. Executive Summary & Tagline
> **"Understand the moment. Organize the thought. Keep everything private."**

**NeuroLens** is a private, on-device cognitive accessibility layer engineered specifically for Snapdragon®-powered Windows PCs. Rather than diagnosing conditions or claiming to infer subjective emotional states, NeuroLens bridges the gap between messy human communication and executive processing. It continuously transforms unstructured speech, text, and user-selected visual context into structured tasks, deadlines, possibility-based interpretations, and safe suggested responses.

By leveraging Qualcomm® on-device AI acceleration (Hexagon™ NPU via GenieX and QAI AppBuilder), NeuroLens guarantees zero cloud leakage for intimate spoken thoughts, private meeting recordings, and personal workflows.

---

## 2. Problem Statement & Accessibility Need
Human communication is rapid, implicit, and often overloaded with ambiguity:
- **Indirect Requests:** Phrases like *"It would probably be good if..."* conceal strict operational requirements.
- **Ambiguous Scope:** Phrases like *"Maybe look into that sometime"* waste mental energy on speculation.
- **Cognitive Overload:** Students in fast-paced lectures and neurodivergent professionals with ADHD/executive dysfunction experience cognitive friction parsing what is *actionable* vs. what is *ambiguous*.
- **The Cloud Privacy Trap:** Existing solutions (ChatGPT, cloud transcription) require transmitting voice and screen data to remote cloud servers—a major violation of privacy for enterprise meetings and private study.

---

## 3. The Core Innovation: Cognitive Compiler ("Known ≠ Inferred ≠ Unknown")
NeuroLens reframes unstructured language through a formal **Cognitive Compiler**:

$$\text{Raw Utterance} \longrightarrow \begin{cases} \mathbf{Known} & \text{(Literal meaning, explicit tasks, deadlines)} \\ \mathbf{Inferred} & \text{(Plausible interpretations with confidence \& evidence)} \\ \mathbf{Unknown} & \text{(Ambiguities \& explicit clarifying questions)} \end{cases}$$

### Key Differentiators:
1. **Possibility-Based Interpretation:** When intent is ambiguous, NeuroLens offers multi-hypothesis interpretations with attached textual evidence rather than hallucinating intent.
2. **Zero-Hallucination Ambiguity Engine:** When parameters are missing (unclear owner, vague timeline), the system generates targeted clarifying questions (*"What specific changes are needed?"*) rather than inventing data.
3. **Deterministic + Neural Hybrid:** Obvious temporal markers ("Friday", "tomorrow", "kal tak") are resolved via high-speed deterministic regex rules, offloading routine work and validating neural output.

---

## 4. Hardware & Software Architecture on Snapdragon
NeuroLens runs as a hybrid pipeline where heavy neural inference is mapped to the Snapdragon NPU, while application logic, databases, and UI reside on the CPU:

```
[ Microphone ]           [ Screen Snipping ]
      │ (Audio Stream)          │ (Selected Region)
      ▼                         ▼
 [Silero / WebRTC VAD]   [Qwen3-VL-4B-Instruct]
      │                         │ (Visual Understanding)
      ▼                         │
[Whisper-Base on NPU]           │
      │ (Transcript Buffer)     │
      └────────────┬────────────┘
                   ▼
       [Cognitive Compiler]
  (Qwen3-0.6B / Phi-4-Mini on NPU)
   + Deterministic Rule Engines
                   │
                   ▼
         [Pydantic Validator]
                   │
       ┌───────────┴───────────┐
       ▼                       ▼
 [Local SQLite DB]       [Calm Accessibility UI]
(Ephemeral RAM Default) (Minimal / Balanced / Detailed)
```

### Model Stack (Qualcomm AI Hub Verified):
- **ASR (Speech):** Whisper-Base (Qualcomm AI Hub verified for Snapdragon X Elite / X Plus; 200 token sequence, sub-second transcription).
- **Fast Reasoning / Compiler:** Qwen3-0.6B (429 MB Q4_0 executing on Hexagon NPU via GenieX, ~28 tokens/s).
- **Vision Context:** Qwen3-VL-4B-Instruct (On-device visual understanding of slides, emails, and code snippets).
- **Local API Gateway:** GenieX OpenAI-compatible local HTTP endpoint (`http://127.0.0.1:18181/v1`), ensuring zero cloud network egress.

---

## 5. Privacy, Trust & Ephemeral Architecture
- **Ephemeral by Default:** Audio streams and raw transcripts are processed in memory and discarded upon session completion unless the user explicitly clicks *"Save Session"*.
- **Offline Lock:** Core models run completely detached from the internet.
- **Physical NPU Lineage:** Every extracted task or interpretation provides an explainable evidence citation linking back to verbatim transcript markers.

---

## 6. Evaluation Framework & Next Steps
- **Empirical Metric Targets:**
  - Task Extraction Precision & Recall > 90% across controlled multi-turn scenarios.
  - Deadline Accuracy > 95% using the hybrid deterministic-neural engine.
  - Sub-second interaction latency target on Snapdragon X-series hardware.
- **Project Status:** Proposal Phase & Functional Python/Pydantic Cognitive Compiler Prototype verified.