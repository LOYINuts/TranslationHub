import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(SCRIPT_DIR)))

from locale_utils import read_lines, parse_tab_lines

lines = read_lines(os.path.join(SCRIPT_DIR, "KillFeed_ENGLISH.txt"))
entries = [{"key": k, "en": v} for k, v in parse_tab_lines(lines)]

with open(os.path.join(SCRIPT_DIR, "killfeed_template.json"), "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f"完成，共 {len(entries)} 条 -> killfeed_template.json")

