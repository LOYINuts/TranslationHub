import json
import re
from collections import Counter

from generate_zh import ROOT, apply, flatten, load_jsonc

source = flatten(load_jsonc(ROOT / "LogWatcherTranslation.json"))
translations = json.loads((ROOT / "translations.json").read_text(encoding="utf-8"))
output = json.loads((ROOT / "LogWatcherTranslation_zh.json").read_text(encoding="utf-8"))
if set(source) != set(translations):
    raise SystemExit("Translation keys do not match the source")
if output != apply(load_jsonc(ROOT / "LogWatcherTranslation.json"), translations):
    raise SystemExit("Generated translation is out of date")
tokens = re.compile(r"\{[^{}]+\}")
for key, original in source.items():
    if Counter(tokens.findall(original)) != Counter(tokens.findall(translations[key])):
        raise SystemExit(f"Placeholder mismatch: {key}")
print(f"Verified {len(source)} LogWatcher strings")
