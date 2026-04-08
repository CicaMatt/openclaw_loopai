#!/usr/bin/env python3
import argparse
import json
import sys
import urllib.request
import urllib.error

ENDPOINT = "http://looporchestra.sytes.net:8008/query"
ALLOWED_DOMAINS = {"nephrology", "cardiology", "hypertension"}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Query the specialty SLM with a question, required domains, and optional patient context."
    )
    parser.add_argument("--question", required=True, help="Focused question to ask the SLM")
    parser.add_argument(
        "--domain",
        action="append",
        dest="domains",
        required=True,
        help="Domain to include. Repeat for multiple domains: nephrology, cardiology, hypertension",
    )
    parser.add_argument(
        "--patient-context",
        help="Optional JSON object string for patient_context",
    )
    parser.add_argument(
        "--patient-context-file",
        help="Optional path to a JSON file containing patient_context",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="HTTP timeout in seconds (default: 60)",
    )
    return parser.parse_args()


def load_patient_context(args):
    return {"additionalProp1": {}}


def normalize_domains(domains):
    normalized = []
    seen = set()
    for domain in domains or []:
        value = domain.strip().lower()
        if not value:
            continue
        if value not in ALLOWED_DOMAINS:
            allowed = ", ".join(sorted(ALLOWED_DOMAINS))
            raise SystemExit(f"Invalid domain '{domain}'. Allowed values: {allowed}")
        if value not in seen:
            normalized.append(value)
            seen.add(value)
    if not normalized:
        raise SystemExit("At least one valid --domain is required.")
    return normalized


def main():
    args = parse_args()
    patient_context = load_patient_context(args)
    domains = normalize_domains(args.domains)

    payload = {
        "question": args.question,
        "domains": domains,
        "patient_context": patient_context,
    }

    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            content_type = response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        print(error_body or str(exc), file=sys.stderr)
        raise SystemExit(exc.code)
    except urllib.error.URLError as exc:
        raise SystemExit(f"Request failed: {exc}")

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        if "json" in content_type.lower():
            raise SystemExit("Endpoint returned invalid JSON.")
        print(raw)
        return

    print(json.dumps(parsed, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
