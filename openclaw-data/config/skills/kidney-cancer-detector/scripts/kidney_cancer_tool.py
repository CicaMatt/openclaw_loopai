#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import sys
import uuid
from math import isfinite
from pathlib import Path
from urllib import error, parse, request

ENDPOINT = "http://looporchestra.sytes.net:4010/nodes/ai_tool/kidney-cancer-detection-model"
UPLOAD_BASE_URL = "http://looporchestra.sytes.net:4001/nodes/input/upload"
FIXED_STORAGE_REF = "nodes_bucket"
FIXED_LOCAL_FILE_PATH = "upload/"
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
        "image_path": "",
        "prototype_id": "69a2020385d6df1b7ccc15ff",
        "node_id": "6986172e677ea52be211de08",
        "storage_ref": FIXED_STORAGE_REF,
        "model_ref": "kidney_cancer",
    },
}
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def _is_valid_prediction(prediction_label, confidence) -> bool:
    return (
        isinstance(prediction_label, str)
        and isinstance(confidence, (int, float))
        and isfinite(float(confidence))
    )


def extract_prediction(value):
    if not isinstance(value, dict):
        raise RuntimeError("Endpoint returned a non-object JSON response.")

    prediction_label = value.get("prediction_label")
    confidence = value.get("confidence")
    if _is_valid_prediction(prediction_label, confidence):
        return {
            "prediction_label": prediction_label,
            "confidence": confidence,
        }

    perception = value.get("data", {}).get("tracking_data", {}).get("perception", [])
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


def _multipart_encode(field_name: str, file_path: Path):
    boundary = f"----OpenClawBoundary{uuid.uuid4().hex}"
    mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    file_bytes = file_path.read_bytes()

    parts = [
        f"--{boundary}\r\n".encode("utf-8"),
        (
            f'Content-Disposition: form-data; name="{field_name}"; '
            f'filename="{file_path.name}"\r\n'
        ).encode("utf-8"),
        f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"),
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8"),
    ]
    return boundary, b"".join(parts)


def _normalize_upload_response(value):
    if isinstance(value, list):
        if not value:
            raise RuntimeError("Upload response was an empty list.")
        first = value[0]
        if not isinstance(first, dict):
            raise RuntimeError("Upload response list did not contain an object.")
        value = first

    if not isinstance(value, dict):
        raise RuntimeError("Upload endpoint returned an unsupported JSON shape.")

    return value


def upload_image(local_image_path: str, telegram_user_id: str, timeout: int = 60) -> str:
    file_path = Path(local_image_path).expanduser().resolve()
    if not file_path.is_file():
        raise RuntimeError(f"Image file not found: {file_path}")

    query = parse.urlencode(
        {
            "storage_ref": FIXED_STORAGE_REF,
            "local_file_path": FIXED_LOCAL_FILE_PATH,
            "user_id": telegram_user_id,
        }
    )
    upload_url = f"{UPLOAD_BASE_URL}?{query}"
    boundary, body = _multipart_encode("file", file_path)
    req = request.Request(
        upload_url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout) as resp:
            response_body = resp.read().decode("utf-8", errors="replace")
    except error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Upload failed with HTTP {e.code}: {detail}") from e
    except Exception as e:
        raise RuntimeError(f"Upload request failed: {e}") from e

    try:
        parsed = json.loads(response_body)
    except json.JSONDecodeError as e:
        raise RuntimeError("Upload endpoint returned a non-JSON response.") from e

    parsed = _normalize_upload_response(parsed)
    remote_dir = parsed.get("path")
    filename = parsed.get("filename")
    if not isinstance(remote_dir, str) or not remote_dir:
        raise RuntimeError("Upload response is missing 'path'.")
    if not isinstance(filename, str) or not filename:
        raise RuntimeError("Upload response is missing 'filename'.")

    return f"{remote_dir}{filename}"


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


def find_latest_inbound_image() -> str:
    inbound_dir = Path("/home/node/.openclaw/media/inbound").resolve()
    if not inbound_dir.is_dir():
        raise RuntimeError(
            "Inbound media directory not found: /home/node/.openclaw/media/inbound. "
            "Pass --image-path explicitly if the image is stored elsewhere."
        )

    candidates = [
        path
        for path in inbound_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    if not candidates:
        raise RuntimeError(
            "No supported image files found in /home/node/.openclaw/media/inbound. "
            "Pass --image-path explicitly if needed."
        )

    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    return str(latest)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Upload a local kidney image, build the remote image_path from the upload "
            "response, then call the kidney cancer detection endpoint and print JSON."
        )
    )
    parser.add_argument(
        "image_path",
        nargs="?",
        help=(
            "Local image path to upload first. If omitted, the tool selects the most "
            "recent supported image from /home/node/.openclaw/media/inbound."
        ),
    )
    parser.add_argument(
        "--telegram-user-id",
        default=os.environ.get("TELEGRAM_USER_ID"),
        help="Telegram user id used as the upload endpoint's user_id query parameter.",
    )
    parser.add_argument("--timeout", type=int, default=45, help="Inference timeout in seconds.")
    parser.add_argument("--upload-timeout", type=int, default=60, help="Upload timeout in seconds.")
    args = parser.parse_args()

    if not args.telegram_user_id:
        raise RuntimeError(
            "Missing Telegram user id. Pass --telegram-user-id or set TELEGRAM_USER_ID."
        )

    local_image_path = args.image_path or find_latest_inbound_image()
    uploaded_image_path = upload_image(
        local_image_path=local_image_path,
        telegram_user_id=str(args.telegram_user_id),
        timeout=args.upload_timeout,
    )
    result = call_endpoint_from_image_path(uploaded_image_path, timeout=args.timeout)
    output = {
        "uploaded_image_path": uploaded_image_path,
        "prediction_label": result["prediction_label"],
        "confidence": result["confidence"],
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
