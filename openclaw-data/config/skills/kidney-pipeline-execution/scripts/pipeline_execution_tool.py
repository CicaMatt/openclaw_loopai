#!/usr/bin/env python3
import argparse
import copy
import json
import mimetypes
import os
import re
import sys
import time
import uuid
from pathlib import Path
from urllib import error, parse, request

EXECUTION_ENDPOINT = (
    "http://looporchestra.sytes.net:4001/admin/prototype_execution/prototype_execution/"
)
UPLOAD_BASE_URL = "http://looporchestra.sytes.net:4001/nodes/input/upload"
FIXED_STORAGE_REF = "nodes_bucket"
UPLOAD_RETRIES = 3
UPLOAD_RETRY_SLEEP_SECONDS = 1.5
FIXED_LOCAL_FILE_PATH = "upload"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff"}

REQUEST_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "references" / "request-template.json"
INBOUND_MEDIA_DIR = Path("/home/node/.openclaw/media/inbound").resolve()
ARTIFACTS_DIR = Path("/home/node/.openclaw/workspace/kidney-pipeline-artifacts").resolve()


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


def _normalize_upload_response(value):
    if isinstance(value, list):
        if not value:
            raise RuntimeError("Upload response was an empty list.")
        value = value[0]
    if not isinstance(value, dict):
        raise RuntimeError("Upload endpoint returned an unsupported JSON shape.")
    if value == {"Error": {}}:
        raise RuntimeError("Upload response returned an empty error payload.")
    return value


def _guess_mime_type(file_path: Path) -> str:
    guessed, _ = mimetypes.guess_type(str(file_path))
    return guessed or "application/octet-stream"


def _multipart_encode(field_name: str, file_path: Path):
    mime_type = _guess_mime_type(file_path)
    boundary = f"----OpenClawBoundary{uuid.uuid4().hex}"
    file_bytes = file_path.read_bytes()
    body = b"".join(
        [
            f"--{boundary}\r\n".encode("utf-8"),
            (
                f'Content-Disposition: form-data; name="{field_name}"; filename="{file_path.name}"\r\n'
            ).encode("utf-8"),
            f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"),
            file_bytes,
            b"\r\n",
            f"--{boundary}--\r\n".encode("utf-8"),
        ]
    )
    return boundary, body


def _ensure_artifacts_dir() -> Path:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    return ARTIFACTS_DIR


