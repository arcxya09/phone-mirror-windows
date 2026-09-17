"""Offline checks for the design package; this does not test the Windows app."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {'.git', '__pycache__', '.venv', '.vs', 'artifacts'}


def package_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob('*') if p.is_file()
                  and not any(x in IGNORED for x in p.relative_to(root).parts)
                  and p.suffix not in {'.pyc', '.pyo'}
                  and p.name != 'MANIFEST.sha256')


def manifest_text(root: Path) -> str:
    return ''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  '
                   f'{p.relative_to(root).as_posix()}\n' for p in package_files(root))


def local_link_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for p in package_files(root):
        if p.suffix != '.md':
            continue
        text = p.read_text(encoding='utf-8')
        # This package uses simple inline links; fenced examples are not links.
        text = re.sub(r'```.*?```', '', text, flags=re.S)
        for target in re.findall(r'\]\(([^\s)]+)\)', text):
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            dest = (p.parent / unquote(url.path)).resolve()
            if not dest.is_relative_to(root.resolve()) or not dest.exists():
                errors.append(f'{p.relative_to(root)}: missing/unsafe link {target}')
    return errors


def validate_contract(root: Path, value: dict, schema_name: str) -> None:
    schema = json.loads((root / 'schemas' / schema_name).read_text(encoding='utf-8'))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)
    if schema_name == 'local-ipc.schema.json':
        encoded = json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        if len(encoded) > 65536:
            raise ValueError('IPC message exceeds 65536 UTF-8 bytes')
        if value['method'] == 'InsertText':
            if len(value['payload']['text'].encode('utf-8')) > 16384:
                raise ValueError('Text exceeds 16384 UTF-8 bytes')
            if int(value['inputSequence']) > (1 << 64) - 1:
                raise ValueError('Input sequence exceeds UInt64')


def check_package(root: Path, check_manifest: bool = True,
                  require_manifest: bool = False) -> list[str]:
    errors: list[str] = []
    for p in package_files(root):
        try:
            text = p.read_bytes().decode('utf-8')
            if '\r' in text or not text.endswith('\n'):
                errors.append(f'{p.relative_to(root)}: require LF and final newline')
            if p.suffix == '.json':
                json.loads(text)
        except (UnicodeError, ValueError) as exc:
            errors.append(f'{p.relative_to(root)}: {exc}')
    if errors:
        return errors
    errors.extend(local_link_errors(root))
    for sample, schema in [('application-settings.json', 'application-settings.schema.json'),
                           ('ipc-insert-text.json', 'local-ipc.schema.json')]:
        try:
            value = json.loads((root / 'examples' / sample).read_text(encoding='utf-8'))
            validate_contract(root, value, schema)
        except Exception as exc:
            errors.append(f'{sample}: {exc}')
    try:
        plan = (root / 'docs/06-test-plan.md').read_text(encoding='utf-8')
        ids = re.findall(r'^\| ([CVITAUS]\d{2}) \|', plan, flags=re.M)
        if len(ids) != 78 or len(set(ids)) != 78:
            errors.append('Expected 78 unique product acceptance cases')
        references = (root / 'docs/09-references.md').read_text(encoding='utf-8')
        known = set(re.findall(r'^\| (R\d+) \|', references, flags=re.M))
        for p in package_files(root):
            if p.suffix == '.md':
                for ref in re.findall(r'\[(R\d+)\]', p.read_text(encoding='utf-8')):
                    if ref not in known:
                        errors.append(f'{p.relative_to(root)}: undefined reference {ref}')
    except OSError as exc:
        errors.append(f'Required design document missing: {exc}')
    if check_manifest:
        manifest = root / 'MANIFEST.sha256'
        if manifest.exists():
            if manifest.read_text(encoding='utf-8') != manifest_text(root):
                errors.append('Manifest mismatch; review changes before --refresh-manifest')
        elif require_manifest:
            errors.append('Manifest required but absent; use --refresh-manifest after review')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--refresh-manifest', action='store_true')
    group.add_argument('--require-manifest', action='store_true')
    args = parser.parse_args()
    errors = check_package(ROOT, check_manifest=not args.refresh_manifest,
                           require_manifest=args.require_manifest)
    if errors:
        print('\n'.join(errors))
        return 1
    if args.refresh_manifest:
        (ROOT / 'MANIFEST.sha256').write_text(manifest_text(ROOT), encoding='utf-8', newline='\n')
    print(f'PASS: {len(package_files(ROOT))} files; local links, contracts, '
          '78 acceptance definitions and references.')
    if (ROOT / 'MANIFEST.sha256').exists():
        print('SHA256 manifest: generated.' if args.refresh_manifest else 'SHA256 manifest: verified.')
    else:
        print('SHA256 manifest: absent (optional); no digest verification claimed.')
    print('Windows compilation and all product/device/performance tests: NOT RUN.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
