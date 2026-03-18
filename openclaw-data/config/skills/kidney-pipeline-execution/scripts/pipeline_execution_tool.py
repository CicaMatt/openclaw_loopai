#!/usr/bin/env python3
import argparse
import copy
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
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
DOWNLOADED_IMAGES_DIR = Path("/home/node/openclaw-shared/kidney_heatmaps")
TEMP_SEND_DIR = Path("/home/node/.openclaw/workspace/.kidney-pipeline/tmp-send")


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


def download_analyzer_image(image_url: str, timeout: int = 60):
    DOWNLOADED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    suffix = _safe_suffix_from_url(image_url)
    filename = f"analyzer-image-{uuid.uuid4().hex}{suffix}"
    out_path = DOWNLOADED_IMAGES_DIR / filename
    req = request.Request(image_url, headers={"Accept": "image/*"}, method="GET")

    try:
        with request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            content_type = resp.headers.get("Content-Type", "")
    except error.HTTPError as exc:
        raise RuntimeError(f"Analyzer image download failed with HTTP {exc.code}: {image_url}") from exc
    except Exception as exc:
        raise RuntimeError(f"Analyzer image download failed: {exc}") from exc

    out_path.write_bytes(content)
    return {
        "analyzer_image_url": image_url,
        "analyzer_image_local_path": str(out_path),
        "analyzer_image_content_type": content_type,
    }


def send_image_to_telegram(image_path: str, telegram_target: str, timeout: int = 60):
    TEMP_SEND_DIR.mkdir(parents=True, exist_ok=True)
    source_path = Path(image_path)
    suffix = source_path.suffix or ".jpg"
    temp_path_obj = None

    try:
        with tempfile.NamedTemporaryFile(
            dir=str(TEMP_SEND_DIR),
            prefix="telegram-send-",
            suffix=suffix,
            delete=False,
        ) as temp_file:
            temp_path_obj = Path(temp_file.name)

        shutil.copy2(source_path, temp_path_obj)

        command = [
            "openclaw",
            "message",
            "send",
            "--channel",
            "telegram",
            "--target",
            telegram_target,
            "--media",
            str(temp_path_obj),
        ]

        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        detail = stderr or stdout or str(exc)
        raise RuntimeError(f"Telegram image send failed: {detail}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Telegram image send timed out.") from exc
    except Exception as exc:
        raise RuntimeError(f"Telegram image send failed: {exc}") from exc
    finally:
        if temp_path_obj and temp_path_obj.exists():
            temp_path_obj.unlink(missing_ok=True)

    return {
        "telegram_image_target": telegram_target,
        "telegram_image_send_stdout": (completed.stdout or "").strip(),
        "telegram_image_temp_deleted": True,
    }


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


def _replace_image_placeholder(obj, uploaded_image_path: str):
    if isinstance(obj, dict):
        return {key: _replace_image_placeholder(value, uploaded_image_path) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_replace_image_placeholder(item, uploaded_image_path) for item in obj]
    if obj == "<image_path_here>":
        return uploaded_image_path
    return obj


def build_payload(uploaded_image_path: str):
    return _replace_image_placeholder(copy.deepcopy(load_request_template()), uploaded_image_path)


def call_pipeline_execution(uploaded_image_path: str, timeout: int = 120, telegram_target: str | None = None):
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

    image_url = _extract_image_url_from_response(result)
    if image_url:
        download_result = download_analyzer_image(image_url)
        result.update(download_result)
        result.update(
            send_image_to_telegram(
                image_path=download_result["analyzer_image_local_path"],
                telegram_target=telegram_target,
            )
        )

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
            "the <image_path_here> placeholder inside the fixed prototype payload, then "
            "call the prototype execution endpoint and print the raw response as JSON."
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
    parser.add_argument(
        "--telegram-target",
        default=os.environ.get("TELEGRAM_TARGET"),
        help=(
            "Telegram chat target used by `openclaw message send` for the downloaded CAM image. "
            "Defaults to the Telegram user/chat id from --telegram-user-id."
        ),
    )
    args = parser.parse_args()

    if not args.telegram_user_id:
        raise RuntimeError(
            "Missing Telegram user id. Pass --telegram-user-id or set TELEGRAM_USER_ID."
        )

    local_image_path = args.image_path or find_latest_inbound_image()
    telegram_user_id = str(args.telegram_user_id)
    telegram_target = args.telegram_target or telegram_user_id

    uploaded_image_path = upload_image(
        local_image_path=local_image_path,
        telegram_user_id=telegram_user_id,
        timeout=args.upload_timeout,
    )
    result = call_pipeline_execution(
        uploaded_image_path,
        timeout=args.timeout,
        telegram_target=telegram_target,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
