#!/usr/bin/env python3
import argparse
import copy
import json
import mimetypes
import os
import re
import sys
import uuid
from pathlib import Path
from urllib import error, parse, request

EXECUTION_ENDPOINT = (
    "http://looporchestra.sytes.net:4001/admin/prototype_execution/prototype_execution/"
)
UPLOAD_BASE_URL = "http://looporchestra.sytes.net:4001/nodes/input/upload"
FIXED_STORAGE_REF = "nodes_bucket"
FIXED_LOCAL_FILE_PATH = "upload/"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff"}

REQUEST_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "references" / "request-template.json"


def _safe_suffix_from_url(url: str) -> str:
    parsed = parse.urlparse(url)
    suffix = Path(parsed.path).suffix.lower()
    if suffix in SUPPORTED_EXTENSIONS:
        return suffix
    return ".jpg"


def _extract_image_url_from_response(response_obj):
    try:
        file_path = response_obj["response"]["workflows"][0]["branches"][0]["nodes"][0]["children"][0]["children"][0]["tracking"]["parameters"].get("file_path")
    except (KeyError, IndexError, TypeError):
        return None

    if not isinstance(file_path, str) or not file_path:
        return None

    match = re.search(r"https?://\S+", file_path)
    return match.group(0) if match else None


def _deep_get(obj, path, default=None):
    current = obj
    for key in path:
        try:
            current = current[key]
        except (KeyError, IndexError, TypeError):
            return default
    return current


def _extract_module_reference_metrics(response_payload):
    if not isinstance(response_payload, dict):
        return None

    kidney_detector = {
        "Inference time": _deep_get(
            response_payload,
            ["workflows", 0, "branches", 0, "nodes", 0, "children", 0, "tracking", "parameters", "Inference time"],
        ),
        "classes": _deep_get(
            response_payload,
            ["workflows", 0, "branches", 0, "nodes", 0, "children", 0, "tracking", "parameters", "classes"],
        ),
        "confidence": _deep_get(
            response_payload,
            ["workflows", 0, "branches", 0, "nodes", 0, "children", 0, "tracking", "parameters", "confidence"],
        ),
    }
    image_analyzer = {
        "cam_metrics": _deep_get(
            response_payload,
            ["workflows", 0, "branches", 0, "nodes", 0, "children", 0, "children", 0, "tracking", "parameters", "cam_metrics"],
        ),
        "prediction": _deep_get(
            response_payload,
            ["workflows", 0, "branches", 0, "nodes", 0, "children", 0, "children", 0, "tracking", "parameters", "prediction"],
        ),
        "cam_explanation": _deep_get(
            response_payload,
            ["workflows", 0, "branches", 0, "nodes", 0, "children", 0, "children", 0, "tracking", "parameters", "cam_explanation"],
        ),
    }
    xai = {
        "confidence_interpretation": _deep_get(
            response_payload,
            ["workflows", 0, "branches", 0, "nodes", 0, "children", 0, "children", 0, "children", 0, "tracking", "parameters", "confidence_interpretation"],
        ),
        "recommended_next_steps": _deep_get(
            response_payload,
            ["workflows", 0, "branches", 0, "nodes", 0, "children", 0, "children", 0, "children", 0, "tracking", "parameters", "recommended_next_steps"],
        ),
        "references": _deep_get(
            response_payload,
            ["workflows", 0, "branches", 0, "nodes", 0, "children", 0, "children", 0, "children", 0, "tracking", "parameters", "references"],
        ),
        "summary": _deep_get(
            response_payload,
            ["workflows", 0, "branches", 0, "nodes", 0, "children", 0, "children", 0, "children", 0, "tracking", "parameters", "summary"],
        ),
        "visual_evidence": _deep_get(
            response_payload,
            ["workflows", 0, "branches", 0, "nodes", 0, "children", 0, "children", 0, "children", 0, "tracking", "parameters", "visual_evidence"],
        ),
    }

    modules = {
        "kidney_cancer_detector": kidney_detector,
        "image_analyzer": image_analyzer,
        "xai": xai,
    }
    if not any(value is not None for module in modules.values() for value in module.values()):
        return None
    return modules


def load_request_template():
    try:
        return json.loads(REQUEST_TEMPLATE_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Request template file not found: {REQUEST_TEMPLATE_PATH}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Request template file is not valid JSON: {REQUEST_TEMPLATE_PATH}"
        ) from exc



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
        value = value[0]
    if not isinstance(value, dict):
        raise RuntimeError("Upload endpoint returned an unsupported JSON shape.")
    return value


