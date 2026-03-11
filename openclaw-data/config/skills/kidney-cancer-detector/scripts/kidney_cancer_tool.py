#!/usr/bin/env python3
import argparse
import base64
import json
import os
import re
import sys
from math import isfinite
from urllib import request, error

ENDPOINT = "http://looporchestra.sytes.net:8001/nodes/ai_tool/kidney-cancer-detection-model"


def normalize_base64(input_str: str) -> str:
    match = re.match(r"^data:[^;]+;base64,(.*)$", input_str, re.DOTALL)
    return match.group(1) if match else input_str


def is_valid_response_shape(value) -> bool:
    if not isinstance(value, dict):
        return False

    prediction_label = value.get("prediction_label")
    confidence = value.get("confidence")

    return (
        isinstance(prediction_label, str)
        and isinstance(confidence, (int, float))
        and isfinite(float(confidence))
    )


def image_file_to_base64(image_path: str) -> str:
    if not image_path or not isinstance(image_path, str):
        raise RuntimeError("Missing required image path.")

    if not os.path.isfile(image_path):
        raise RuntimeError(f"Image file not found: {image_path}")

    try:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"Failed to read image file: {e}") from e

    if not encoded:
        raise RuntimeError("Image file was empty after base64 encoding.")

    return encoded


def call_endpoint_from_image_path(image_path: str, timeout: int = 45):
    cleaned_base64 = normalize_base64(image_file_to_base64(image_path).strip())

    if not cleaned_base64:
        raise RuntimeError("The encoded image data is empty after base64 normalization.")

    payload = json.dumps({"data": cleaned_base64}).encode("utf-8")
    req = request.Request(
        ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {detail}") from e
    except Exception as e:
        raise RuntimeError(f"Request failed: {e}") from e

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as e:
        raise RuntimeError("Endpoint returned a non-JSON response.") from e

    if not is_valid_response_shape(parsed):
        raise RuntimeError(
            "Endpoint JSON is missing required fields: prediction_label, confidence"
        )

    return {
        "prediction_label": parsed["prediction_label"],
        "confidence": parsed["confidence"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Read a kidney image file, convert it to base64, send it to the kidney cancer detection endpoint, and print the returned JSON"
    )
    parser.add_argument("image_path", help="Path to the image file to encode and send")
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()

    result = call_endpoint_from_image_path(args.image_path, timeout=args.timeout)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)