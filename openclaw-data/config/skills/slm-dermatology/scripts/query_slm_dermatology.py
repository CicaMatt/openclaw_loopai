#!/usr/bin/env python3
import argparse
import json
import sys
from urllib import error, request

BASE_URL = "http://looporchestra.sytes.net:8007"
LOAD_ADAPTER_ENDPOINT = f"{BASE_URL}/node/load-adapter"
CHAT_ENDPOINT = f"{BASE_URL}/chat"
LOAD_ADAPTER_PAYLOAD = {
    "model": "tinyllama",
    "adapter_path": "adapters/derma_v1.0",
    "mode": "derma",
}


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


def post_json(url: str, payload: dict, timeout: int) -> str:
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} from {url}: {detail}") from e
    except Exception as e:
        raise RuntimeError(f"Request to {url} failed: {e}") from e


def load_adapter(timeout: int) -> str:
    return post_json(LOAD_ADAPTER_ENDPOINT, LOAD_ADAPTER_PAYLOAD, timeout)


def call_endpoint(question: str, timeout: int = 45) -> str:
    load_adapter(timeout)
    body = post_json(CHAT_ENDPOINT, {"question": question}, timeout)
    return extract_answer(body)


def main():
    parser = argparse.ArgumentParser(
        description="Load the dermatology adapter and query the dermatology SLM endpoint"
    )
    parser.add_argument("question", help="Dermatology question grounded in records or known context")
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