def upload_image(local_image_path: str, telegram_user_id: str, timeout: int = 60):
    file_path = Path(local_image_path).expanduser().resolve()
    if not file_path.is_file():
        raise RuntimeError(f"Image file not found: {file_path}")

    artifacts_dir = _ensure_artifacts_dir()
    attempts_path = artifacts_dir / "upload-attempts.json"
    upload_request_path = artifacts_dir / "upload-request.json"
    upload_response_path = artifacts_dir / "upload-response.json"

    attempts = []
    last_error = None

    for retry_index in range(1, UPLOAD_RETRIES + 1):
        query = parse.urlencode(
            {
                "storage_ref": FIXED_STORAGE_REF,
                "local_file_path": FIXED_LOCAL_FILE_PATH,
                "user_id": telegram_user_id,
            }
        )
        upload_url = f"{UPLOAD_BASE_URL}?{query}"
        boundary, body = _multipart_encode("file", file_path)
        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        }

        request_record = {
            "attempt": retry_index,
            "retry_index": retry_index,
            "storage_ref": FIXED_STORAGE_REF,
            "method": "POST",
            "url": UPLOAD_BASE_URL,
            "query_url": upload_url,
            "params": {
                "storage_ref": FIXED_STORAGE_REF,
                "local_file_path": FIXED_LOCAL_FILE_PATH,
                "user_id": telegram_user_id,
            },
            "headers": headers,
            "multipart_field": {
                "name": "file",
                "filename": file_path.name,
                "content_type": _guess_mime_type(file_path),
                "local_path": str(file_path),
                "size_bytes": file_path.stat().st_size,
            },
        }

        req = request.Request(
            upload_url,
            data=body,
            headers=headers,
            method="POST",
        )

        response_body = None
        status = None
        response_headers = {}
        transport_error = None
        parsed = None

        try:
            with request.urlopen(req, timeout=timeout) as resp:
                response_body = resp.read().decode("utf-8", errors="replace")
                status = resp.status
                response_headers = dict(resp.headers.items())
        except error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            status = e.code
            response_headers = dict(e.headers.items()) if e.headers else {}
            transport_error = f"Upload failed with HTTP {e.code}: {detail}"
            response_body = detail
        except Exception as e:
            transport_error = f"Upload request failed: {e}"

        if response_body is not None:
            try:
                parsed = json.loads(response_body)
            except json.JSONDecodeError:
                parsed = None

        attempt_record = {
            "request": request_record,
            "response": {
                "status_code": status,
                "headers": response_headers,
                "body": parsed if parsed is not None else None,
                "body_text": response_body if parsed is None else None,
            },
            "success": False,
            "error": transport_error,
        }

        if parsed is not None:
            try:
                parsed = _normalize_upload_response(parsed)
                remote_dir = parsed.get("path")
                filename = parsed.get("filename")
                if not isinstance(remote_dir, str) or not remote_dir:
                    raise RuntimeError("Upload response is missing 'path'.")
                if not isinstance(filename, str) or not filename:
                    raise RuntimeError("Upload response is missing 'filename'.")

                uploaded_image_path = f"{remote_dir}{filename}"
                attempt_record["success"] = True
                attempts.append(attempt_record)
                attempts_path.write_text(json.dumps(attempts, indent=2, ensure_ascii=False), encoding="utf-8")
                upload_request_path.write_text(json.dumps(request_record, indent=2, ensure_ascii=False), encoding="utf-8")
                upload_response_path.write_text(
                    json.dumps(attempt_record["response"], indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                return {
                    "uploaded_image_path": uploaded_image_path,
                    "upload_storage_ref_used": FIXED_STORAGE_REF,
                    "upload_attempts_artifact": str(attempts_path),
                    "upload_request_artifact": str(upload_request_path),
                    "upload_response_artifact": str(upload_response_path),
                    "upload_response_json": parsed,
                }
            except RuntimeError as e:
                if not attempt_record["error"]:
                    attempt_record["error"] = str(e)

        if not attempt_record["error"]:
            if parsed is None and response_body is not None:
                attempt_record["error"] = "Upload endpoint returned a non-JSON response."
            else:
                attempt_record["error"] = "Upload failed without a readable response body."

        attempts.append(attempt_record)
        attempts_path.write_text(json.dumps(attempts, indent=2, ensure_ascii=False), encoding="utf-8")
        last_error = attempt_record["error"]
        if retry_index < UPLOAD_RETRIES:
            time.sleep(UPLOAD_RETRY_SLEEP_SECONDS)

    raise RuntimeError(last_error or "Upload failed for nodes_bucket.")


def _resolve_input_image_path(image_path: str | None) -> Path:
    if image_path:
        file_path = Path(image_path).expanduser().resolve()
        if not file_path.is_file():
            raise RuntimeError(f"Image file not found: {file_path}")
        return file_path

    if not INBOUND_MEDIA_DIR.is_dir():
        raise RuntimeError(
            "Inbound media directory not found: /home/node/.openclaw/media/inbound. "
            "Pass an image path explicitly if the image is stored elsewhere."
        )

    candidates = [
        path
        for path in INBOUND_MEDIA_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    if not candidates:
        raise RuntimeError(
            "No supported image files found in /home/node/.openclaw/media/inbound. "
            "Pass an image path explicitly if needed."
        )

    return max(candidates, key=lambda p: p.stat().st_mtime).resolve()



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
    if isinstance(obj, str) and (
        obj == "<image_path_here>"
        or (parent_key in PATH_FIELD_KEYS and obj.strip().lstrip("/").startswith("upload/"))
    ):
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


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Upload a local image with the kidney cancer skill's multipart POST flow, "
            "replace the <image_path_here> placeholder inside the fixed prototype payload, call the "
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

    input_image_path = _resolve_input_image_path(args.image_path)
    telegram_user_id = str(args.telegram_user_id)

    upload_result = upload_image(
        local_image_path=str(input_image_path),
        telegram_user_id=telegram_user_id,
        timeout=args.upload_timeout,
    )
    uploaded_image_path = upload_result["uploaded_image_path"]
    result = call_pipeline_execution(
        uploaded_image_path,
        timeout=args.timeout,
    )
    result["local_image_path_used"] = str(input_image_path)
    result["upload_storage_ref_used"] = upload_result["upload_storage_ref_used"]
    result["upload_attempts_artifact"] = upload_result["upload_attempts_artifact"]
    result["upload_request_artifact"] = upload_result["upload_request_artifact"]
    result["upload_response_artifact"] = upload_result["upload_response_artifact"]
    result["upload_response_json"] = upload_result["upload_response_json"]
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
