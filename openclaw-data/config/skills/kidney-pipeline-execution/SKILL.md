---
name: kidney-pipeline-execution
description: Execute the kidney cancer detection pipeline by first uploading a user-provided image with the same upload flow and Telegram user id logic used by the kidney-cancer-detection skill, then replacing the image-path placeholder in the stored prototype request JSON and sending it to the prototype execution endpoint. Use when a user wants to run this integrated kidney pipeline on an image and inspect either the raw response or the expected key outputs from the kidney cancer detector, the Image Analyzer, and the X-AI component.
---

# Kidney Pipeline Execution

Upload the local image first, then execute the fixed kidney cancer detection prototype payload with the uploaded remote image path substituted into the request JSON. This pipeline includes a Kidney Cancer Detection model, an Image Analyzer component, and an integrated X-AI component downstream.

## Workflow

1. Determine the local image to analyze.
   - Prefer an explicit local file path when one is available.
   - If no path is provided, use the most recent supported image under `/home/node/.openclaw/media/inbound`.
2. Require the Telegram user id.
   - Pass it as `--telegram-user-id` or set `TELEGRAM_USER_ID`.
   - Use that value as the upload request's `user_id` query parameter.
3. Upload the image with a `POST multipart/form-data` request to:
   - `http://looporchestra.sytes.net:4001/nodes/input/upload?storage_ref=nodes_bucket&local_file_path=upload%2F&user_id=<telegram-user-id>`
4. Read the upload response JSON and build the remote image path by concatenating:
   - `path + filename`
5. Replace every `<image_path_here>` placeholder in the fixed prototype JSON with the uploaded remote image path.
6. Send the full resulting JSON payload to:
   - `http://looporchestra.sytes.net:4001/admin/prototype_execution/prototype_execution/`
7. Return the raw response inside a minimal envelope that includes:
   - `uploaded_image_path`
   - `endpoint`
   - `http_status`
   - `content_type`
   - `response`
8. When summarizing the result for the user, expect and prioritize these wanted output fields from the raw response:
   - `response.workflows[0].branches[0].nodes[0].children[0].tracking.parameters.classes`
   - `response.workflows[0].branches[0].nodes[0].children[0].tracking.parameters.confidence`
   - `response.workflows[0].branches[0].nodes[0].children[0].children[0].tracking.parameters.prediction`
   - every available `cam_...` field under the Image Analyzer tracking parameters, including the full `cam_metrics` object and any other `cam_*` entries such as `cam_explanation`
   - `response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.confidence_interpretation`
   - `response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.recommended_next_steps`
   - `response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.references`
   - `response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.summary`
   - `response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.visual_evidence`
9. Present those wanted outputs in a clean human-readable summary instead of low-level JSON-path labels. Prefer labels such as `Kidney cancer class`, `Confidence`, `Image Analyzer prediction`, `CAM coverage`, `CAM center ratio`, `CAM left-right asymmetry`, `CAM top-bottom asymmetry`, `CAM explanation`, `Confidence interpretation`, `Recommended next steps`, `References`, `Summary`, and `Visual evidence`.
10. Do not include low-level run details by default in user-facing replies. Omit technical execution metadata such as upload paths, endpoint names, HTTP status, node ids, workflow ids, raw file paths, and similar run-internal fields unless the user explicitly asks for technical details or the raw response.
11. Mention, when present, that the broader raw response may also include an analyzer output `file_path` plus X-AI explanatory fields such as `confidence_interpretation`, `recommended_next_steps`, `references`, `summary`, and `visual_evidence`.

## Fixed request values

Keep these values static:
- `storage_ref`: `nodes_bucket`
- `local_file_path`: `upload/`
- execution endpoint: `http://looporchestra.sytes.net:4001/admin/prototype_execution/prototype_execution/`
- prototype payload: use the fixed JSON embedded in `scripts/pipeline_execution_tool.py`

## What this skill runs

```bash
python3 scripts/pipeline_execution_tool.py --telegram-user-id <telegram-user-id> [local-image-path]
```

If `local-image-path` is omitted, the script automatically selects the newest supported image from `/home/node/.openclaw/media/inbound`.

## Upload response handling

Given an upload response like:

```json
{
  "path": "upload/2026-03-15_14.52.42_5EdSbYnzCrKdhainPvGx/",
  "filename": "9dd106ff-65ad-4a16-a381-6d76e4845c9c.jpg",
  "column_names": null
}
```

Build:

```text
image_path = "upload/2026-03-15_14.52.42_5EdSbYnzCrKdhainPvGx/9dd106ff-65ad-4a16-a381-6d76e4845c9c.jpg"
```

Use that full value anywhere the request JSON contains `<image_path_here>`.

## Expected output

Expect a stable high-level wrapper plus a kidney-pipeline-oriented response body.

Return the endpoint response inside this wrapper:

```json
{
  "uploaded_image_path": "string",
  "endpoint": "string",
  "http_status": 200,
  "content_type": "application/json",
  "response": {}
}
```

For user-facing summaries, treat these as the primary expected outputs when present:

```json
{
  "wanted_output_fields": {
    "kidney_cancer_class": "response.workflows[0].branches[0].nodes[0].children[0].tracking.parameters.classes",
    "kidney_cancer_confidence": "response.workflows[0].branches[0].nodes[0].children[0].tracking.parameters.confidence",
    "image_analyzer_prediction": "response.workflows[0].branches[0].nodes[0].children[0].children[0].tracking.parameters.prediction",
    "cam_metrics": "response.workflows[0].branches[0].nodes[0].children[0].children[0].tracking.parameters.cam_metrics",
    "cam_explanation": "response.workflows[0].branches[0].nodes[0].children[0].children[0].tracking.parameters.cam_explanation",
    "confidence_interpretation": "response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.confidence_interpretation",
    "recommended_next_steps": "response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.recommended_next_steps",
    "references": "response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.references",
    "summary": "response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.summary",
    "visual_evidence": "response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.visual_evidence"
  }
}
```

When `cam_metrics` is present, include all of its subfields in the wanted output summary, such as:
- `coverage`
- `center_ratio`
- `lr_asym`
- `tb_asym`

Also include these secondary fields when useful:
- `response.workflows[0].branches[0].nodes[0].children[0].children[0].tracking.parameters.file_path`

When `recommended_next_steps` is present, preserve the list order. When `references` is present, preserve each item's available fields such as `title`, `author`, `year`, and `url`.

Do not present the summary as raw JSON-path labels unless the user explicitly asks for raw field paths. Default to a cleaner format with readable labels and grouped findings.
Do not include low-level run details in the default summary. Reserve upload paths, endpoint values, HTTP status, execution metadata, node identifiers, and other run-internal fields for explicit technical or debugging requests.

If the endpoint returns non-JSON text, return that text as the `response` value.
