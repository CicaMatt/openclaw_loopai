---
name: pipeline-generator
description: Generate an ML pipeline prototype by sending a user prompt to http://looporchestra.sytes.net:4010/nodes/ai_tool/AutoGen-model and reading the returned Answer field. Use only when the user explicitly asks for an ML pipeline prototype to be defined/generated, then explain the returned pipeline at a high level.
---

# Pipeline Generator

Generate a draft ML pipeline design from the remote AutoGen endpoint, then translate it into a concise, high-level explanation for the user.

## Workflow

1. Confirm the request is explicit.
   - Use this skill only if the user clearly asks for an ML pipeline prototype/definition.

2. Build the generation prompt.
   - Use the user request directly.
   - If details are missing, add minimal assumptions (data type, target, constraints) and label them as assumptions.

3. Call the endpoint.
   - Run:

```bash
python3 scripts/generate_pipeline.py "<prompt>"
```

- The script sends JSON input `{ "prompt": "..." }` to:
  `http://looporchestra.sytes.net:8001/nodes/ai_tool/AutoGen-model`
- It expects JSON output with `Answer` and prints that value. There is also the base64 of an image outputted, ignore it.

4. Explain the result at a high level.
   - Summarize the pipeline into plain language.
   - Cover: objective, data flow, model/training approach, evaluation, and deployment/monitoring idea.
   - Keep it strategic and high-level (avoid code-level detail unless asked).

5. Flag uncertainty.
   - If endpoint output is ambiguous, say what is unclear and propose a refined follow-up prompt.

## Output pattern

Return:

- **Generated pipeline (raw)**: short excerpt or full text (if short)
- **High-level explanation**: bullet summary of stages and purpose
