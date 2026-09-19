import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
sys.path.insert(0, root_dir)

from locale_utils import load_json, translation_format_issues


def flatten(value, prefix="", out=None):
    out = {} if out is None else out
    if isinstance(value, dict):
        for key, child in value.items():
            flatten(child, f"{prefix}.{key}" if prefix else key, out)
    else:
        out[prefix] = value
    return out


source = flatten(load_json(os.path.join(script_dir, "Language.json")))
output = flatten(load_json(os.path.join(script_dir, "Language_zh.json")))
translations = load_json(os.path.join(script_dir, "translations.json"))
issues = []

missing = sorted(source.keys() - output.keys())
extra = sorted(output.keys() - source.keys())
if missing:
    issues.append(f"Missing in ZH ({len(missing)}): {', '.join(missing[:10])}")
if extra:
    issues.append(f"Extra in ZH ({len(extra)}): {', '.join(extra[:10])}")
for path, translated in translations.items():
    if output.get(path) != translated:
        issues.append(f"Stale translation: {path}")
for path in sorted(source.keys() & output.keys()):
    if isinstance(source[path], str) and isinstance(output[path], str):
        format_issues = translation_format_issues(source[path], output[path])
        if format_issues:
            issues.append(f"Format mismatch: {path}: {'; '.join(format_issues)}")

if issues:
    print("\n".join(issues))
else:
    print(f"Perfect match: {len(output)} keys, {len(translations)} managed translations")
raise SystemExit(bool(issues))
