# TOOLS.md - Medical Skills & Capability Notes

## pipeline-generator
- **Role:** Broader ecosystem ML pipeline generation capability.
- **Use for:** rare medical systems-design discussions, not routine patient diagnostic support.
- **Limits:** Not a diagnostic authority and should not shape clinical conclusions directly.

## kidney-pipeline-execution
- **Role:** Execute the fixed kidney cancer detection pipeline starting from an image file.
- **Use for:** running the integrated kidney pipeline when an image should be uploaded and passed through the Kidney Cancer Detection model, the Image Analyzer component, and the downstream X-AI component.
- **Suggestion rule:** If the diagnostic impression raises kidney-focused problems or a possible renal mass concern, suggest that the user can run this specialized pipeline and invite them to upload a CT image scan.
- **Meaning:** Produces a preliminary pipeline result structure; for quick summaries, prioritize these wanted outputs when present: the kidney cancer class, the kidney cancer confidence, the Image Analyzer prediction, and all available `cam_...` fields from the Image Analyzer output, especially the full `cam_metrics` set and `cam_explanation`.
- **Presentation rule:** When reporting results to the user, do not default to low-level JSON labels. Present them in a cleaner summary with readable labels such as `Kidney cancer class`, `Confidence`, `Image Analyzer prediction`, `CAM coverage`, `CAM center ratio`, `CAM left-right asymmetry`, `CAM top-bottom asymmetry`, and `CAM explanation`.
- **Default verbosity rule:** Do not include low-level run details in normal replies. Omit upload paths, endpoint values, HTTP status, node ids, workflow ids, raw file paths, and other execution metadata unless the user explicitly asks for technical or raw output.
- **Limits:** This is still a prototype pipeline output, not a diagnosis. The X-AI component may be integrated in the workflow even when its own returned tracking data is limited.
- **Output message:** Always remember to the use that the tool output as a preliminary signal, not as an actual diagnosis.

## skin-cancer-pipeline
- **Role:** Execute the fixed skin cancer detection pipeline starting from a skin image file.
- **Use for:** running the integrated skin pipeline when an image should be uploaded and passed through the Skin Cancer Detection model, the Image Analyzer component, and the downstream X-AI component.
- **Suggestion rule:** If the diagnostic impression raises concern for a suspicious skin lesion or possible skin malignancy, suggest that the user can run this specialized pipeline and invite them to upload a skin image.
- **Meaning:** Produces a preliminary pipeline result structure; for quick summaries, prioritize these wanted outputs when present: the skin cancer class, the skin cancer confidence, the Image Analyzer prediction, and all available `cam_...` fields from the Image Analyzer output, especially the full `cam_metrics` set and `cam_explanation`.
- **Presentation rule:** When reporting results to the user, do not default to low-level JSON labels. Present them in a cleaner summary with readable labels such as `Skin cancer class`, `Confidence`, `Image Analyzer prediction`, `CAM coverage`, `CAM center ratio`, `CAM left-right asymmetry`, `CAM top-bottom asymmetry`, and `CAM explanation`.
- **Default verbosity rule:** Do not include low-level run details in normal replies. Omit upload paths, endpoint values, HTTP status, node ids, workflow ids, raw file paths, and other execution metadata unless the user explicitly asks for technical or raw output.
- **Limits:** This is still a prototype pipeline output, not a diagnosis. The X-AI component may be integrated in the workflow even when its own returned tracking data is limited.
- **Output message:** Always remember to tell the user that the tool output is a preliminary signal, not an actual diagnosis.

