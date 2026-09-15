"""xTranslator XML 工作脚本：词典填充、待译导出、写回。

用法（仓库根目录）：
  python dialogue_mod_translation/translate.py stats <xml-or-dir>
  python dialogue_mod_translation/translate.py pending <xml> [--fill-bdd]
  python dialogue_mod_translation/translate.py apply <pending.json>
  python dialogue_mod_translation/translate.py --self-check
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
from collections import defaultdict

DEFAULT_GRUPS = ("BOOK", "INFO", "DIAL", "NPC_")
DONE_STATUS = "90"
ESP_RE = re.compile(r"<ESP\b.*?</ESP>", re.DOTALL)
GRUP_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,4}$")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BDD_PATH = os.path.join(ROOT, "bdd.tsv")


def _utf8_stdio() -> None:
    if hasattr(sys.stdout, "buffer"):
        import io

        if not (isinstance(sys.stdout, io.TextIOWrapper) and (sys.stdout.encoding or "").lower() == "utf-8"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def get_tag(block: str, tag: str) -> str:
    m = re.search(rf"<{tag}>(.*?)</{tag}>", block, re.DOTALL)
    if m:
        return m.group(1)
    if re.search(rf"<{tag}\s*/>", block):
        return ""
    return ""


def set_traduit(block: str, text: str) -> str:
    new = f"<TRADUIT>{xml_escape(text)}</TRADUIT>"
    if re.search(r"<TRADUIT\s*/>", block):
        return re.sub(r"<TRADUIT\s*/>", new, block, count=1)
    if re.search(r"<TRADUIT>.*?</TRADUIT>", block, re.DOTALL):
        return re.sub(r"<TRADUIT>.*?</TRADUIT>", new, block, count=1, flags=re.DOTALL)
    raise ValueError("block has no TRADUIT tag")


def set_status(block: str, status: str) -> str:
    return re.sub(r"<STATUS>.*?</STATUS>", f"<STATUS>{status}</STATUS>", block, count=1, flags=re.DOTALL)


def parse_esp(block: str) -> dict:
    original_raw = get_tag(block, "ORIGINAL")
    traduit_raw = get_tag(block, "TRADUIT")
    comment = get_tag(block, "COMMENTAIRE")
    emotion = ""
    em = re.search(r"EmotionType\s*:\s*(\S+)", comment)
    if em:
        emotion = em.group(1)
    return {
        "grup": get_tag(block, "GRUP"),
        "id": get_tag(block, "ID"),
        "edid": get_tag(block, "EDID"),
        "champ": get_tag(block, "CHAMP"),
        "original": html.unescape(original_raw),
        "traduit": html.unescape(traduit_raw),
        "status": get_tag(block, "STATUS"),
        "emotion": emotion,
    }


def item_key(item: dict) -> tuple[str, str, str]:
    return item["id"], item["champ"], item["original"]



def group_key(item: dict) -> tuple[str, str, str]:
    return item["grup"], item["champ"], item["original"]



def grouped_items(items: list[dict]) -> list[dict]:
    """Build translation units without losing exact XML targets."""
    groups: dict[tuple[str, str, str], dict] = {}
    for item in items:
        key = group_key(item)
        group = groups.setdefault(
            key,
            {
                "grup": item["grup"],
                "champ": item["champ"],
                "original": item["original"],
                "traduit": "",
                "count": 0,
                "edids": [],
                "items": [],
            },
        )
        group["count"] += 1
        if item["edid"] not in group["edids"]:
            group["edids"].append(item["edid"])
        group["items"].append({"id": item["id"], "champ": item["champ"], "original": item["original"]})
        text = (item.get("traduit") or "").strip()
        if text and not group["traduit"]:
            group["traduit"] = item["traduit"]
        elif text and group["traduit"] != item["traduit"]:
            previous = group["traduit"]
            group["traduit"] = ""
            candidates = group.setdefault("candidates", [])
            for candidate in (previous, item["traduit"]):
                if candidate and candidate not in candidates:
                    candidates.append(candidate)
    return list(groups.values())


PLACEHOLDER_RE = re.compile(r"%[A-Za-z]|\\[A-Za-z]+|\$[A-Za-z_][A-Za-z0-9_]*|\{[^{}]+\}|\[[^\]]+\]|<[^>]+>")


def format_tokens(text: str) -> list[str]:
    return sorted(PLACEHOLDER_RE.findall(text))


def validate_translation(original: str, traduit: str) -> None:
    if format_tokens(original) != format_tokens(traduit):
        raise ValueError(f"placeholder/tag mismatch: {original!r} -> {traduit!r}")

def load_bdd(path: str = BDD_PATH) -> dict[tuple[str, str], list[str]]:
    """(grup, original) -> unique traduit list. Skip malformed/multiline TSV rows."""
    index: dict[tuple[str, str], list[str]] = {}
    seen: dict[tuple[str, str], set[str]] = defaultdict(set)
    with open(path, "r", encoding="utf-8") as f:
        next(f, None)
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                continue
            grup, original, traduit = parts
            if not GRUP_RE.match(grup) or not original or not traduit:
                continue
            key = (grup, original)
            if traduit in seen[key]:
                continue
            seen[key].add(traduit)
            index.setdefault(key, []).append(traduit)
    return index


def bdd_hits(index: dict[tuple[str, str], list[str]], grup: str, original: str) -> list[str]:
    return list(index.get((grup, original), ()))


def pending_blocks(xml: str, grups: set[str]) -> list[tuple[str, dict]]:
    out = []
    for block in ESP_RE.findall(xml):
        rec = parse_esp(block)
        if rec["grup"] not in grups:
            continue
        if rec["status"] != "0":
            continue
        if not rec["original"].strip() or rec["traduit"].strip():
            continue
        out.append((block, rec))
    return out


def fill_bdd(xml: str, index: dict[tuple[str, str], list[str]], grups: set[str]) -> tuple[str, int]:
    n = 0

    def repl(m: re.Match) -> str:
        nonlocal n
        block = m.group(0)
        rec = parse_esp(block)
        if rec["grup"] not in grups or rec["status"] != "0" or rec["traduit"].strip():
            return block
        hits = bdd_hits(index, rec["grup"], rec["original"])
        if len(hits) != 1:
            return block
        n += 1
        return set_status(set_traduit(block, hits[0]), DONE_STATUS)

    return ESP_RE.sub(repl, xml), n


def apply_pending(xml: str, items: list[dict], groups: list[dict] | None = None) -> tuple[str, int]:
    want = {item_key(it): it["traduit"] for it in items if (it.get("traduit") or "").strip()}
    grouped_want: dict[tuple[str, str, str], str] = {}
    grouped_targets: dict[tuple[str, str, str], set[tuple[str, str, str]]] = {}
    for group in groups or []:
        text = (group.get("traduit") or "").strip()
        if not text:
            continue
        key = group_key(group)
        grouped_want[key] = group["traduit"]
        grouped_targets[key] = {item_key(target) for target in group.get("items", [])}
    n = 0

    def repl(m: re.Match) -> str:
        nonlocal n
        block = m.group(0)
        rec = parse_esp(block)
        key = item_key(rec)
        group = group_key(rec)
        text = None
        if key in grouped_targets.get(group, set()):
            text = grouped_want[group]
        if not text:
            text = want.get(key)
        if not text or rec["status"] != "0" or rec["traduit"].strip():
            return block
        validate_translation(rec["original"], text)
        n += 1
        return set_status(set_traduit(block, text), DONE_STATUS)

    return ESP_RE.sub(repl, xml), n

# ponytail: scan one directory level; mod layout keeps XML beside pending.json.
def xml_paths(path: str) -> list[str]:
    if not os.path.isdir(path):
        return [path]
    paths = [os.path.join(path, name) for name in sorted(os.listdir(path)) if name.lower().endswith(".xml")]
    if not paths:
        raise ValueError(f"no XML files found: {path}")
    return paths


def stats(xml: str, grups: set[str]) -> None:
    if "\ufffd" in xml:
        print(f"警告: 原文含替换字符 �，疑似编码损坏（{xml.count(chr(0xfffd))} 处）")
    from collections import Counter

    gcount: Counter[str] = Counter()
    pending: Counter[str] = Counter()
    done: Counter[str] = Counter()
    for block in ESP_RE.findall(xml):
        rec = parse_esp(block)
        g = rec["grup"] or "?"
        gcount[g] += 1
        empty = not rec["traduit"].strip()
        if rec["status"] == "0" and empty:
            pending[g] += 1
        elif rec["traduit"].strip():
            done[g] += 1
    print(f"{'GRUP':<8} {'总数':<8} {'待译(0)':<10} {'已有译文'}")
    print("-" * 40)
    for g, c in sorted(gcount.items()):
        mark = "*" if g in grups else " "
        print(f"{mark}{g:<7} {c:<8} {pending[g]:<10} {done[g]}")
    print("-" * 40)
    print(f"默认 GRUP 待译: {sum(pending[g] for g in grups)}")


def pending_path_for(xml_path: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(xml_path)), "pending.json")


def merge_old_traduit(items: list[dict], old_path: str) -> None:
    if not os.path.exists(old_path):
        return
    with open(old_path, "r", encoding="utf-8") as f:
        old = json.load(f)
    prev = {item_key(it): it.get("traduit", "") for it in old.get("items", [])}
    prev_groups = {group_key(group): group.get("traduit", "") for group in old.get("groups", [])}
    for item in items:
        text = prev.get(item_key(item)) or prev_groups.get(group_key(item), "")
        if text and not item.get("traduit"):
            item["traduit"] = text

def cmd_pending(xml_path: str, grups: set[str], do_fill: bool, out_path: str) -> None:
    xml = open(xml_path, encoding="utf-8-sig", newline="").read()
    filled = 0
    if do_fill:
        index = load_bdd()
        xml, filled = fill_bdd(xml, index, grups)
        with open(xml_path, "w", encoding="utf-8", newline="") as f:
            f.write(xml)
        print(f"bdd 唯一命中已写入 {filled} 条")
        index_for_hits = index
    else:
        index_for_hits = load_bdd()

    items = []
    for _, rec in pending_blocks(xml, grups):
        hits = bdd_hits(index_for_hits, rec["grup"], rec["original"])
        items.append(
            {
                "id": rec["id"],
                "edid": rec["edid"],
                "grup": rec["grup"],
                "champ": rec["champ"],
                "original": rec["original"],
                "traduit": hits[0] if len(hits) == 1 else "",
                "emotion": rec["emotion"],
                "bdd": hits,
            }
        )
    merge_old_traduit(items, out_path)
    payload = {
        "xml": os.path.relpath(xml_path, ROOT).replace("\\", "/"),
        "grups": sorted(grups),
        "items": items,
        "groups": grouped_items(items),
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    empty = sum(1 for it in items if not it["traduit"])
    group_empty = sum(1 for group in payload["groups"] if not group["traduit"])
    print(f"pending {len(items)} 条，去重为 {len(payload['groups'])} 组（其中 {empty} 条 / {group_empty} 组无译文）-> {out_path}")

def cmd_apply(pending_file: str) -> None:
    with open(pending_file, "r", encoding="utf-8") as f:
        payload = json.load(f)
    xml_path = payload["xml"]
    if not os.path.isabs(xml_path):
        xml_path = os.path.join(ROOT, xml_path)
    xml = open(xml_path, encoding="utf-8-sig", newline="").read()
    xml, n = apply_pending(xml, payload.get("items", []), payload.get("groups", []))
    with open(xml_path, "w", encoding="utf-8", newline="") as f:
        f.write(xml)
    left = sum(1 for _, rec in pending_blocks(xml, set(payload.get("grups", DEFAULT_GRUPS))))
    print(f"写入 {n} 条 -> {xml_path}；剩余待译 {left}")


def _self_check() -> None:
    sample = """<?xml version="1.0" encoding="utf-8"?>
