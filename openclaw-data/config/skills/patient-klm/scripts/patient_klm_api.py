#!/usr/bin/env python3
import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "http://looporchestra.sytes.net:8006"
DEFAULT_PATIENT_ID = "P-001"


def load_json_arg(inline_json: str | None, file_path: str | None):
    if inline_json and file_path:
        raise SystemExit("Provide either --json or --file, not both.")
    if inline_json:
        return json.loads(inline_json)
    if file_path:
        return json.loads(Path(file_path).read_text())
    raise SystemExit("A JSON payload is required. Use --json or --file.")


def request_json(method: str, path: str, payload=None):
    url = f"{BASE_URL}{path}"
    headers = {"Accept": "application/json"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return resp.status, json.loads(body)
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, {"raw": body}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"raw": body}
        return e.code, {"error": True, "body": parsed}


def print_json(data):
    json.dump(data, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Patient KLM API helper")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("get-patient", "get-timeline", "get-genomics"):
        p = sub.add_parser(name)
        p.add_argument("--patient-id", default=DEFAULT_PATIENT_ID)

    p = sub.add_parser("add-patient")
    p.add_argument("--json")
    p.add_argument("--file")

    p = sub.add_parser("add-visit")
    p.add_argument("--patient-id", default=DEFAULT_PATIENT_ID)
    p.add_argument("--json")
    p.add_argument("--file")

    p = sub.add_parser("add-triple")
    p.add_argument("--json")
    p.add_argument("--file")

    args = parser.parse_args()

    if args.command == "get-patient":
        status, data = request_json("GET", f"/patient/{args.patient_id}")
    elif args.command == "get-timeline":
        status, data = request_json("GET", f"/patient/{args.patient_id}/timeline")
    elif args.command == "get-genomics":
        status, data = request_json("GET", f"/patient/{args.patient_id}/genomics")
    elif args.command == "add-patient":
        payload = load_json_arg(args.json, args.file)
        status, data = request_json("POST", "/patient", payload)
    elif args.command == "add-visit":
        payload = load_json_arg(args.json, args.file)
        status, data = request_json("POST", f"/patient/{args.patient_id}/visit", payload)
    elif args.command == "add-triple":
        payload = load_json_arg(args.json, args.file)
        status, data = request_json("POST", "/triple", payload)
    else:
        raise SystemExit(f"Unsupported command: {args.command}")

    result = {"status": status, "result": data}
    print_json(result)
    if status >= 400:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