## depression-pipeline
- **Role:** Execute the fixed voice depression pipeline starting from an uploaded audio file.
- **Use for:** running the integrated audio pipeline when a user provides a voice recording that should be uploaded and passed through the Voice Depression Detection model and the Fuzzy Stress Evaluator.
- **Meaning:** Produces a preliminary pipeline result structure; for summaries, prioritize the Voice Depression Detection class, confidence, inference time, and any returned stress label, score, confidence, or explanation from the Fuzzy Stress Evaluator.
- **Presentation rule:** Group the reply into the two modules, use readable labels instead of raw JSON paths, and omit low-level execution metadata unless the user explicitly asks for the raw or technical response.
- **Limits:** This is still a prototype pipeline output, not a diagnosis. Some runs may complete the upload and input stages but fail to expose downstream model outputs in the returned payload.
- **Output message:** Always tell the user that the tool output is a preliminary signal, not an actual diagnosis.

## llm_distillator
- **Role:** Distill the outputs of one or more diagnostic tools together with the symptom discussion and immediate conversation context into a clear patient-facing summary.
- **Use for:** after symptoms have already been discussed and a diagnostic tool has just run, especially when its output needs to be translated into a coherent explanation for the user.
- **Suggestion rule:** Suggest this skill only once there has been enough symptom discussion to frame the case and a tool has just produced a diagnostic result or preliminary diagnosis.
- **Presentation rule:** Use it to convert raw or fragmented tool output into a concise explanation that matches the agent’s diagnostic output structure and preserves the distinction between tool findings and clinical interpretation.
- **Safety rule:** Present the distilled result as a preliminary interpretation, not a confirmed diagnosis, and keep uncertainty visible when the upstream tool output is limited or ambiguous.

## patient-klm
- **Role:** Patient-specific knowledge base skill for retrieving live structured health context, including symptom history, visits, disease timeline, genomics, and custom patient facts.
- **Use for:** when the user reports symptoms and patient-specific context could materially improve interpretation, first retrieve the latest relevant patient record through the patient-klm skill, then combine that structured report with the user’s current symptom description.
- **Default patient rule:** If the user asks for patient knowledge base access without specifying a patient, default to patient_id `P-001`.
- **Presentation rule:** Integrate the fetched report with the newly reported symptoms into one coherent clinical picture. Clearly distinguish what came from the patient knowledge base versus what the user reported now when that distinction matters.
- **Safety rule:** Treat patient-klm output as supporting clinical context, not final truth. Do not overstate certainty, do not invent missing facts, and say when important context is still missing.
- **Answering rule:** After incorporating the updated report, provide a comprehensive but careful explanation of the user’s likely health situation, including uncertainty, red flags, and next-step guidance when relevant.

## slm-expert
- **Role:** Record-grounded SLM consultation skill that queries a small language model with expertise in nephrology, cardiology, and hypertension.
- **Use for:** when the agent has already retrieved patient records and wants a focused model pass for kidney-related, cardiovascular, or blood-pressure-related interpretation, summarization, hypothesis generation, or follow-up support grounded in stored health data.
- **Question rule:** Send one concise question about patient health data stored in records, not a vague multi-part prompt.
- **Presentation rule:** Treat the SLM answer as an intermediate signal to be processed by the calling agent, not as a final verdict to relay blindly.
- **Safety rule:** Cross-check the SLM output against the actual records, keep uncertainty visible, and do not present it as a confirmed diagnosis.

## slm-dermatology
- **Role:** Dermatology-focused SLM consultation skill that queries a small language model after first loading the dermatology adapter.
- **Use for:** when the agent has already retrieved relevant patient context and wants a focused dermatology model pass for lesions, rashes, skin-history interpretation, dermatology image context, hypothesis generation, summarization, or follow-up support grounded in available data.
- **Question rule:** Send one concise dermatology question grounded in records or clearly established conversation context, not a vague multi-part prompt.
- **Execution rule:** Before every inference, first call `/node/load-adapter` with the fixed payload for `tinyllama`, `adapters/derma_v1.0`, and `mode` `derma`, then perform the chat query.
- **Presentation rule:** Treat the SLM answer as an intermediate signal to be processed by the calling agent, not as a final verdict to relay blindly.
- **Safety rule:** Cross-check the SLM output against the actual context, keep uncertainty visible, and do not present it as a confirmed diagnosis.

## Interpretation Rules
- State uncertainty plainly when output quality is limited.