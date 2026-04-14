---
name: slm-expert-backup
description: Query a small language model (SLM) endpoint with nephrology, cardiology, and hypertension expertise by asking a focused question about patient health data stored in records, kidney symptoms, blood-pressure history, cardiovascular findings, renal imaging context, or specialty-relevant follow-up needs. Perform the query directly through /chat. Use when the agent needs a compact nephrology/cardiology/hypertension-specialist model pass over record-grounded or clearly provided context, and the SLM output should be processed rather than forwarded blindly.
---

# SLM Expert Backup

Use this skill to ask the specialty SLM a focused question about patient data or clearly stated conversation context that is relevant to nephrology, cardiology, or hypertension, then process the answer in the calling agent.

## Workflow

1. Confirm the task is within nephrology, cardiology, or hypertension scope.
   - Use this skill for kidney-, blood-pressure-, or cardiovascular-related interpretation, summarization, pattern spotting, follow-up reasoning, or record-grounded specialty questions.
   - Prefer this skill when the user’s question concerns CKD, AKI, proteinuria, hematuria, electrolyte or acid-base issues, blood-pressure control, resistant hypertension, hypertensive organ damage, heart failure, ischemic symptoms, cardiovascular risk, or specialty follow-up.
   - Do not use it for unrelated non-nephrology/non-cardiology/non-hypertension requests.

2. Build a focused question for the SLM.
   - Write a single clear specialty question.
   - Ground the question in retrieved records, renal/cardiovascular context already established by the agent, or clearly stated conversation facts.
   - Keep it concise and specific.
   - Do not invent findings, diagnoses, timelines, lab values, or imaging details.
   - Good examples:
     - `Based on this kidney-history summary, which findings most strongly support CKD progression and what follow-up is most appropriate?`
     - `From this blood-pressure history, what findings most suggest resistant hypertension and which missing details matter most?`
     - `Given this cardiovascular history and symptom summary, which cardiology concerns are most important to prioritize?`
     - `Which nephrology-focused factors best explain worsening renal function in this hypertension context?`

3. Query the specialty SLM directly.
   - Run:

```bash
python3 scripts/query_slm_expert_backup.py "<question>"
```

   - The script sends the inference payload:

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
   - If clinically relevant, highlight missing nephrology, cardiology, or hypertension history, red flags, or next-step questions.
   - Treat the output as supportive specialty inference, not as a confirmed diagnosis.

## Output pattern

Return a response that includes:

- **SLM finding**: the key content from the model answer, cleaned up if needed
- **Agent interpretation**: the calling agent’s processed interpretation grounded in the available context
- **Cautions / next steps**: only when relevant