def upload_image(local_image_path: str, telegram_user_id: str, timeout: int = 60) -> dict:
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

    return {
        "uploaded_image_path": f"{remote_dir}{filename}",
        "upload_path": remote_dir,
        "upload_filename": filename,
        "telegram_user_id_used": str(telegram_user_id),
        "upload_request_url": upload_url,
        "raw_upload_response": parsed,
    }


PATH_FIELD_KEYS = {"filename", "pdf_path", "File Path"}

def _replace_uploaded_image_path(obj, uploaded_image_path: str, parent_key=None):
    if isinstance(obj, dict):
        return {
            key: _replace_uploaded_image_path(value, uploaded_image_path, parent_key=key)
            for key, value in obj.items()
        }
    if isinstance(obj, list):
        return [
            _replace_uploaded_image_path(item, uploaded_image_path, parent_key=parent_key)
            for item in obj
        ]
    if isinstance(obj, str) and (obj == "<image_path_here>"):
        return uploaded_image_path
    return obj



def _assert_no_placeholder_path(payload_obj):
    found = []

    def _walk(value, path="root"):
        if isinstance(value, dict):
            for key, child in value.items():
                _walk(child, f"{path}.{key}")
            return
        if isinstance(value, list):
            for index, child in enumerate(value):
                _walk(child, f"{path}[{index}]")
            return
        if value == "<image_path_here>":
            found.append(path)

    _walk(payload_obj)
    if found:
        joined = ", ".join(found[:10])
        raise RuntimeError(f"Request payload still contains <image_path_here> at: {joined}")



def build_payload(uploaded_image_path: str):
    payload_obj = _replace_uploaded_image_path(copy.deepcopy(load_request_template()), uploaded_image_path)
    _assert_no_placeholder_path(payload_obj)
    return payload_obj


def call_pipeline_execution(uploaded_image_path: str, timeout: int = 120):
    payload_obj = build_payload(uploaded_image_path)
    payload = json.dumps(payload_obj).encode("utf-8")
    req = request.Request(
        EXECUTION_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            status = resp.status
            content_type = resp.headers.get("Content-Type", "")
    except error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Execution failed with HTTP {e.code}: {detail}") from e
    except Exception as e:
        raise RuntimeError(f"Execution request failed: {e}") from e

    parsed_body = None
    try:
        parsed_body = json.loads(body)
    except json.JSONDecodeError:
        parsed_body = body

    result = {
        "uploaded_image_path": uploaded_image_path,
        "endpoint": EXECUTION_ENDPOINT,
        "http_status": status,
        "content_type": content_type,
        "response": parsed_body,
    }

    module_reference_metrics = _extract_module_reference_metrics(parsed_body)
    if module_reference_metrics is not None:
        result["module_reference_metrics"] = module_reference_metrics

    image_url = _extract_image_url_from_response(result)
    result["analyzer_image_url"] = image_url
    result["sent_result_image"] = False
    return result


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
            "Upload a local image with the same flow as the kidney cancer skill, replace "
            "the <image_path_here> placeholder inside the fixed prototype payload, call the "
            "prototype execution endpoint, expose any analyzer image URL in the JSON wrapper, "
            "and print the result without sending out-of-band Telegram messages."
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
    parser.add_argument("--timeout", type=int, default=120, help="Execution timeout in seconds.")
    parser.add_argument("--upload-timeout", type=int, default=60, help="Upload timeout in seconds.")
    args = parser.parse_args()

    if not args.telegram_user_id:
        raise RuntimeError(
            "Missing Telegram user id. Pass --telegram-user-id or set TELEGRAM_USER_ID."
        )

    local_image_path = args.image_path or find_latest_inbound_image()
    telegram_user_id = str(args.telegram_user_id)

    upload_result = upload_image(
        local_image_path=local_image_path,
        telegram_user_id=telegram_user_id,
        timeout=args.upload_timeout,
    )
    result = call_pipeline_execution(
        upload_result["uploaded_image_path"],
        timeout=args.timeout,
    )
    result["local_image_path_used"] = str(Path(local_image_path).expanduser().resolve())
    result["telegram_user_id_used_for_upload"] = upload_result["telegram_user_id_used"]
    result["upload_path"] = upload_result["upload_path"]
    result["upload_filename"] = upload_result["upload_filename"]
    result["upload_request_url"] = upload_result["upload_request_url"]
    result["raw_upload_response"] = upload_result["raw_upload_response"]
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
