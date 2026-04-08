---
name: slm-dermatology
description: Query a small language model (SLM) endpoint with dermatology expertise by asking a focused question about patient health data stored in records, skin symptoms, lesion descriptions, rash history, dermatology imaging context, or dermatology-relevant follow-up needs. Before each inference, first load the dermatology adapter with the fixed /node/load-adapter payload, then perform the query. Use when the agent needs a compact dermatology-specialist model pass over record-grounded or clearly provided skin-related context, and the SLM output should be processed rather than forwarded blindly.
---

# SLM Dermatology

Use this skill to ask the dermatology SLM a focused question about patient data or clearly stated conversation context that is relevant to skin symptoms, lesions, rashes, dermatology images, or dermatology follow-up, then process the answer in the calling agent.

## Workflow

1. Confirm the task is within dermatology scope.
   - Use this skill for skin-related interpretation, summarization, pattern spotting, follow-up reasoning, or record-grounded dermatology questions.
   - Prefer this skill when the user’s question concerns lesions, rashes, pigmentation changes, inflammatory skin disease, dermatology imaging context, or skin-focused differential support.
   - Do not use it for unrelated non-dermatology requests.

2. Build a focused question for the SLM.
   - Write a single clear dermatology question.
   - Ground the question in retrieved records, uploaded-image context already established by the agent, or clearly stated conversation facts.
   - Keep it concise and specific.
   - Do not invent findings, diagnoses, timelines, or morphology details.
   - Good examples:
     - `Based on this lesion description and image summary, which dermatology features are most concerning and what follow-up is most appropriate?`
     - `From this patient record, what findings most strongly support inflammatory dermatitis rather than an infectious rash?`
     - `What dermatology-focused differential diagnoses best fit this chronic pruritic plaque history?`
     - `Which missing skin-history details would matter most before interpreting this pigmented lesion?`

3. Load the dermatology adapter before every inference.
   - Always do the adapter-load step immediately before the chat query.
   - Run:

```bash
python3 scripts/query_slm_dermatology.py "<question>"
```

   - The script first sends this payload to the adapter-loading endpoint:

```json
{
  "model": "tinyllama",
  "adapter_path": "adapters/derma_v1.0",
  "mode": "derma"
}
```

   - Adapter endpoint:

```text
http://looporchestra.sytes.net:8007/node/load-adapter
```

   - It then sends the inference payload:

```json
{
  "question": "<question>"
}
```

   - Chat endpoint:

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
   - Cross-check it against the actual record or conversation context already available.
   - Preserve uncertainty and avoid overstating confidence.
   - If clinically relevant, highlight missing dermatology history, red flags, or next-step questions.
   - Treat the output as supportive specialty inference, not as a confirmed diagnosis.

## Output pattern

Return a response that includes:

- **SLM finding**: the key content from the model answer, cleaned up if needed
- **Agent interpretation**: the calling agent’s processed interpretation grounded in the available context
- **Cautions / next steps**: only when relevant
