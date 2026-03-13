---
name: kidney-cancer-detection
description: Use this skill when the user wants to analyze a kidney medical image for possible kidney cancer detection, classify the result, or route an image to a kidney cancer prediction endpoint using a local or remote inference service.
metadata:
  openclaw:
    tags:
      - medical-imaging
      - kidney
      - oncology
      - classification
---

# Kidney Cancer Detection

This skill helps analyze a kidney medical image by:
- always using the fixed configured image path `626130f7c71f6b9e651c76be/69a2020385d6df1b7ccc15ff/kidney_test2.jpeg`
- always sending the fixed `storage_ref` value `nodes_bucket`
- sending the exact nested request payload expected by the kidney cancer detection endpoint
- avoiding any local file read or base64 conversion step
- validating the returned JSON
- presenting the prediction label and confidence clearly

## When to use this skill

Use this skill when the user:
- wants to run kidney cancer detection on a medical image
- provides a chest scan image path for analysis
- asks to call a kidney cancer inference endpoint
- wants a wrapper script for kidney cancer prediction
- needs structured output containing a label and confidence score

Do not use this skill when:
- the user only wants general educational information about kidney cancer
- the user asks for a diagnosis without any model or image-processing workflow
- the request is unrelated to medical image inference

Keep in mind that the image you have to analyze must be selected by spotting the user loaded image from the "./config/media/inbound" folder.

## Expected input

The workflow ignores any supplied image path or image payload and always sends these fixed request values:
- `image_path`: `626130f7c71f6b9e651c76be/69a2020385d6df1b7ccc15ff/kidney_test2.jpeg`
- `storage_ref`: `nodes_bucket`

## What this skill runs

```bash
python3 kidney_cancer_tool.py
```

The script sends a JSON request shaped like:

```json
{
  "metadata": {
    "name": "kidney_cancer_detection_model",
    "tags": {
      "user": "Test_POC"
    },
    "start": false,
    "workflow_name": "KidneyCancer_detection",
    "workflow_type": "NodeType : ai-tool",
    "workflow_id": "25",
    "workflow_run_id": "b1a313fa376d4bbda379aba0aae18124",
    "run_id": "b1a313fa376d4bbda379aba0aae18124"
  },
  "data": {
    "age": "",
    "localization": "",
    "dx_type": "",
    "sex": "",
    "image_path": "626130f7c71f6b9e651c76be/69a2020385d6df1b7ccc15ff/kidney_test2.jpeg",
    "prototype_id": "69a2020385d6df1b7ccc15ff",
    "node_id": "6986172e677ea52be211de08",
    "storage_ref": "nodes_bucket",
    "model_ref": "kidney_cancer"
  }
}
```

## Expected output

Return validated JSON with this shape:

```json
{
  "prediction_label": "string",
  "confidence": 0.98
}