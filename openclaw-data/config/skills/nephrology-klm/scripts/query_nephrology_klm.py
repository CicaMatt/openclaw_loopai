#!/usr/bin/env python3
import argparse
import json
import sys
from urllib import error, request

ENDPOINT = "http://looporchestra.sytes.net:8001/nodes/ai_tool/Nephrology-KLM-model"


def extract_answer(body: str) -> str:
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return body.strip()

    if not isinstance(parsed, dict):
        return json.dumps(parsed, indent=2)

    data = parsed.get("data")
    if isinstance(data, dict):
        answer = data.get("Answer") or data.get("answer") or data.get("ANSWER")
        if answer is not None:
            if isinstance(answer, str):
                text = answer.strip()
                try:
                    nested = json.loads(text)
                    if isinstance(nested, dict) and "answer" in nested:
                        return str(nested["answer"])
                except json.JSONDecodeError:
                    pass
                return text
            return json.dumps(answer, indent=2)

    for key in ("Answer", "answer", "ANSWER"):
        if key in parsed:
            value = parsed[key]
            return value if isinstance(value, str) else json.dumps(value, indent=2)

    return json.dumps(parsed, indent=2)


def call_endpoint(prompt: str, timeout: int = 45) -> str:
    payload = json.dumps({
        "metadata": {
            "name": "nephrology-klm",
            "workflow_name": "nephrology-klm",
            "workflow_type": "experiment",
            "workflow_id": "nephrology-klm",
            "workflow_run_id": "manual",
            "run_id": "manual",
        },
        "data": {"prompt": prompt},
    }).encode("utf-8")
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
        description="Query the Nephrology-KLM endpoint and print the returned answer"
    )
    parser.add_argument("prompt", help="Nephrology prompt to send to the model")
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
