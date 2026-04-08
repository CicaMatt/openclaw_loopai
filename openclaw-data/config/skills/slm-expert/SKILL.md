---
name: slm-expert
description: Query a small language model (SLM) endpoint with expertise in nephrology, cardiology, and hypertension by sending a focused question together with one or more required medical domains and a fixed blank patient_context object. Use when the agent needs a specialty-aware answer or supporting interpretation in those domains and must explicitly set the `domains` field on every request.
---

# SLM Expert

Use this skill to query the specialty SLM at `http://looporchestra.sytes.net:8008/query` for nephrology, cardiology, or hypertension questions.

## Workflow

1. Confirm the request is in scope.
   - Use this skill for nephrology, cardiology, or hypertension questions.
   - Use it when the question needs explicit specialty routing through the `domains` field.
   - Do not use it for unrelated specialties.

2. Build the question.
   - Write one clear, focused question.
   - Use the user's wording directly when it is already specific.
   - If the user gives case details, compress them into a concise specialty question.
   - Do not invent missing facts.

3. Choose the domains.
   - Always set the `domains` field together with the `question`.
   - Include one or more of these values only: `nephrology`, `cardiology`, `hypertension`.
   - Choose the narrowest correct set.
   - Use multiple domains only when the question genuinely spans them.
   - Example mappings:
     - Kidney disease, CKD, AKI, proteinuria, renal medication issues -> `nephrology`
     - Cardiovascular risk, heart disease, lipid therapy, cardiac findings -> `cardiology`
     - Blood pressure control, hypertensive organ damage, antihypertensive strategy -> `hypertension`
     - Hypertensive kidney damage -> `nephrology`, `hypertension`

4. Leave patient context as the fixed blank object.
   - Always send `patient_context`.
   - Do not pass case-specific or real patient details in `patient_context`.
   - Use this exact shape:

```json
{"patient_context":{"additionalProp1":{}}}
```

5. Call the endpoint.
   - Run the helper script from the skill directory:

```bash
python3 scripts/query_slm_expert.py \
  --question "What signs of kidney damage should be monitored in hypertensive patients?" \
  --domain nephrology \
  --domain hypertension
```

   - The helper always sends a fixed blank `patient_context` object.

   - The script sends this payload shape:

```json
{
  "question": "string",
  "domains": ["string"],
  "patient_context": {
    "additionalProp1": {}
  }
}
```

   - Endpoint:

```text
http://looporchestra.sytes.net:8008/query
```

6. Read the response.
   - Prefer `answer` as the main model output.
   - Read `domain` as the model-selected or echoed specialty scope.
   - Treat `sources` as optional supporting metadata.
   - If the answer is `Not found in context.`, report that plainly instead of inventing content.

7. Use the result safely.
   - Treat the SLM output as supportive specialty input, not a confirmed diagnosis.
   - Cross-check it against the available patient details and the user’s question.
   - Preserve uncertainty.
   - If the output is thin or context-limited, say so.

## Request examples

Use patterns like these:

```json
{"question": "When is medication recommended for cardiovascular risk factor management?", "domains": ["cardiology"]}
{"question": "Why do patients with CKD require careful medication management?", "domains": ["nephrology"]}
{"question": "What signs of kidney damage should be monitored in hypertensive patients?", "domains": ["nephrology", "hypertension"]}
```

## Output pattern

Return a response that includes, when useful:

- **SLM answer**: the key answer text
- **Domain(s)**: the domains used or returned
- **Agent interpretation**: a short grounded interpretation
- **Cautions / gaps**: especially when the model says context is missing or the answer is limited
