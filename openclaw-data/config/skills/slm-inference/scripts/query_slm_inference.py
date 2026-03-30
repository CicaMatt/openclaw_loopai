#!/usr/bin/env python3
import argparse
import json
import sys
from urllib import error, request

ENDPOINT = "http://looporchestra.sytes.net:8007/chat"


def extract_answer(body: str) -> str:
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return body.strip()

    if isinstance(parsed, str):
        return parsed.strip()

    if not isinstance(parsed, dict):
        return json.dumps(parsed, indent=2)

    for key in ("answer", "Answer", "response", "message"):
        value = parsed.get(key)
        if value is not None:
            if isinstance(value, str):
                text = value.strip()
                try:
                    nested = json.loads(text)
                    if isinstance(nested, dict):
                        for nested_key in ("answer", "Answer", "response", "message"):
                            nested_value = nested.get(nested_key)
                            if nested_value is not None:
                                return str(nested_value).strip()
                except json.JSONDecodeError:
                    pass
                return text
            return json.dumps(value, indent=2)

    data = parsed.get("data")
    if isinstance(data, dict):
        for key in ("answer", "Answer", "response", "message"):
            value = data.get(key)
            if value is not None:
                return value if isinstance(value, str) else json.dumps(value, indent=2)

    return json.dumps(parsed, indent=2)


def call_endpoint(question: str, timeout: int = 45) -> str:
    payload = json.dumps({"question": question}).encode("utf-8")

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

    return extract_answer(body)


def main():
    parser = argparse.ArgumentParser(
        description="Query the SLM inference endpoint and print the returned answer"
    )
    parser.add_argument("question", help="Question about patient health data stored in records")
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()

    answer = call_endpoint(args.question, timeout=args.timeout)
    print(answer)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
