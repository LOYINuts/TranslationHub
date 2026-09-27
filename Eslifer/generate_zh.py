from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "origin" / "eslifier_translation.ts"
OUTPUT = ROOT / "eslifier_translation.ts"
TRANSLATIONS = ROOT / "translations.json"
sys.path.insert(0, str(ROOT.parent))
from locale_utils import translation_format_issues


def build() -> str:
    source_text = SOURCE.read_bytes().decode("utf-8").removeprefix("\ufeff")
    translations = json.loads(TRANSLATIONS.read_text(encoding="utf-8"))
    tree = ET.fromstring(source_text)
    seen = set()
    for message in tree.findall(".//message"):
        source = "".join(message.find("source").itertext())
        translation = translations.get(source)
        if not isinstance(translation, str):
            raise ValueError(f"Missing translation: {source}")
        issues = translation_format_issues(source, translation)
        if issues:
            raise ValueError(f"{source}: {'; '.join(issues)}")
        node = message.find("translation")
        if node is None:
            node = ET.SubElement(message, "translation")
        node.attrib.pop("type", None)
        node.text = translation
        seen.add(source)
    extra = set(translations) - seen
    if extra:
        raise ValueError(f"Unused translation keys: {len(extra)}")
    start = source_text.find("<TS")
    end = source_text.rfind("</TS>") + len("</TS>")
    if start < 0 or end < len("</TS>"):
        raise ValueError("Invalid Qt TS root")
    newline = "\r\n" if "\r\n" in source_text else "\n"
    body = ET.tostring(tree, encoding="unicode", short_empty_elements=True)
    body = body.replace("\r\n", "\n").replace("\n", newline)
    return source_text[:start] + body + source_text[end:]


def main() -> int:
    check = sys.argv[1:] == ["--check"]
    if sys.argv[1:] and not check:
        raise SystemExit("usage: python generate_zh.py [--check]")
    expected = build()
    if check:
        if not OUTPUT.exists() or OUTPUT.read_bytes().decode("utf-8") != expected:
            raise ValueError("Generated Qt TS file is stale")
    else:
        OUTPUT.write_bytes(expected.encode("utf-8"))
    print(f"总计: {len(json.loads(TRANSLATIONS.read_text(encoding='utf-8')))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
