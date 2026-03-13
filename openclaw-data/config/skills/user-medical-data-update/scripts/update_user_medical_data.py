#!/usr/bin/env python3
import argparse
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path('/home/node/openclaw-shared/user_medical_data')
BASIC_TEMPLATE = {
    'full_name': None,
    'preferred_name': None,
    'date_of_birth': None,
    'age': None,
    'sex': None,
    'gender': None,
    'blood_type': None,
    'height_cm': None,
    'weight_kg': None,
    'allergies': [],
    'chronic_conditions': [],
    'medications': [],
    'emergency_contact': None,
    'primary_physician': None,
    'notes': None,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def ensure_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def sanitize_identifier(value: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9._-]+', '_', value.strip())
    cleaned = cleaned.strip('._-')
    return cleaned or 'unknown-user'


def extract_telegram_user_id(payload: Dict[str, Any]) -> Optional[str]:
    direct = str(payload.get('telegram_user_id', '')).strip()
    if direct:
        return direct

    channel_identifiers = payload.get('channel_identifiers') or {}
    nested = str(channel_identifiers.get('telegram_user_id', '')).strip()
    if nested:
        return nested

    return None


def resolve_canonical_user_id(payload: Dict[str, Any], user_id: str) -> str:
    telegram_user_id = extract_telegram_user_id(payload)
    if telegram_user_id:
        return telegram_user_id
    return user_id


def resolve_storage_folder_name(payload: Dict[str, Any], user_id: str) -> str:
    return sanitize_identifier(resolve_canonical_user_id(payload, user_id))


def load_payload_from_file(path: Path) -> Dict[str, Any]:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def load_payload_from_stdin() -> Dict[str, Any]:
    return json.load(__import__('sys').stdin)


def empty_record(user_id: str, telegram_user_id: Optional[str] = None) -> Dict[str, Any]:
    return {
        'schema_version': '1.0',
        'user_id': user_id,
        'telegram_user_id': telegram_user_id,
        'created_at': now_iso(),
        'updated_at': now_iso(),
        'basic_health_data': deepcopy(BASIC_TEMPLATE),
        'symptom_health_timeline': [],
    }


def load_existing(record_path: Path, user_id: str, telegram_user_id: Optional[str] = None) -> Dict[str, Any]:
    if not record_path.exists():
        return empty_record(user_id, telegram_user_id=telegram_user_id)
    with record_path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    if 'basic_health_data' not in data:
        data['basic_health_data'] = deepcopy(BASIC_TEMPLATE)
    else:
        for key, default in BASIC_TEMPLATE.items():
            data['basic_health_data'].setdefault(key, deepcopy(default))
    data.setdefault('symptom_health_timeline', [])
    data.setdefault('schema_version', '1.0')
    data.setdefault('user_id', user_id)
    data.setdefault('telegram_user_id', telegram_user_id)
    data.setdefault('created_at', now_iso())
    return data


def merge_basic(existing: Dict[str, Any], updates: Dict[str, Any]) -> None:
    for key, value in (updates or {}).items():
        if value is None or value == '':
            continue
        if isinstance(existing['basic_health_data'].get(key), list):
            merged = existing['basic_health_data'].get(key, [])[:]
            for item in ensure_list(value):
                if item not in merged:
                    merged.append(item)
            existing['basic_health_data'][key] = merged
        else:
            existing['basic_health_data'][key] = value


def normalize_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    timestamp = entry.get('timestamp') or now_iso()
    return {
        'timestamp': timestamp,
        'type': entry.get('type', 'health_note'),
        'text': entry.get('text', '').strip(),
        'source': entry.get('source', 'user_report'),
        'status': entry.get('status', 'reported'),
        'metadata': entry.get('metadata', {}),
    }


def merge_timeline(existing: Dict[str, Any], incoming_entries: List[Dict[str, Any]]) -> int:
    timeline = existing['symptom_health_timeline']
    existing_keys = {
        (
            item.get('timestamp'),
            item.get('type'),
            item.get('text', '').strip().lower(),
            item.get('source'),
        )
        for item in timeline
    }
    added = 0
    for raw in incoming_entries or []:
        entry = normalize_entry(raw)
        if not entry['text']:
            continue
        key = (
            entry['timestamp'],
            entry['type'],
            entry['text'].strip().lower(),
            entry['source'],
        )
        if key in existing_keys:
            continue
        timeline.append(entry)
        existing_keys.add(key)
        added += 1
    timeline.sort(key=lambda x: (x.get('timestamp') or '', x.get('type') or '', x.get('text') or ''))
    return added


def main() -> int:
    parser = argparse.ArgumentParser(description='Create or update structured user medical data records.')
    parser.add_argument('--payload-file', help='Path to a JSON payload file.')
    parser.add_argument('--payload-stdin', action='store_true', help='Read the JSON payload from stdin.')
    args = parser.parse_args()

    if bool(args.payload_file) == bool(args.payload_stdin):
        raise SystemExit('Provide exactly one of --payload-file or --payload-stdin')

    if args.payload_stdin:
        payload = load_payload_from_stdin()
    else:
        payload = load_payload_from_file(Path(args.payload_file))
    user_id = str(payload.get('user_id', '')).strip()
    if not user_id:
        raise SystemExit('payload must include user_id')

    telegram_user_id = extract_telegram_user_id(payload)
    canonical_user_id = resolve_canonical_user_id(payload, user_id)
    storage_folder_name = resolve_storage_folder_name(payload, user_id)

    user_dir = BASE_DIR / storage_folder_name
    user_dir.mkdir(parents=True, exist_ok=True)
    record_path = user_dir / 'medical_data.json'

    record = load_existing(record_path, canonical_user_id, telegram_user_id=telegram_user_id)
    record['user_id'] = canonical_user_id
    if telegram_user_id:
        record['telegram_user_id'] = telegram_user_id
    merge_basic(record, payload.get('basic_health_data', {}))
    added = merge_timeline(record, payload.get('symptom_health_timeline', []))
    record['updated_at'] = now_iso()

    with record_path.open('w', encoding='utf-8') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
        f.write('\n')

    result = {
        'record_path': str(record_path),
        'storage_folder_name': storage_folder_name,
        'user_id': record['user_id'],
        'telegram_user_id': telegram_user_id,
        'timeline_entries_added': added,
        'updated_at': record['updated_at'],
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
