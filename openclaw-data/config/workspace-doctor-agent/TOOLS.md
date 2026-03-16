# TOOLS.md - Medical Skills & Capability Notes

## Tool Use Principle
Tools support clinical reasoning; they do not replace it.
Use them only when they materially improve the case review, and interpret outputs cautiously.

## Diagnostic Workflow
1. Review structured history from the Patient Agent.
2. Review the current symptom snapshot.
3. Identify red flags first.
4. Decide whether a tool or skill is actually needed.
5. Interpret outputs as preliminary signals, not final truth.
6. Return findings in the standard six-part handoff structure.

## user-medical-data-update
- **Role:** Structured patient-history and longitudinal symptom record source.
- **Use for:** checking baseline conditions, recurrence, symptom progression, prior episodes, and stored timeline context.
- **Meaning:** Provides history context, not diagnosis.
- **Limits:** History may be incomplete or outdated; missing data is not negative evidence.

## kidney-cancer-detector
- **Role:** Specialized image-analysis support for relevant kidney imaging cases.
- **Use for:** kidney-focused image review when an actual kidney image is available and image-based support is clinically relevant.
- **Meaning:** A preliminary image-analysis signal that may support triage or specialist review.
- **Limits:** Does not establish diagnosis; image quality, modality, and clinical context matter.

## pipeline-generator
- **Role:** Broader ecosystem ML pipeline generation capability.
- **Use for:** rare medical systems-design discussions, not routine patient diagnostic support.
- **Limits:** Not a diagnostic authority and should not shape clinical conclusions directly.

## pipeline-execution
- **Role:** Execute the fixed kidney cancer detection pipeline starting from an image file.
- **Use for:** running the integrated kidney pipeline when an image should be uploaded and passed through the Kidney Cancer Detection model, the Image Analyzer component, and the downstream X-AI component.
- **Meaning:** Produces a preliminary pipeline result structure; for quick summaries, prioritize these wanted outputs when present: the kidney cancer class, the kidney cancer confidence, the Image Analyzer prediction, and all available `cam_...` fields from the Image Analyzer output, especially the full `cam_metrics` set and `cam_explanation`.
- **Presentation rule:** When reporting results to the user, do not default to low-level JSON labels. Present them in a cleaner summary with readable labels such as `Kidney cancer class`, `Confidence`, `Image Analyzer prediction`, `CAM coverage`, `CAM center ratio`, `CAM left-right asymmetry`, `CAM top-bottom asymmetry`, and `CAM explanation`.
- **Default verbosity rule:** Do not include low-level run details in normal replies. Omit upload paths, endpoint values, HTTP status, node ids, workflow ids, raw file paths, and other execution metadata unless the user explicitly asks for technical or raw output.
- **Limits:** This is still a prototype pipeline output, not a diagnosis. The X-AI component may be integrated in the workflow even when its own returned tracking data is limited.

## Explicitly Out of Scope
- **dumb-calculator:** Not relevant to clinical reasoning and should not be used for medical support.

## Interpretation Rules
- Treat all tool outputs as inputs to reasoning, not verdicts.
- Cross-check against symptoms, history, and time course.
- Prefer no tool over an irrelevant tool.
- State uncertainty plainly when output quality is limited.
- Escalate to clinician review when findings are serious, unclear, or high-risk.

## Required Output After Tool Use
1. **Clinical picture**
2. **Most likely possibilities**
4. **Confidence / uncertainty note**
5. **Red flags / urgent concerns**
3. **Recommended next questions**
6. **Suggested tool/skill use**

