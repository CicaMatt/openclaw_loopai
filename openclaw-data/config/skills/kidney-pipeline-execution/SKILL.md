---
name: kidney-pipeline-execution
description: Execute the kidney cancer detection pipeline by first uploading a user-provided image with the same upload flow and Telegram user id logic used by the kidney-cancer-detection skill, then replacing the image-path placeholder in the stored prototype request JSON and sending it to the prototype execution endpoint. Use when a user wants to run this integrated kidney pipeline on an image and inspect either the raw response or the expected key outputs from the kidney cancer detector, the Image Analyzer, and the X-AI component.
---

# Kidney Pipeline Execution

Upload the local image first, then execute the fixed kidney cancer detection prototype payload with the uploaded remote image path substituted into the request JSON.

Treat this pipeline as a 3-module flow:
1. **Kidney Cancer Detector module**
2. **Image Analyzer module**
3. **X-AI module**

Keep that structure explicit when reading results and when summarizing each run for the user.

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
5. Replace the `<image_path_here>` placeholder in the fixed prototype JSON with the uploaded remote image path.
6. Send the full resulting JSON payload to:
   - `http://looporchestra.sytes.net:4001/admin/prototype_execution/prototype_execution/`
7. Read the analyzer image URL from `response.workflows[0].branches[0].nodes[0].children[0].children[0].tracking.parameters.file_path`.
   - Extract the URL from that field.
   - Do **not** send out-of-band Telegram messages from the script itself.
   - Return the analyzer image URL in the tool output and let the parent agent include it in the normal reply to the active conversation.
   - This avoids accidental delivery to the wrong chat or a stale target.
8. Return the raw response inside a minimal envelope that includes:
   - `uploaded_image_path`
   - `endpoint`
   - `http_status`
   - `content_type`
   - `response`
   - when available, also include `analyzer_image_url` and `sent_result_image`
9. If `analyzer_image_url` is available, include the analyzer image in the user-facing reply itself.
   - Prefer attaching or embedding it in the same reply that summarizes the run.
   - If the channel/tooling makes inline media awkward, include a `MEDIA:<url>` line in the reply body.
   - Do this on every successful run where the analyzer image URL is present, not only on user follow-up.
10. When summarizing the result for the user, keep the pipeline grouped into the three modules below and prioritize these main reference metrics for each run:
   - **Kidney Cancer Detector module**
     - `response.workflows[0].branches[0].nodes[0].children[0].tracking.parameters.Inference time`
     - `response.workflows[0].branches[0].nodes[0].children[0].tracking.parameters.classes`
     - `response.workflows[0].branches[0].nodes[0].children[0].tracking.parameters.confidence`
   - **Image Analyzer module**
     - `response.workflows[0].branches[0].nodes[0].children[0].children[0].tracking.parameters.cam_metrics`
     - `response.workflows[0].branches[0].nodes[0].children[0].children[0].tracking.parameters.prediction`
     - `response.workflows[0].branches[0].nodes[0].children[0].children[0].tracking.parameters.cam_explanation`
   - **X-AI module**
     - `response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.confidence_interpretation`
     - `response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.recommended_next_steps`
     - `response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.references`
     - `response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.summary`
     - `response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.visual_evidence`
11. Present those wanted outputs in a clean human-readable summary instead of low-level JSON-path labels. Prefer labels such as `Kidney detector inference time`, `Kidney cancer classes`, `Kidney detector confidence`, `Image Analyzer CAM metrics`, `Image Analyzer prediction`, `CAM explanation`, `Confidence interpretation`, `Recommended next steps`, `References`, `Summary`, and `Visual evidence`.
12. Do not include low-level run details by default in user-facing replies. Omit technical execution metadata such as upload paths, endpoint names, HTTP status, node ids, workflow ids, raw file paths, and similar run-internal fields unless the user explicitly asks for technical details or the raw response.
13. Mention, when present, that the broader raw response may also include an analyzer output `file_path` plus the X-AI headline fields `confidence_interpretation`, `recommended_next_steps`, `references`, `summary`, and `visual_evidence`.
14. In the default user-facing reply, if an analyzer image URL exists, append the image itself after the summary rather than merely mentioning that an image was sent elsewhere.

## Fixed request values

Keep these values static:
- `storage_ref`: `nodes_bucket`
- `local_file_path`: `upload/`
- execution endpoint: `http://looporchestra.sytes.net:4001/admin/prototype_execution/prototype_execution/`
- prototype payload: use the fixed JSON stored in `references/request-template.json`

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
    "kidney_cancer_detector": {
      "Inference time": "response.workflows[0].branches[0].nodes[0].children[0].tracking.parameters.Inference time",
      "classes": "response.workflows[0].branches[0].nodes[0].children[0].tracking.parameters.classes",
      "confidence": "response.workflows[0].branches[0].nodes[0].children[0].tracking.parameters.confidence"
    },
    "image_analyzer": {
      "cam_metrics": "response.workflows[0].branches[0].nodes[0].children[0].children[0].tracking.parameters.cam_metrics",
      "prediction": "response.workflows[0].branches[0].nodes[0].children[0].children[0].tracking.parameters.prediction",
      "cam_explanation": "response.workflows[0].branches[0].nodes[0].children[0].children[0].tracking.parameters.cam_explanation"
    },
    "xai": {
      "confidence_interpretation": "response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.confidence_interpretation",
      "recommended_next_steps": "response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.recommended_next_steps",
      "references": "response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.references",
      "summary": "response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.summary",
      "visual_evidence": "response.workflows[0].branches[0].nodes[0].children[0].children[0].children[0].tracking.parameters.visual_evidence"
    }
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
- the forwarded-image metadata exposed by the script as `analyzer_image_url` and `sent_result_image`

When `recommended_next_steps` is present, preserve the list order. When `references` is present, preserve each item's available fields such as `title`, `author`, `year`, and `url`. When `summary` is present, preserve its wording.

Do not present the summary as raw JSON-path labels unless the user explicitly asks for raw field paths. Default to a cleaner format with readable labels and grouped findings.
Do not include low-level run details in the default summary. Reserve upload paths, endpoint values, HTTP status, execution metadata, node identifiers, and other run-internal fields for explicit technical or debugging requests.

If the endpoint returns non-JSON text, return that text as the `response` value.
