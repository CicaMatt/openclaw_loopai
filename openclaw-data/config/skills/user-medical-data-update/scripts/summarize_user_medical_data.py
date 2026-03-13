#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path('/home/node/openclaw-shared/user_medical_data')


def sanitize_identifier(value: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9._-]+', '_', value.strip())
    cleaned = cleaned.strip('._-')
    return cleaned or 'unknown-user'


def load_json_record(record_path: Path) -> Dict[str, Any]:
    with record_path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    data['_record_path'] = str(record_path)
    return data


def find_record_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    direct_path = BASE_DIR / sanitize_identifier(user_id) / 'medical_data.json'
    if direct_path.exists():
        return load_json_record(direct_path)

    for record_path in BASE_DIR.glob('*/medical_data.json'):
        data = load_json_record(record_path)
        if str(data.get('user_id', '')).strip() == user_id:
            return data
    return None


def load_record(user_id: Optional[str] = None, telegram_user_id: Optional[str] = None) -> Dict[str, Any]:
    if telegram_user_id:
        record_path = BASE_DIR / sanitize_identifier(telegram_user_id) / 'medical_data.json'
        if not record_path.exists():
            raise FileNotFoundError(
                f'No medical data found for telegram_user_id={telegram_user_id} at {record_path}'
            )
        return load_json_record(record_path)

    if user_id:
        data = find_record_by_user_id(user_id)
        if data is not None:
            return data
        raise FileNotFoundError(f'No medical data found for user_id={user_id} under {BASE_DIR}')

    raise ValueError('Either user_id or telegram_user_id is required')


def nonempty_basic_fields(basic: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for key, value in (basic or {}).items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        if isinstance(value, list) and not value:
            continue
        result[key] = value
    return result


def latest_entries(timeline: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    sorted_items = sorted(
        timeline or [],
        key=lambda x: (x.get('timestamp') or '', x.get('type') or '', x.get('text') or ''),
        reverse=True,
    )
    return sorted_items[:limit]


def build_summary(data: Dict[str, Any], recent_limit: int) -> Dict[str, Any]:
    basic = nonempty_basic_fields(data.get('basic_health_data', {}))
    timeline = data.get('symptom_health_timeline', [])
    recent = latest_entries(timeline, recent_limit)

    symptom_count = sum(1 for item in timeline if item.get('type') == 'symptom')
    measurement_count = sum(1 for item in timeline if item.get('type') == 'measurement')

    return {
        'user_id': data.get('user_id'),
        'telegram_user_id': data.get('telegram_user_id'),
        'record_path': data.get('_record_path'),
        'created_at': data.get('created_at'),
        'updated_at': data.get('updated_at'),
        'basic_health_data': basic,
        'timeline_entry_count': len(timeline),
        'symptom_entry_count': symptom_count,
        'measurement_entry_count': measurement_count,
        'recent_timeline_entries': recent,
    }


def print_human_summary(summary: Dict[str, Any]) -> None:
    print(f"User ID: {summary.get('user_id')}")
    print(f"Telegram User ID: {summary.get('telegram_user_id')}")
    print(f"Record: {summary.get('record_path')}")
    print(f"Created: {summary.get('created_at')}")
    print(f"Updated: {summary.get('updated_at')}")
    print('')
    print('Basic health data:')
    basic = summary.get('basic_health_data') or {}
    if not basic:
        print('- None recorded')
    else:
        for key, value in basic.items():
            print(f'- {key}: {value}')
    print('')
    print(f"Timeline entries: {summary.get('timeline_entry_count', 0)}")
    print(f"Symptoms logged: {summary.get('symptom_entry_count', 0)}")
    print(f"Measurements logged: {summary.get('measurement_entry_count', 0)}")
    print('')
    print('Recent timeline entries:')
    recent = summary.get('recent_timeline_entries') or []
    if not recent:
        print('- None recorded')
    else:
        for item in recent:
            print(f"- [{item.get('timestamp')}] {item.get('type')}: {item.get('text')}")


def main() -> int:
    parser = argparse.ArgumentParser(description='Summarize structured user medical data records.')
    parser.add_argument('--user-id', help='Stable logical user identifier stored in the record')
    parser.add_argument('--telegram-user-id', help='Telegram user ID used as the storage folder name')
    parser.add_argument('--recent-limit', type=int, default=10, help='Number of recent timeline entries to show')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    args = parser.parse_args()

    if not args.user_id and not args.telegram_user_id:
        raise SystemExit('Provide --user-id or --telegram-user-id')

    data = load_record(user_id=args.user_id, telegram_user_id=args.telegram_user_id)
    summary = build_summary(data, args.recent_limit)

    if args.format == 'json':
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print_human_summary(summary)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
