#!/usr/bin/env python3
import argparse
import json
import sys
from math import isfinite
from urllib import request, error

ENDPOINT = "http://looporchestra.sytes.net:4010/nodes/ai_tool/kidney-cancer-detection-model"
FIXED_IMAGE_PATH = "626130f7c71f6b9e651c76be/69a2020385d6df1b7ccc15ff/kidney_test2.jpeg"
FIXED_STORAGE_REF = "nodes_bucket"
FIXED_REQUEST_PAYLOAD = {
    "metadata": {
        "name": "kidney_cancer_detection_model",
        "tags": {"user": "Test_POC"},
        "start": False,
        "workflow_name": "KidneyCancer_detection",
        "workflow_type": "NodeType : ai-tool",
        "workflow_id": "25",
        "workflow_run_id": "b1a313fa376d4bbda379aba0aae18124",
        "run_id": "b1a313fa376d4bbda379aba0aae18124",
    },
    "data": {
        "age": "",
        "localization": "",
        "dx_type": "",
        "sex": "",
        "image_path": FIXED_IMAGE_PATH,
        "prototype_id": "69a2020385d6df1b7ccc15ff",
        "node_id": "6986172e677ea52be211de08",
        "storage_ref": FIXED_STORAGE_REF,
        "model_ref": "kidney_cancer",
    },
}


def _is_valid_prediction(prediction_label, confidence) -> bool:
    return (
        isinstance(prediction_label, str)
        and isinstance(confidence, (int, float))
        and isfinite(float(confidence))
    )


def extract_prediction(value):
    if not isinstance(value, dict):
        raise RuntimeError("Endpoint returned a non-object JSON response.")

    # Support the original flat response shape.
    prediction_label = value.get("prediction_label")
    confidence = value.get("confidence")
    if _is_valid_prediction(prediction_label, confidence):
        return {
            "prediction_label": prediction_label,
            "confidence": confidence,
        }

    # Support the nested response shape currently returned by the endpoint.
    perception = (
        value.get("data", {})
        .get("tracking_data", {})
        .get("perception", [])
    )
    if isinstance(perception, list) and perception:
        first = perception[0]
        if isinstance(first, dict):
            prediction_label = first.get("prediction_label") or first.get("prediction")
            confidence = first.get("confidence")
            if _is_valid_prediction(prediction_label, confidence):
                return {
                    "prediction_label": prediction_label,
                    "confidence": confidence,
                }

    raise RuntimeError(
        "Endpoint JSON is missing prediction data in both flat and nested formats"
    )


def call_endpoint_from_image_path(image_path: str, timeout: int = 45):
    if not image_path or not isinstance(image_path, str):
        raise RuntimeError("Missing required image path.")

    request_payload = {
        "metadata": dict(FIXED_REQUEST_PAYLOAD["metadata"]),
        "data": dict(FIXED_REQUEST_PAYLOAD["data"]),
    }
    request_payload["data"]["image_path"] = image_path
    request_payload["data"]["storage_ref"] = FIXED_STORAGE_REF

    payload = json.dumps(request_payload).encode("utf-8")
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

    return extract_prediction(parsed)


def main():
    parser = argparse.ArgumentParser(
        description="Send the fixed kidney cancer detection request payload to the endpoint and print the returned JSON"
    )
    parser.add_argument(
        "image_path",
        nargs="?",
        help="Ignored. The tool always uses the fixed configured image path.",
    )
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()

    result = call_endpoint_from_image_path(FIXED_IMAGE_PATH, timeout=args.timeout)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)