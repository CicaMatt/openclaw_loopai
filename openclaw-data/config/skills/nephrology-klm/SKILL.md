---
name: nephrology-klm
description: Query the Nephrology-KLM knowledge model for nephrology expertise, differential-diagnosis support, disease-specific interpretation, and specialized kidney-related feedback. Use when the user needs nephrology-domain guidance about CKD, AKI, glomerular disease, dialysis, electrolyte/acid-base disorders, renal imaging findings, nephrology treatment considerations, or kidney-focused diagnosis/expertise.
---

# Nephrology KLM

Query the remote Nephrology-KLM endpoint and translate its output into safe, concise nephrology-oriented guidance.

## Workflow

1. Confirm the request is nephrology-specific.
   - Use this skill for kidney disease, renal oncology, nephrology treatment questions, renal function interpretation, dialysis topics, electrolyte or acid-base issues, and nephrology differential support.
   - Do not use it for unrelated specialties.

2. Build the prompt.
   - Use the user's question directly when it is already specific.
   - If the user provides case details, summarize them into one clear nephrology prompt.
   - If assumptions are needed, state them explicitly.

3. Call the endpoint.
   - Run:

```bash
python3 scripts/query_nephrology_klm.py "<prompt>"
```

- The script sends:

```json
{
  "metadata": {
    "name": "nephrology-klm",
    "workflow_name": "nephrology-klm",
    "workflow_type": "experiment",
    "workflow_id": "nephrology-klm",
    "workflow_run_id": "manual",
    "run_id": "manual"
  },
  "data": {
    "prompt": "<prompt>"
  }
}
```

- Endpoint:
  `http://looporchestra.sytes.net:8001/nodes/ai_tool/Nephrology-KLM-model`

4. Read the response.
   - Prefer the returned `data.Answer` field.
   - If that field contains a JSON string, extract the `answer` text when possible.
   - If parsing fails, return the raw answer text and note the ambiguity.

5. Respond safely.
   - Summarize the nephrology answer in plain language.
   - Separate model output from your own cautionary framing.
   - Avoid presenting the KLM output as certain or as a substitute for clinician judgment.
   - If urgent red flags appear, recommend prompt in-person medical evaluation.

## Output pattern

Return:

- **Nephrology KLM answer**: short excerpt or the full answer if compact
- **Plain-language summary**: the main nephrology takeaway
- **Important cautions / next steps**: especially when diagnosis or treatment decisions need clinical confirmation
