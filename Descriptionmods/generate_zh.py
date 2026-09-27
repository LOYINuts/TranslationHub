from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TRANSLATIONS = ROOT / "translations.json"


def read_text(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"\xff\xfe"):
        return data[2:].decode("utf-16-le")
    if data.startswith(b"\xfe\xff"):
        return data[2:].decode("utf-16-be")
    return data.decode("utf-8-sig")


def write_text(path: Path, text: str, template: Path) -> None:
    data = template.read_bytes()
    if data.startswith(b"\xff\xfe"):
        path.write_bytes(b"\xff\xfe" + text.encode("utf-16-le"))
    elif data.startswith(b"\xfe\xff"):
        path.write_bytes(b"\xfe\xff" + text.encode("utf-16-be"))
    elif data.startswith(b"\xef\xbb\xbf"):
        path.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
    else:
        path.write_bytes(text.encode("utf-8"))




def render(source: Path, translations: dict) -> str:
    relative = source.relative_to(ROOT).as_posix()
    file_translations = translations.get(relative)
    if not isinstance(file_translations, dict):
        raise ValueError(f"Missing translation map: {relative}")
    seen = defaultdict(int)
    output = []
    for line in read_text(source).splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        if not body or body.startswith("#") or "|" not in body:
            output.append(line)
            continue
        key, remainder = body.split("|", 1)
        values = file_translations.get(key)
        if not isinstance(values, list):
            raise ValueError(f"Missing translation list: {relative}:{key}")
        index = seen[key]
        if index >= len(values):
            raise ValueError(f"Too many source records: {relative}:{key}")
        translated = values[index]
        seen[key] += 1
        if "|" in remainder:
            _, metadata = remainder.split("|", 1)
            output.append(f"{key}|{translated}|{metadata.rstrip()}{ending}")
        else:
            output.append(f"{key}|{translated}{ending}")
    for key, values in file_translations.items():
        if seen[key] != len(values):
            raise ValueError(f"Unused translation values: {relative}:{key}")
    return "".join(output)


def main() -> int:
    args = sys.argv[1:]
    check = args == ["--check"]
    if args and not check:
        raise SystemExit("usage: python generate_zh.py [--check]")
    translations = json.loads(TRANSLATIONS.read_text(encoding="utf-8"))
    records = sum(len(values) for file_map in translations.values() for values in file_map.values())
    for source in sorted(ROOT.rglob("*.ini")):
        if "zh" in source.relative_to(ROOT).parts:
            continue
        target = ROOT / "zh" / source.relative_to(ROOT)
        expected = render(source, translations)
        if check:
            if not target.exists() or read_text(target) != expected:
                raise ValueError(f"Generated file is stale: {target.relative_to(ROOT)}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            write_text(target, expected, source)
    print(f"总计: {records}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
