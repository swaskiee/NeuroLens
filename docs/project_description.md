# NeuroLens: Private, Real-Time AI for Cognitive Accessibility

**Project description: Snapdragon® AI Lab Build & Present Challenge 2026**
Swati Dubey, individual participant | Repository: github.com/swaskiee/NeuroLens

*"Understand the moment. Organize the thought. Keep everything private."*

## 1. Summary

NeuroLens is a proposed on-device assistant for Snapdragon-powered Windows PCs. It takes speech, text and (optionally) a user-selected screenshot and turns them into structured next steps: what was asked, by when, what is unclear, and what to ask or reply. It is designed to keep sensitive conversations and screen content on the device, using local AI models on the Snapdragon NPU where supported.

NeuroLens is an accessibility and productivity aid. It does not diagnose or treat any condition and does not claim to know what a speaker "really" feels or intends.

## 2. Problem

Real communication is fast and indirect. "It would probably be good if you could get the analysis over sometime before Friday" is a request with a deadline, but it is easy to miss in a live meeting or lecture. People who benefit from lower cognitive load, such as students following fast lectures, professionals in busy meetings, and anyone who finds indirect phrasing hard to parse, have to work out the real task, the deadline and the missing details in real time.

Cloud assistants can help with this, but they require sending private conversations and screen content to a remote service. That is a poor fit for personal, workplace or study material.

## 3. Solution: a Cognitive Compiler

NeuroLens compiles messy language into a fixed, validated structure rather than a free-form chat reply. Its core idea is to keep three things separate:

| Layer | What it contains | How it is produced |
|---|---|---|
| **Known** | Literal meaning, explicit tasks, deadlines | Rules for obvious dates and times, plus the model |
| **Inferred** | Possible readings of ambiguous wording, each with supporting words from the input | Model and heuristics, always phrased as possibilities |
| **Unknown** | Missing task, deadline or referent, and a clarifying question | Uncertainty scoring; the system asks instead of guessing |

Other design choices: the model's output must pass a Pydantic schema or the system falls back to deterministic rules; deadlines are extracted by rules first, so the model is not trusted for them; and the level of detail shown can be tuned (minimal to detailed) to limit cognitive load.

## 4. Architecture and Snapdragon plan

Audio goes through voice-activity detection and Whisper-Base for transcription. Optional screenshots go to Qwen3-VL-4B-Instruct. Text from either source goes to the Cognitive Compiler, which uses a small local language model (Qwen3-0.6B, with Phi-4-Mini as an alternative) served through GenieX's OpenAI-compatible local endpoint, combined with rule engines. Output is validated, then shown in the UI and optionally saved to local SQLite storage.

These models are listed on Qualcomm AI Hub for Snapdragon X-series devices. The plan is for inference to run on the Hexagon NPU where supported, with the UI, storage and rule logic on the CPU. I will verify NPU execution and measure latency on my own Snapdragon laptop and report the results. No performance figures are claimed in this document.

## 5. Privacy design

Design goals for the full application:

- Raw audio and screenshots are processed in memory and discarded unless the user chooses to save.
- Memory stores user-approved preferences (for example "prefers short answers"), not conversation logs.
- Core inference needs no cloud AI service. Offline operation will be tested and documented before it is claimed.

## 6. Current status

**Implemented and tested (CPU):** the structured-output schema, the rule-based compiler (actions, deadlines, ambiguity scoring, clarifying questions, evidence-linked interpretations), a local-model client with schema validation and automatic fallback, and a 16-test suite. The model path has been tested with a stubbed model; it has not yet been run against a real GenieX server.

**Planned:** speech input (VAD, Whisper-Base), screenshot understanding (Qwen3-VL), Focus Mode, local memory, Privacy Center and a simple UI.

**Not yet done:** any measurement on Snapdragon hardware.

## 7. Evaluation plan

A small hand-labelled set of about 30 utterances (explicit tasks, deadlines, ambiguous statements, multiple tasks, Hinglish), scored for task precision and recall, deadline accuracy and ambiguity classification. On-device: ASR latency, time to first token, end-to-end latency, and CPU versus NPU comparison. An offline test with the network disabled. All numbers will be measured, not assumed.

## 8. Limitations and responsible use

The rule engine is pattern matching and will miss many phrasings, which is why a model path exists. Small local models can make mistakes, so every interpretation carries its evidence and the system prefers asking a question over guessing. NeuroLens is not a medical, diagnostic or emotion-detection product.
