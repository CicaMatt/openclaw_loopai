---
name: kidney-cancer-detection
description: Use this skill when the user wants to analyze a kidney medical image for possible kidney cancer detection, classify the result, or route a kidney image through the upload API and then into the kidney cancer prediction endpoint using the returned remote image path.
---

# Kidney Cancer Detection

Upload the local image first, then run inference with the uploaded remote path.

## Workflow

1. Determine the local image to analyze.
   - Prefer an explicit local file path when one is available.
   - If no path is provided, use the most recent supported image under `./config/media/inbound`.
2. Require the Telegram user id.
   - Pass it as `--telegram-user-id` or set `TELEGRAM_USER_ID`.
   - Use that value as the upload request's `user_id` query parameter.
3. Upload the image with a `POST multipart/form-data` request to:
   - `http://looporchestra.sytes.net:4001/nodes/input/upload?storage_ref=nodes_bucket&local_file_path=upload%2F&user_id=<telegram-user-id>`
4. Read the upload response JSON and build the new remote `image_path` by concatenating:
   - `path + filename`
5. Call the kidney cancer inference endpoint using that uploaded `image_path`.

## Fixed request values

Keep these values static:
- `storage_ref`: `nodes_bucket`
- `local_file_path`: `upload/`
- inference endpoint `data.storage_ref`: `nodes_bucket`

## What this skill runs

```bash
python3 scripts/kidney_cancer_tool.py --telegram-user-id <telegram-user-id> [local-image-path]
```

If `local-image-path` is omitted, the script automatically selects the newest supported image from `./config/media/inbound`.

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

Use that full value as the inference request's `data.image_path`.

## Expected output

Return validated JSON with this shape:

```json
{
  "uploaded_image_path": "string",
  "prediction_label": "string",
  "confidence": 0.98
}
```
