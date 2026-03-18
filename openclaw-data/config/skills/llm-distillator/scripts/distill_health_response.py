#!/usr/bin/env python3
"""Distill health conversation context + diagnostic tool output via Hugging Face."""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct"
HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN_PLACEHOLDER = "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"

SYSTEM_PROMPT = """You are a medically cautious synthesis assistant.
Your task is to combine health-related conversation context with diagnostic tool output into one clear, comprehensive answer for the user.

Rules:
- Use only the provided information.
- Do not invent symptoms, diagnoses, measurements, or timelines.
- Separate likely findings from uncertainty.
- If the inputs suggest emergency red flags, explicitly say urgent medical evaluation is warranted.
- If the tool output has limitations, reflect them.
- Keep the tone calm, clear, and accessible to a non-expert.
- End with practical next-step guidance when appropriate.
"""

USER_PROMPT_TEMPLATE = """Create a comprehensive explanation for the user by combining the two sources below.

Conversation context:
{context}

Diagnostic tool output:
{diagnosis}

Write a final answer that:
1. Briefly summarizes the overall picture.
2. Explains what in the conversation is clinically relevant.
3. Explains what the diagnostic tool output suggests.
4. States uncertainty, caveats, or contradictions clearly.
5. Gives practical next-step guidance and notes urgency if needed.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", help="Health-related conversation context text")
    parser.add_argument("--context-file", help="Path to a file containing conversation context")
    parser.add_argument("--diagnosis", help="Diagnostic tool output text")
    parser.add_argument("--diagnosis-file", help="Path to a file containing diagnostic tool output")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Hugging Face model id (default: {DEFAULT_MODEL})")
    parser.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature")
    parser.add_argument("--max-tokens", type=int, default=700, help="Maximum completion tokens")
    parser.add_argument("--timeout", type=int, default=90, help="HTTP timeout in seconds")
    parser.add_argument("--output-file", help="Optional output file path")
    parser.add_argument("--print-prompt", action="store_true", help="Print the assembled prompt and exit")
    return parser.parse_args()


def read_text_arg(raw_text: str | None, file_path: str | None, label: str) -> str:
    if raw_text:
        return raw_text.strip()
    if file_path:
        return Path(file_path).read_text(encoding="utf-8").strip()
    raise SystemExit(f"Missing required input for {label}. Provide --{label} or --{label}-file.")


def build_user_prompt(context: str, diagnosis: str) -> str:
    return USER_PROMPT_TEMPLATE.format(context=context.strip(), diagnosis=diagnosis.strip())


def resolve_token() -> str:
    env_token = os.getenv("HUGGING_FACE_TOKEN") or os.getenv("HF_TOKEN")
    if env_token:
        return env_token.strip()
    return HF_TOKEN_PLACEHOLDER.strip()


def call_hugging_face(token: str, model: str, prompt: str, temperature: float, max_tokens: int, timeout: int) -> str:
    if not token:
        raise SystemExit(
            "Set HUGGING_FACE_TOKEN (or HF_TOKEN) in the environment, or replace HF_TOKEN_PLACEHOLDER in the script with your real token."
        )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    req = urllib.request.Request(
        HF_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            response_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Hugging Face API error ({exc.code}): {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Network error contacting Hugging Face: {exc}") from exc

    try:
        return response_data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        pretty = json.dumps(response_data, indent=2, ensure_ascii=False)
        raise SystemExit(f"Unexpected API response format:\n{pretty}") from exc


def main() -> int:
    args = parse_args()

    context = read_text_arg(args.context, args.context_file, "context")
    diagnosis = read_text_arg(args.diagnosis, args.diagnosis_file, "diagnosis")
    prompt = build_user_prompt(context, diagnosis)

    if args.print_prompt:
        print("=== SYSTEM PROMPT ===")
        print(SYSTEM_PROMPT.strip())
        print("\n=== USER PROMPT ===")
        print(prompt)
        return 0

    token = resolve_token()
    output = call_hugging_face(
        token=token,
        model=args.model,
        prompt=prompt,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
    )

    if args.output_file:
        Path(args.output_file).write_text(output + "\n", encoding="utf-8")

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
