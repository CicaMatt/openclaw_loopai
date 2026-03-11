#!/usr/bin/env python3
import argparse
import json
import sys
from urllib import request, error

ENDPOINT = "http://looporchestra.sytes.net:8001/nodes/ai_tool/AutoGen-model"


def call_endpoint(prompt: str, timeout: int = 45):
    payload = json.dumps({"prompt": prompt}).encode("utf-8")
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

    # Expected: JSON with an "Answer" string.
    # Fallback: attempt common key casing or return raw string body.
    try:
        parsed = json.loads(body)
        if isinstance(parsed, dict):
            for key in ("Answer", "answer", "ANSWER"):
                if key in parsed:
                    return str(parsed[key])
            return json.dumps(parsed, indent=2)
    except json.JSONDecodeError:
        pass

    return body.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Call AutoGen pipeline endpoint with a prompt and print the returned Answer"
    )
    parser.add_argument("prompt", help="Prompt describing the ML pipeline prototype request")
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()

    answer = call_endpoint(args.prompt, timeout=args.timeout)
    print(answer)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
