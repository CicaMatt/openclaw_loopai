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
- accepting an image path or image payload
- converting the image into base64 when needed
- sending it to a kidney cancer detection endpoint
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

The workflow should accept one of these:
- a path to a local image file
- a base64-encoded image
- a data URL containing a base64-encoded image

Preferred CLI input:
- `image_path`: path to the image file to analyze

## What this skill runs

```bash
python3 kidney_cancer_tool.py /path/to/image.png
```

## Expected output

Return validated JSON with this shape:

```json
{
  "prediction_label": "string",
  "confidence": 0.98
}