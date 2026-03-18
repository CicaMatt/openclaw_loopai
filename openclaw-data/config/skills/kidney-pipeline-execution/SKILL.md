---
name: kidney-pipeline-execution
description: Execute the kidney cancer CT pipeline by uploading a user-provided kidney CT image, taking the real uploaded image path returned by the upload endpoint, replacing the image-path placeholder inside the fixed prototype request JSON, then sending that request to the kidney pipeline execution endpoint and summarizing the Kidney Cancer Detector, Image Analyzer, and X-AI outputs. Use when a user wants to run the integrated kidney pipeline on a CT scan image and inspect either the raw response or a clean summary of the main outputs.
---

# Kidney Pipeline Execution

Upload the user image first, use the returned upload path in the fixed request template, then execute the kidney pipeline.

## Required behavior

Follow this sequence exactly:

1. Determine the local CT image to analyze.
   - Prefer the explicit user-provided local image path.
   - If no path is provided, use the newest supported image under `/home/node/.openclaw/media/inbound`.
2. Require the Telegram user id.
   - Pass it as `--telegram-user-id` or set `TELEGRAM_USER_ID`.
   - Use that value as the upload request's `user_id` query parameter.
3. Upload the image with `POST multipart/form-data` to:
   - `http://looporchestra.sytes.net:4001/nodes/input/upload?storage_ref=nodes_bucket&local_file_path=upload%2F&user_id=<telegram-user-id>`
4. Read the upload response JSON.
   - Build the real remote image path as `path + filename`.
   - Use the returned path from the upload response only.
   - Do not keep example paths, stale upload paths, or unresolved placeholders in the executed request.
5. Load `references/request-template.json`.
6. Replace every <image-path-here> placeholder in the template with the real uploaded image path (rows 56, 208, 305, 371, 396).
7. Send the resulting JSON payload to:
   - `http://looporchestra.sytes.net:4001/admin/prototype_execution/prototype_execution/`
8. Read the pipeline response and summarize it by module:
   - Kidney Cancer Detector
   - Image Analyzer
   - X-AI
9. If the analyzer image URL exists at `response.workflows[0].branches[0].nodes[0].children[0].children[0].tracking.parameters.file_path`, extract the URL and include the image in the normal reply.
10. Do not send out-of-band Telegram messages from the script.

## Fixed values

Keep these values fixed:
- `storage_ref`: `nodes_bucket`
- `local_file_path`: `upload/`
- execution endpoint: `http://looporchestra.sytes.net:4001/admin/prototype_execution/prototype_execution/`
- request template: `references/request-template.json`

## Implementation notes

- Treat the request template as a fixed prototype payload, but always inject the freshly uploaded image path before execution.
- Fail loudly if `<image_path_here>` remains anywhere in the payload after replacement.
- If template fields such as `filename`, `pdf_path`, or `File Path` contain placeholder or stale upload-path values, replace them with the fresh uploaded image path before execution.
- Preserve the response wrapper shape returned by the script.
- If the endpoint returns non-JSON text, return that text as the `response` value.

## Preferred script

Run:

```bash
python3 scripts/pipeline_execution_tool.py --telegram-user-id <telegram-user-id> [local-image-path]
```

If `local-image-path` is omitted, the script should select the newest supported image from `/home/node/.openclaw/media/inbound`.

## Summary fields to prioritize

When present, summarize these fields first.

### Kidney Cancer Detector
- `Inference time`
- `classes`
- `confidence`

### Image Analyzer
- `cam_metrics`
- `prediction`
- `cam_explanation`
- `file_path` when useful for returning the analyzer image

When `cam_metrics` is present, include all available subfields such as:
- `coverage`
- `center_ratio`
- `lr_asym`
- `tb_asym`

### X-AI
- `confidence_interpretation`
- `recommended_next_steps`
- `references`
- `summary`
- `visual_evidence`

Preserve list order for `recommended_next_steps`.
Preserve available fields in each reference item such as `title`, `author`, `year`, and `url`.

## User-facing reply rules

- Group the result into the three modules.
- Use readable labels instead of raw JSON paths.
- Do not include low-level execution metadata by default.
- Mention clearly that the pipeline output is a preliminary signal, not a diagnosis.
- Append the analyzer image itself when an analyzer image URL is available.