<DocumentElement>
  <ESP>
    <GRUP>NPC_</GRUP>
    <ID>00000001</ID>
    <EDID>TestNpc</EDID>
    <CHAMP>FULL</CHAMP>
    <ORIGINAL>Hello &amp; Hi</ORIGINAL>
    <TRADUIT />
    <STATUS>0</STATUS>
  </ESP>
</DocumentElement>
"""
    rec = parse_esp(ESP_RE.findall(sample)[0])
    assert rec["original"] == "Hello & Hi", rec
    filled, n = fill_bdd(sample, {("NPC_", "Hello & Hi"): ["你好"]}, {"NPC_"})
    assert n == 1 and "<TRADUIT>你好</TRADUIT>" in filled and "<STATUS>90</STATUS>" in filled
    pending = [{"id": "00000001", "champ": "FULL", "original": "Hello & Hi", "traduit": "你好&我"}]
    applied, n2 = apply_pending(sample, pending)
    assert n2 == 1 and "&amp;" in applied and "<TRADUIT>你好&amp;我</TRADUIT>" in applied
    groups = grouped_items([
        {
            "id": "00000001", "edid": "TestNpc", "grup": "NPC_", "champ": "FULL",
            "original": "Hello & Hi", "traduit": "你好",
        },
        {
            "id": "00000002", "edid": "TestNpc2", "grup": "NPC_", "champ": "FULL",
            "original": "Hello & Hi", "traduit": "你好",
        },
    ])
    assert len(groups) == 1 and groups[0]["count"] == 2
    try:
        validate_translation("%s", "缺少占位符")
    except ValueError:
        pass
    else:
        raise AssertionError("placeholder validation failed")
    applied_group, n3 = apply_pending(sample, [{
        "id": "00000001", "champ": "FULL", "original": "Hello & Hi", "traduit": "旧译",
    }], groups)
    assert n3 == 1 and "<TRADUIT>你好</TRADUIT>" in applied_group
    print("self-check OK")


def parse_grups(arg: str | None) -> set[str]:
    if not arg:
        return set(DEFAULT_GRUPS)
    return {g.strip() for g in arg.split(",") if g.strip()}


def main(argv: list[str]) -> None:
    _utf8_stdio()
    if "--self-check" in argv or (len(argv) > 1 and argv[1] == "--self-check"):
        _self_check()
        return
    if len(argv) < 3:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    cmd = argv[1]
    grups = set(DEFAULT_GRUPS)
    if "--grups" in argv:
        i = argv.index("--grups")
        grups = parse_grups(argv[i + 1] if i + 1 < len(argv) else "")
    if cmd == "stats":
        paths = xml_paths(argv[2])
        for path in paths:
            if len(paths) > 1 or os.path.isdir(argv[2]):
                print(f"\n## {path}")
            stats(open(path, encoding="utf-8-sig", newline="").read(), grups)
        return
    if cmd == "pending":
        xml_path = argv[2]
        out = pending_path_for(xml_path)
        if "--out" in argv:
            out = argv[argv.index("--out") + 1]
        cmd_pending(xml_path, grups, do_fill="--fill-bdd" in argv, out_path=out)
        return
    if cmd == "apply":
        cmd_apply(argv[2])
        return
    if cmd == "fill-bdd":
        cmd_pending(argv[2], grups, do_fill=True, out_path=pending_path_for(argv[2]))
        return
    print(f"unknown command: {cmd}", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main(sys.argv)
