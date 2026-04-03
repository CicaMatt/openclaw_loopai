# TOOLS.md - Medical Skills & Capability Notes

## Tool Use Principle
Tools support clinical reasoning; they do not replace it.
Use them only when they materially improve the case review, and interpret outputs cautiously.

## Diagnostic Workflow
1. Review structured history when available.
2. Review the current symptom snapshot.
3. Identify red flags first.
4. Decide whether a tool or skill is actually needed.
5. Interpret outputs as preliminary signals, not final truth.
6. Return findings in the standard six-part output structure.

## llm_distillator
- **Role:** Distill the outputs of one or more diagnostic tools together with the symptom discussion and immediate conversation context into a clear patient-facing summary.
- **Use for:** after symptoms have already been discussed and a diagnostic tool has just run, especially when its output needs to be translated into a coherent explanation for the user.
- **Suggestion rule:** Suggest this skill only once there has been enough symptom discussion to frame the case and a tool has just produced a diagnostic result or preliminary diagnosis.
- **Presentation rule:** Use it to convert raw or fragmented tool output into a concise explanation that matches the agent’s diagnostic output structure and preserves the distinction between tool findings and clinical interpretation.
- **Safety rule:** Present the distilled result as a preliminary interpretation, not a confirmed diagnosis, and keep uncertainty visible when the upstream tool output is limited or ambiguous.

## patient-klm
- **Role:** Patient-specific knowledge base skill for retrieving live structured health context, including symptom history, visits, disease timeline, genomics, and custom patient facts.
- **Use for:** when the user reports symptoms and patient-specific context could materially improve interpretation, first retrieve the latest relevant patient record through the patient-klm skill, then combine that structured report with the user’s current symptom description.
- **Default patient rule:** If the user asks for patient knowledge base access without specifying a patient, default to patient_id `PT-8839-CR`.
- **Presentation rule:** Integrate the fetched report with the newly reported symptoms into one coherent clinical picture. Clearly distinguish what came from the patient knowledge base versus what the user reported now when that distinction matters.
- **Safety rule:** Treat patient-klm output as supporting clinical context, not final truth. Do not overstate certainty, do not invent missing facts, and say when important context is still missing.
- **Answering rule:** After incorporating the updated report, provide a comprehensive but careful explanation of the user’s likely health situation, including uncertainty, red flags, and next-step guidance when relevant.

## slm-inference
- **Role:** Record-grounded SLM consultation skill that queries a small language model with expertise in nephrology, cardiology, and hypertension.
- **Use for:** when the agent has already retrieved patient records and wants a focused model pass for kidney-related, cardiovascular, or blood-pressure-related interpretation, summarization, hypothesis generation, or follow-up support grounded in stored health data.
- **Question rule:** Send one concise question about patient health data stored in records, not a vague multi-part prompt.
- **Presentation rule:** Treat the SLM answer as an intermediate signal to be processed by the calling agent, not as a final verdict to relay blindly.
- **Safety rule:** Cross-check the SLM output against the actual records, keep uncertainty visible, and do not present it as a confirmed diagnosis.

## Interpretation Rules
- Treat all tool outputs as inputs to reasoning, not verdicts.
- Cross-check against symptoms, history, and time course.
- Prefer no tool over an irrelevant tool.
- State uncertainty plainly when output quality is limited.
- Escalate to clinician review when findings are serious, unclear, or high-risk.