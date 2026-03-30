---
name: slm-inference
description: Query a small language model (SLM) endpoint with expertise in nephrology, cardiology, and hypertension by asking a focused question about patient health data stored in records, then use the returned answer as an input to the calling agent’s own reasoning. Use when the agent needs a compact model pass over patient-record data for kidney, cardiovascular, or blood-pressure-related interpretation, hypothesis generation, summarization, or record-grounded follow-up support, and the SLM output should be processed rather than forwarded blindly.
---

# SLM Inference

Use this skill to ask the SLM a focused health question about patient data already available in records, especially when nephrology, cardiology, or hypertension expertise is useful, then process the answer in the calling agent.

## Workflow

1. Confirm the task is record-grounded and within scope.
   - Use this skill when the question should be answered from patient health data stored in records.
   - Prefer this skill for compact inference, interpretation, summarization, pattern spotting, or follow-up reasoning over stored health data.
   - This SLM is especially suitable for nephrology, cardiology, and hypertension-related questions.
   - Do not use it when the request is unrelated to patient records.

2. Build a focused question for the SLM.
   - Write a single clear question about the patient’s health data in records.
   - Ground the question in the known record context already retrieved by the agent.
   - Keep it concise and specific.
   - Do not invent record contents.
   - Prefer questions that benefit from nephrology, cardiology, or hypertension expertise.
   - Good examples:
     - `Based on this patient record, what are the main kidney-related concerns that need follow-up?`
     - `From the stored health record, what findings most strongly suggest CKD progression?`
     - `What cardiovascular risks stand out most from this patient’s diagnoses, medications, and recent labs?`
     - `Which parts of this record most strongly support poorly controlled hypertension or target-organ impact?`

3. Call the endpoint.
   - Run:

```bash
python3 scripts/query_slm_inference.py "<question>"
```

   - The script sends this payload shape:

```json
{
  "question": "<question>"
}
```

   - Endpoint:

```text
http://looporchestra.sytes.net:8007/chat
```

4. Read the response.
   - Prefer a clean text answer.
   - Accept common shapes such as `answer`, `Answer`, `response`, `message`, or raw text.
   - If the endpoint returns nested JSON encoded as a string, extract the useful answer text when possible.
   - If parsing is ambiguous, keep the best raw text and say so briefly in your own reasoning.

5. Process the SLM answer in the calling agent.
   - Do not treat the SLM output as the final user-facing answer by default.
   - Use it as an input to the agent’s own reasoning, synthesis, or explanation.
   - Cross-check it against the actual patient record context already available.
   - Preserve uncertainty and avoid overstating confidence.
   - If clinically relevant, highlight missing data, red flags, or next-step questions.
   - Treat the output as supportive specialty inference, not as a confirmed diagnosis.

## Output pattern

Return a response that includes:

- **SLM finding**: the key content from the model answer, cleaned up if needed
- **Agent interpretation**: the calling agent’s processed interpretation grounded in the records
- **Cautions / next steps**: only when relevant