---
name: skin-cancer-pipeline
description: Execute the skin cancer image pipeline by uploading a user-provided skin image through the same upload endpoint used by the kidney pipeline, taking the real uploaded image path returned by that endpoint, replacing the image-path placeholders inside the fixed skin-cancer prototype request JSON, then sending the built request to the same prototype execution endpoint and returning the pipeline response plus any analyzer image URL for normal chat forwarding. Use when a user wants to run the integrated skin-cancer pipeline on an uploaded image and inspect either the raw response or a clean summary of the main outputs.
---

# Skin Cancer Pipeline

Upload the user image first, use the returned upload path in the fixed request template, then execute the skin-cancer pipeline.

## Required behavior

Follow this sequence exactly:

1. Determine the local image to analyze.
   - Prefer the explicit user-provided local image path.
   - If no path is provided, use the newest supported image under `/home/node/.openclaw/media/inbound`.
2. Require the Telegram user id.
   - Pass it as `--telegram-user-id` or set `TELEGRAM_USER_ID`.
   - Use that value as the upload request's `user_id` query parameter.
3. Upload the image with `POST multipart/form-data` to:
   - `http://looporchestra.sytes.net:4001/nodes/input/upload?storage_ref=nodes_bucket&local_file_path=upload/&user_id=<telegram-user-id>`
   - Construct the multipart body in the same style as the provided `urllib.request` implementation:
     - read the file bytes first
     - generate `boundary = uuid.uuid4().hex`
     - build the body manually with the single `file` part
     - set `Content-Type: multipart/form-data; boundary=<boundary>`
     - set `Content-Length` to the exact byte length of the body
4. Read the upload response JSON.
   - Build the real remote image path as `path + filename`.
   - Replace the request template placeholders with that returned uploaded path only.
   - Do not keep example paths, stale upload paths, or unresolved placeholders in the executed request.
5. Load `references/request-template.json`.
6. Replace every `<image-path-here>` placeholder in the template with the real uploaded image path.
7. Send the resulting JSON payload to:
   - `http://looporchestra.sytes.net:4001/admin/prototype_execution/prototype_execution/`
8. Read the pipeline response and preserve the JSON wrapper shape returned by the script.
9. Normalize the endpoint response into a meaningful top-level JSON summary under `meaningful_response`, mirroring the kidney pipeline pattern but using the skin pipeline metrics.
   - Include `skin_cancer_detector.inference_time`, `skin_cancer_detector.class`, and `skin_cancer_detector.confidence`.
   - Include `image_analyzer.prediction`, `image_analyzer.cam_coverage`, `image_analyzer.cam_center_ratio`, `image_analyzer.cam_left_right_asymmetry`, `image_analyzer.cam_top_bottom_asymmetry`, `image_analyzer.cam_explanation`, and `image_analyzer.analyzer_image_url` when present.
   - Include X-AI fields under `xai`: `confidence_interpretation`, `recommended_next_steps`, `references`, `summary`, and `visual_evidence`.
10. If an analyzer image URL exists in the response, extract it and include the image in the normal reply.
11. Do not send out-of-band Telegram messages from the script.

## Fixed values

Keep these values fixed:
- `storage_ref`: `nodes_bucket`
- `local_file_path`: `upload/`
- execution endpoint: `http://looporchestra.sytes.net:4001/admin/prototype_execution/prototype_execution/`
- request template: `references/request-template.json`

## Implementation notes

- Treat the request template as a fixed prototype payload, but always inject the freshly uploaded image path before execution.
- Keep the upload implementation aligned with the explicit `urllib.request` pattern requested by the user: manual multipart assembly, UUID boundary, and explicit `Content-Length`.
- Fail loudly if `<image-path-here>` remains anywhere in the payload after replacement.
- If the endpoint returns non-JSON text, return that text as the `response` value.
- Preserve the response wrapper shape returned by the script.
- Add a normalized `meaningful_response` object so callers can rely on a concise, clinically meaningful JSON summary instead of re-parsing raw workflow paths.
- Retain analyzer-image extraction in the script so the calling agent can forward the image through the chat.

## Preferred script

Run:

```bash
python3 scripts/pipeline_execution_tool.py --telegram-user-id <telegram-user-id> [local-image-path]
```

If `local-image-path` is omitted, the script should select the newest supported image from `/home/node/.openclaw/media/inbound`.

## Summary fields to prioritize

When present, summarize these fields first.

### Skin Cancer Detection
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
