---
name: depression-pipeline
description: Execute the voice depression pipeline by uploading a user-provided audio file, taking the real uploaded file path returned by the shared upload endpoint, replacing the fixed path placeholder inside the prototype request JSON, then sending the built request to the shared prototype execution endpoint and summarizing the Voice Depression Detection and Fuzzy Stress Evaluator outputs. Use when a user wants to run the depression audio pipeline on a chat-provided audio file and inspect either the raw response or a clean summary of the main outputs.
---

# Depression Pipeline

Upload the user audio first, use the returned upload path in the fixed request template, then execute the depression pipeline.

## Required behavior

Follow this sequence exactly:

1. Determine the local audio file to analyze.
   - Prefer the explicit user-provided local audio path.
   - If no path is provided, use the newest supported audio file under `/home/node/.openclaw/media/inbound`.
2. Require the Telegram user id.
   - Pass it as `--telegram-user-id` or set `TELEGRAM_USER_ID`.
   - Use that value as the upload request's `user_id` query parameter.
3. Upload the audio with `POST multipart/form-data` to:
   - `http://looporchestra.sytes.net:4001/nodes/input/upload?storage_ref=nodes_bucket&local_file_path=upload%2F&user_id=<telegram-user-id>`
4. Read the upload response JSON.
   - Build the real remote audio path as `path + filename`.
   - Use the returned path from the upload response only.
   - Do not keep example paths, stale upload paths, or unresolved placeholders in the executed request.
5. Load `references/request-template.json`.
6. Replace every `<audio-path-here>` placeholder in the template with the real uploaded audio path.
7. Send the resulting JSON payload to:
   - `http://looporchestra.sytes.net:4001/admin/prototype_execution/prototype_execution/`
8. Read the pipeline response and summarize it by module:
   - Voice Depression Detection
   - Fuzzy Stress Evaluator


## Fixed values

Keep these values fixed:
- `storage_ref`: `nodes_bucket`
- `local_file_path`: `upload/`
- execution endpoint: `http://looporchestra.sytes.net:4001/admin/prototype_execution/prototype_execution/`
- request template: `references/request-template.json`

## Implementation notes

- Treat the request template as a fixed prototype payload, but always inject the freshly uploaded audio path before execution.
- Fail loudly if `<audio_path_here>` remains anywhere in the payload after replacement.
- If template fields such as `filename`, `pdf_path`, or `File Path` contain placeholder or stale upload-path values, replace them with the fresh uploaded audio path before execution.
- Preserve the response wrapper shape returned by the script.
- If the endpoint returns non-JSON text, return that text as the `response` value.

## Preferred script

Run:

```bash
python3 scripts/pipeline_execution_tool.py --telegram-user-id <telegram-user-id> [--include-timeline] [local-audio-path]
```

If `local-audio-path` is omitted, the script should select the newest supported audio file from `/home/node/.openclaw/media/inbound`.

## Summary fields to prioritize

Extract module metrics from the actual tracking parameter objects in the execution response.

### Voice Depression Detection
- Primary path: `workflows[0].branches[0].nodes[0].children[0].tracking.parameters`
- Extract these fields first when present:
  - `Inference time`
  - `classes`
  - `confidence`
- Present them with readable labels such as:
  - `Inference time`
  - `Class`
  - `Confidence`
- If extra useful fields appear under the same tracking object, include them only when they add clear value.

### Fuzzy Stress Evaluator
- Primary path: `workflows[0].branches[0].nodes[0].children[0].children[0].tracking.parameters`
- Extract these fields first when present:
  - `stress_level`
  - `formatted`
  - `lambda`
  - `confidence`
  - `score`
  - `explanation`
  - `timeline`
- Present them with readable labels such as:
  - `Stress level`
  - `Score` for `formatted` or `score`
  - `Lambda`
  - `Confidence`
  - `Explanation`
- Include `timeline` only when the user asks for more detail or when it materially helps explain the result.
- The helper script should keep `Timeline` out of `user_summary` by default and include it only when `--include-timeline` is passed.

### Actual observed outputs from real runs
- Voice Depression Detection has returned values such as:
  - `classes: Minimal`
  - `confidence: 0.0`
  - `classes: Moderate`
  - `confidence: 11.3`
- Fuzzy Stress Evaluator has returned values such as:
  - `stress_level: Low`, `formatted: 0.200`, `lambda: 0.20014652301190844`
  - `stress_level: Moderate`, `formatted: 0.385`, `lambda: 0.3851116997420148`

## User-facing reply rules

- Prefer a normalized `user_summary` object from the helper script when available.
- Group the result into the two modules.
- Use readable labels instead of raw JSON paths.
- Do not include low-level execution metadata by default.
- Mention clearly that the pipeline output is a preliminary signal, not a diagnosis.
- Do not attach or send any image in the normal reply for this skill.
