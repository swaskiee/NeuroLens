"""
Generate NeuroLens Pitch Deck Presentation (.pptx)
Complies with Snapdragon AI Lab Build & Present Challenge 8-10 slide structure.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def create_deck(output_path="docs/NeuroLens_Pitch_Deck.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    DARK_NAVY = RGBColor(16, 24, 40)
    WHITE = RGBColor(255, 255, 255)
    QUALCOMM_RED = RGBColor(224, 32, 32)
    SLATE_GRAY = RGBColor(71, 84, 103)
    LIGHT_BG = RGBColor(248, 250, 252)
    ACCENT_BLUE = RGBColor(2, 122, 255)
    CARD_BG = RGBColor(238, 242, 246)

    def set_slide_background(slide, color):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_header(slide, title_text, category="NEUROLENS | SNAPDRAGON AI LAB 2026"):
        box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.2))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p0 = tf.paragraphs[0]
        p0.text = category.upper()
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = QUALCOMM_RED
        
        p1 = tf.add_paragraph()
        p1.text = title_text
        p1.font.size = Pt(28)
        p1.font.bold = True
        p1.font.color.rgb = DARK_NAVY

    # SLIDE 1: Title Slide
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, DARK_NAVY)
    
    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.3), Inches(3.2))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "NeuroLens"
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = WHITE
    
    p2 = tf1.add_paragraph()
    p2.text = "Private, Real-Time AI for Cognitive Accessibility"
    p2.font.size = Pt(24)
    p2.font.color.rgb = ACCENT_BLUE
    p2.space_before = Pt(10)

    p3 = tf1.add_paragraph()
    p3.text = "\"Understand the moment. Organize the thought. Keep everything private.\""
    p3.font.size = Pt(16)
    p3.font.italic = True
    p3.font.color.rgb = RGBColor(200, 210, 225)
    p3.space_before = Pt(14)

    p4 = tf1.add_paragraph()
    p4.text = "Snapdragon® AI Lab Build & Present Challenge 2026 | Optimized for Snapdragon-Powered HP PCs"
    p4.font.size = Pt(13)
    p4.font.bold = True
    p4.font.color.rgb = QUALCOMM_RED
    p4.space_before = Pt(24)

    # SLIDE 2: The Core Problem
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, LIGHT_BG)
    add_header(s2, "Human Communication Is Fast. Understanding It Isn't Always.")
    
    box2 = s2.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.7), Inches(4.8))
    tf2 = box2.text_frame
    tf2.word_wrap = True
    
    points2 = [
        ("Cognitive Friction in Daily Conversations", "Subtle, indirect speech like 'It would probably be good if you revisited...' creates severe executive load for neurodivergent minds (ADHD, social processing challenges) and overwhelmed students."),
        ("The Implicit-to-Action Gap", "Unstructured communication rarely delivers cleanly packaged task lists. Users spend massive mental energy disambiguating what is a real task vs. casual discussion."),
        ("The Cloud Privacy Dilemma", "Sending daily conversations, lectures, and screen context to cloud LLMs creates unacceptable privacy, data governance, and compliance risks."),
        ("The Need for On-Device Translation", "A private cognitive layer sitting between messy spoken/visual information and the user's brain—running 100% locally on the device.")
    ]
    for title, desc in points2:
        p = tf2.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(16)
        p.font.color.rgb = DARK_NAVY
        p.space_before = Pt(12)
        
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = SLATE_GRAY

    # SLIDE 3: Why Existing AI Falls Short
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, LIGHT_BG)
    add_header(s3, "Why Existing Tools Fall Short")
    
    box3 = s3.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.7), Inches(4.8))
    tf3 = box3.text_frame
    tf3.word_wrap = True
    
    table_data = [
        ("Generic Transcription (Whisper APIs)", "Dumps thousands of raw words without understanding. Increases cognitive load instead of reducing it."),
        ("Cloud AI Chatbots (ChatGPT / Cloud Claude)", "Leaks sensitive personal thoughts and workplace meetings to remote cloud infrastructure with recurring latency."),
        ("Productivity Apps (Todoist / Notion)", "Requires manual typing and tedious task breakdown. Fails to capture live verbal context at the moment of utterance."),
        ("Hallucinatory AI Assistants", "Asserts false certainty about ambiguous intent instead of clearly stating what is unknown or asking for clarification.")
    ]
    for k, v in table_data:
        p = tf3.add_paragraph()
        p.text = f"✖ {k}: "
        p.font.bold = True
        p.font.size = Pt(16)
        p.font.color.rgb = DARK_NAVY
        p.space_before = Pt(12)
        
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.color.rgb = SLATE_GRAY

    # SLIDE 4: Solution: The Cognitive Compiler
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, LIGHT_BG)
    add_header(s4, "The Solution: NeuroLens Cognitive Compiler")
    
    box4 = s4.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.7), Inches(4.8))
    tf4 = box4.text_frame
    tf4.word_wrap = True
    
    intro4 = tf4.paragraphs[0]
    intro4.text = "NeuroLens is not a generic chatbot. It is a formal Cognitive Compiler:"
    intro4.font.size = Pt(18)
    intro4.font.bold = True
    intro4.font.color.rgb = DARK_NAVY
    
    steps4 = [
        ("Parse", "Captures raw speech chunks via VAD and user-selected visual screen context."),
        ("Disambiguate", "Evaluates linguistic ambiguity, extracts deterministic deadlines, and tags uncertainty."),
        ("Structure", "Emits verified JSON containing explicit tasks, priority, deadlines, and multi-hypothesis interpretations."),
        ("Present", "Adapts information density across Minimal, Balanced, and Detailed cognitive load modes.")
    ]
    for s_title, s_desc in steps4:
        p = tf4.add_paragraph()
        p.text = f"► {s_title}: "
        p.font.bold = True
        p.font.size = Pt(16)
        p.font.color.rgb = ACCENT_BLUE
        p.space_before = Pt(10)
        
        run = p.add_run()
        run.text = s_desc
        run.font.bold = False
        run.font.color.rgb = SLATE_GRAY

    # SLIDE 5: Core Innovation: Known ≠ Inferred ≠ Unknown
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, LIGHT_BG)
    add_header(s5, "Core Innovation: Known ≠ Inferred ≠ Unknown")
    
    box5 = s5.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.7), Inches(4.8))
    tf5 = box5.text_frame
    tf5.word_wrap = True
    
    framework = [
        ("1. KNOWN (Factual & Explicit)", "Literal meaning, explicit task requirements, and deterministic deadlines ('before Friday')."),
        ("2. INFERRED (Possibility-Based with Evidence)", "Probabilistic interpretations with attached confidence and verbatim quotes ('Priority request: 82% confidence, backed by before Friday')."),
        ("3. UNKNOWN (Zero-Hallucination Ambiguity)", "When instructions are vague, NeuroLens generates targeted clarifying questions instead of guessing intent ('What specific changes are needed in section 1?').")
    ]
    for f_title, f_desc in framework:
        p = tf5.add_paragraph()
        p.text = f"{f_title}\n"
        p.font.bold = True
        p.font.size = Pt(17)
        p.font.color.rgb = DARK_NAVY
        p.space_before = Pt(12)
        
        run = p.add_run()
        run.text = f"   {f_desc}"
        run.font.bold = False
        run.font.size = Pt(15)
        run.font.color.rgb = SLATE_GRAY

    # SLIDE 6: Snapdragon Native NPU Architecture
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, LIGHT_BG)
    add_header(s6, "Snapdragon® Hardware Architecture & NPU Pathway")
    
    box6 = s6.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.7), Inches(4.8))
    tf6 = box6.text_frame
    tf6.word_wrap = True
    
    p = tf6.paragraphs[0]
    p.text = "AI inference is offloaded to the Hexagon NPU; application logic & database reside on the CPU."
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY
    
    npu_stack = [
        ("Speech (ASR)", "Whisper-Base — Qualcomm AI Hub verified for Snapdragon X Elite / X Plus; fast local speech-to-text without cloud streaming."),
        ("Reasoning (Cognitive Compiler)", "Qwen3-0.6B / Phi-4-Mini — Local GenieX / QAIRT execution on Hexagon NPU; sub-second JSON compilation (~28 tokens/s)."),
        ("Vision (ContextLens)", "Qwen3-VL-4B-Instruct — On-device visual understanding of slides, charts, and screen context via GenieX."),
        ("Local API Bridge", "GenieX OpenAI-compatible local server (http://127.0.0.1:18181/v1) — No cloud network requests required.")
    ]
    for mod, desc in npu_stack:
        p = tf6.add_paragraph()
        p.text = f"• {mod}: "
        p.font.bold = True
        p.font.size = Pt(15)
        p.font.color.rgb = QUALCOMM_RED
        p.space_before = Pt(10)
        
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = SLATE_GRAY

    # SLIDE 7: Privacy by Design
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, LIGHT_BG)
    add_header(s7, "Privacy by Design: Ephemeral by Default")
    
    box7 = s7.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.7), Inches(4.8))
    tf7 = box7.text_frame
    tf7.word_wrap = True
    
    priv_points = [
        ("Ephemeral Speech & Context", "Raw audio chunks are processed in RAM and immediately discarded. Never permanently logged without explicit user consent."),
        ("Network Independence (Offline Lock)", "Full AI processing verified with network disconnected. Zero outbound telemetry or cloud API calls."),
        ("Granular Local Memory", "Stores user communication preferences ('prefers concise replies', 'break tasks into small steps') locally in SQLite rather than profiling raw transcripts."),
        ("One-Click Data Purge", "Guaranteed local data destruction with immediate database deletion.")
    ]
    for p_title, p_desc in priv_points:
        p = tf7.add_paragraph()
        p.text = f"✔ {p_title}: "
        p.font.bold = True
        p.font.size = Pt(16)
        p.font.color.rgb = DARK_NAVY
        p.space_before = Pt(12)
        
        run = p.add_run()
        run.text = p_desc
        run.font.bold = False
        run.font.color.rgb = SLATE_GRAY

    # SLIDE 8: Live Demonstration Workflow
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, LIGHT_BG)
    add_header(s8, "Live Prototype Demonstration")
    
    box8 = s8.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.7), Inches(4.8))
    tf8 = box8.text_frame
    tf8.word_wrap = True
    
    demo_flow = [
        ("Input Transcript", "\"It would probably be good if you could get the analysis over to me sometime before Friday. And maybe revisit the first section because I don't think we're quite there yet.\""),
        ("Extracted Action Items", "1. [ ] Send analysis (Priority: HIGH)   |   2. [ ] Revisit first section (Priority: MEDIUM)"),
        ("Detected Deadlines", "• Friday (Resolved via deterministic hybrid rule + NPU inference)"),
        ("Possibility & Evidence", "• Interpretation: Priority deliverable (82% confidence, evidence: 'get the analysis over before Friday')"),
        ("Ambiguity & Clarification", "• Ambiguity: MEDIUM (revisions to section 1 unspecified) -> Clarifying Question: 'What specific adjustments would you like made to section 1?'")
    ]
    for d_title, d_desc in demo_flow:
        p = tf8.add_paragraph()
        p.text = f"[{d_title}]\n"
        p.font.bold = True
        p.font.size = Pt(15)
        p.font.color.rgb = ACCENT_BLUE
        p.space_before = Pt(8)
        
        run = p.add_run()
        run.text = f"  {d_desc}"
        run.font.bold = False
        run.font.size = Pt(14)
        run.font.color.rgb = DARK_NAVY

    # SLIDE 9: Evaluation & Benchmarking Plan
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, LIGHT_BG)
    add_header(s9, "Target Metrics & Evaluation Plan")
    
    box9 = s9.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.7), Inches(4.8))
    tf9 = box9.text_frame
    tf9.word_wrap = True
    
    eval_metrics = [
        ("Task Extraction Precision & Recall", ">90% benchmark across controlled conversational and lecture transcripts."),
        ("Deadline Extraction Accuracy", ">95% accuracy via dual neural + deterministic rule engine."),
        ("End-to-End Latency Target", "Sub-second turnaround on Snapdragon X NPU platform for real-time responsiveness."),
        ("Honest Benchmark Policy", "All latency and token metrics are documented as measured directly on target Snapdragon hardware, without inflated cloud assumptions.")
    ]
    for m_title, m_desc in eval_metrics:
        p = tf9.add_paragraph()
        p.text = f"• {m_title}: "
        p.font.bold = True
        p.font.size = Pt(16)
        p.font.color.rgb = DARK_NAVY
        p.space_before = Pt(12)
        
        run = p.add_run()
        run.text = m_desc
        run.font.bold = False
        run.font.color.rgb = SLATE_GRAY

    # SLIDE 10: Roadmap & Snapdragon Opportunity
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, DARK_NAVY)
    
    box10 = s10.shapes.add_textbox(Inches(0.8), Inches(1.0), Inches(11.7), Inches(5.8))
    tf10 = box10.text_frame
    tf10.word_wrap = True
    
    p = tf10.paragraphs[0]
    p.text = "Roadmap & The Snapdragon® Advantage"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = WHITE
    
    roadmap = [
        ("Phase 1 (Completed Prototype)", "Pydantic-validated Cognitive Compiler, hybrid deadline engine, ambiguity detector, and multi-scenario verification."),
        ("Phase 2 (Hackathon MVP)", "Streamlit calm UI integration, live Whisper-Base microphone ingestion, and GenieX local server binding on Snapdragon X PC."),
        ("Phase 3 (Multimodal Extension)", "Qwen3-VL ContextLens for instant slide/document region understanding."),
        ("Long-term Vision", "Empowering millions of neurodivergent users and professionals with private, on-device cognitive augmentation powered by Qualcomm Snapdragon.")
    ]
    for r_title, r_desc in roadmap:
        p = tf10.add_paragraph()
        p.text = f"\n✔ {r_title}: "
        p.font.bold = True
        p.font.size = Pt(16)
        p.font.color.rgb = ACCENT_BLUE
        
        run = p.add_run()
        run.text = r_desc
        run.font.bold = False
        run.font.color.rgb = RGBColor(220, 230, 242)

    prs.save(output_path)
    print(f"Presentation successfully created at: {output_path}")

if __name__ == "__main__":
    create_deck()