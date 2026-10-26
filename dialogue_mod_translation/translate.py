"""xTranslator XML 工作脚本：词典填充、待译导出、写回。

用法（仓库根目录）：
  uv run dialogue_mod_translation/translate.py stats <xml-or-dir>
  uv run dialogue_mod_translation/translate.py pending <xml> [--fill-bdd]
  uv run dialogue_mod_translation/translate.py apply <pending.json>
  uv run dialogue_mod_translation/translate.py rewrite <pending.json>
  uv run dialogue_mod_translation/translate.py bdd [--check|--normalize]
  uv run dialogue_mod_translation/translate.py --self-check
"""

from __future__ import annotations

import contextlib
import csv
import html
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from locale_utils import (
    BOM_UTF8,
    force_utf8_stdout,
    translation_format_issues,
)
from locale_utils import (
    format_tokens as _shared_format_tokens,
)

DEFAULT_GRUPS = ("BOOK", "INFO", "DIAL", "NPC_")
DONE_STATUS = "90"
ESP_RE = re.compile(r"<ESP\b.*?</ESP>", re.DOTALL)
GRUP_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,4}$")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BDD_PATH = os.path.join(ROOT, "bdd.tsv")


def read_xml(path: str) -> tuple[str, bool]:
    """Read a UTF-8 xTranslator XML and report whether it had a BOM."""
    with open(path, "rb") as handle:
        raw = handle.read()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        raise ValueError(f"xTranslator XML 应为 UTF-8，实际为 UTF-16: {path}")
    has_bom = raw.startswith(BOM_UTF8)
    return (raw[len(BOM_UTF8):] if has_bom else raw).decode("utf-8"), has_bom


def write_xml(path: str, text: str, has_bom: bool) -> None:
    """Write the XML back with its original BOM state. ponytail: preserve the xTranslator byte shape."""
    payload = text.encode("utf-8")
    with open(path, "wb") as handle:
        handle.write((BOM_UTF8 + payload) if has_bom else payload)


def _utf8_stdio() -> None:
    force_utf8_stdout()


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
        "status": get_tag(block, "STATUS").strip(),
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


# 共享 token 提取（locale_utils）+ XML 转义和裸尖括号，后者是旧校验器的覆盖面
_EXTRA_TOKEN_RE = re.compile(r"\\[A-Za-z]+|<[^>]+>")


def format_tokens(text: str) -> list[str]:
    return _shared_format_tokens(text) + _EXTRA_TOKEN_RE.findall(text)


def validate_translation(original: str, traduit: str) -> None:
    issues = translation_format_issues(original, traduit)
    if Counter(format_tokens(original)) != Counter(format_tokens(traduit)):
        issues.append("placeholder/tag mismatch")
    if issues:
        raise ValueError(f"{'; '.join(issues)}: {original!r} -> {traduit!r}")

BDD_HEADER = ("grup", "original", "traduit")


def bdd_blocks(path: str = BDD_PATH):
    """Yield the raw text of every TSV record. A record ends at a newline outside quotes."""
    buffer: list[str] = []
    quotes = 0
    with open(path, encoding="utf-8", newline="") as handle:
        for line in handle:
            buffer.append(line)
            quotes += line.count('"')
            if quotes % 2 == 0:
                yield "".join(buffer)
                buffer = []
    if buffer:
        yield "".join(buffer)


def bdd_fields(block: str) -> list[str]:
    """Split one TSV record into columns, honouring quoted fields."""
    row = next(csv.reader(io.StringIO(block), delimiter="\t", quotechar='"', doublequote=True), [])
    # A CRLF checkout would otherwise leave \r\n inside a quoted field, and no XML
    # ORIGINAL (where the XML parser normalises newlines) would ever match that key.
    return [field.replace("\r\n", "\n") for field in row]


def parse_bdd_block(block: str) -> tuple[str, str, str] | None:
    """Parse one record. None when it is not 3 columns or carries an unusable grup."""
    row = bdd_fields(block)
    if len(row) != 3:
        return None
    grup, original, traduit = row
    if not GRUP_RE.match(grup) or not original or not traduit:
        return None
    return grup, original, traduit


def iter_bdd_blocks(path: str = BDD_PATH):
    """Yield (parsed record or None, raw block) for every record, header excluded.

    ponytail: csv handles the quoted multi-line BOOK/INFO text that the old
    line-and-tab splitter threw away.
    """
    for position, block in enumerate(bdd_blocks(path)):
        if position == 0:
            if tuple(bdd_fields(block)) != BDD_HEADER:
                raise ValueError(f"bdd.tsv 表头不是 {BDD_HEADER}: {block[:60]!r}")
            continue
        yield parse_bdd_block(block), block


def load_bdd(path: str = BDD_PATH) -> dict[tuple[str, str], list[str]]:
    """(grup, original) -> unique traduit list, in file order."""
    index: dict[tuple[str, str], list[str]] = {}
    seen: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row, _ in iter_bdd_blocks(path):
        if row is None:
            continue
        grup, original, traduit = row
        key = (grup, original)
        if traduit in seen[key]:
            continue
        seen[key].add(traduit)
        index.setdefault(key, []).append(traduit)
    return index


def bdd_hits(index: dict[tuple[str, str], list[str]], grup: str, original: str) -> list[str]:
    return list(index.get((grup, original), ()))


def scan_bdd(path: str = BDD_PATH) -> dict[str, int]:
    """Summarize bdd.tsv: records, duplicates, ambiguous keys, multi-line records."""
    records = malformed = duplicates = multi_line = 0
    triples: set[tuple[str, str, str]] = set()
    variants: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row, block in iter_bdd_blocks(path):
        if row is None:
            malformed += 1
            continue
        records += 1
        if row in triples:
            duplicates += 1
        else:
            triples.add(row)
        variants[(row[0], row[1])].add(row[2])
        if block.count("\n") > 1:
            multi_line += 1
    ambiguous = sum(1 for values in variants.values() if len(values) > 1)
    return {
        "records": records,
        "malformed": malformed,
        "unique": len(triples),
        "duplicates": duplicates,
        "keys": len(variants),
        "ambiguous": ambiguous,
        "fillable": len(variants) - ambiguous,
        "multi_line": multi_line,
    }


def cmd_bdd(path: str = BDD_PATH, check: bool = False, normalize: bool = False) -> int:
    """Report bdd.tsv health, or drop exact duplicate records when --normalize is given."""
    summary = scan_bdd(path)
    print(f"记录 {summary['records']} | 唯一 {summary['unique']} | 重复 {summary['duplicates']}"
          f" | 畸形 {summary['malformed']}")
    print(
        f"键 {summary['keys']} | 可自动填充 {summary['fillable']} | 多义键 {summary['ambiguous']}"
        f" | 多行记录 {summary['multi_line']}"
    )
    if check:
        if summary["duplicates"] or summary["malformed"]:
            print("需要规范化：uv run dialogue_mod_translation/translate.py bdd --normalize")
            return 1
        return 0
    if not normalize:
        return 0
    if not summary["duplicates"]:
        print("无重复记录")
        return 0
    kept: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    dropped = 0
    for position, block in enumerate(bdd_blocks(path)):
        if position == 0:
            kept.append(block)
            continue
        row = parse_bdd_block(block)
        if row is None:
            kept.append(block)  # ponytail: keep what we cannot classify, --check reports it
        elif row in seen:
            dropped += 1
        else:
            seen.add(row)
            kept.append(block)
    with open(path, "wb") as handle:
        handle.write("".join(kept).encode("utf-8"))
    print(f"已删除 {dropped} 条重复记录（保留记录逐字节未变）")
    return 0


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


def rewrite_pending(xml: str, items: list[dict], groups: list[dict] | None = None) -> tuple[str, int]:
    """Rewrite already-translated records from pending.json. Returns (xml, count).

    `apply_pending` only fills STATUS 0 records; polishing existing wording needs
    this path, which overwrites STATUS 90 text in place.
    """
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
        text = None
        if item_key(rec) in grouped_targets.get(group_key(rec), set()):
            text = grouped_want[group_key(rec)]
        if not text:
            text = want.get(item_key(rec))
        if not text or rec["traduit"] == text:
            return block
        validate_translation(rec["original"], text)
        n += 1
        return set_status(set_traduit(block, text), DONE_STATUS)

    return ESP_RE.sub(repl, xml), n

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
    with open(old_path, encoding="utf-8") as f:
        old = json.load(f)
    prev = {item_key(it): it.get("traduit", "") for it in old.get("items", [])}
    prev_groups = {group_key(group): group.get("traduit", "") for group in old.get("groups", [])}
    for item in items:
        text = prev.get(item_key(item)) or prev_groups.get(group_key(item), "")
        if text and not item.get("traduit"):
            item["traduit"] = text

def cmd_pending(xml_path: str, grups: set[str], do_fill: bool, out_path: str) -> None:
    xml, has_bom = read_xml(xml_path)
    filled = 0
    if do_fill:
        index = load_bdd()
        xml, filled = fill_bdd(xml, index, grups)
        write_xml(xml_path, xml, has_bom)
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
    try:
        xml_ref = os.path.relpath(xml_path, ROOT)
    except ValueError:  # 不同盘符：relpath 无解，直接存绝对路径
        xml_ref = os.path.abspath(xml_path)
    payload = {
        "xml": xml_ref.replace("\\", "/"),
        "grups": sorted(grups),
        "items": items,
        "groups": grouped_items(items),
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    empty = sum(1 for it in items if not it["traduit"])
    group_empty = sum(1 for group in payload["groups"] if not group["traduit"])
    print(
        f"pending {len(items)} 条，去重为 {len(payload['groups'])} 组"
        f"（其中 {empty} 条 / {group_empty} 组无译文）-> {out_path}"
    )

def cmd_apply(pending_file: str) -> None:
    with open(pending_file, encoding="utf-8") as f:
        payload = json.load(f)
    xml_path = payload["xml"]
    if not os.path.isabs(xml_path):
        xml_path = os.path.join(ROOT, xml_path)
    xml, has_bom = read_xml(xml_path)
    xml, n = apply_pending(xml, payload.get("items", []), payload.get("groups", []))
    write_xml(xml_path, xml, has_bom)
    left = sum(1 for _, rec in pending_blocks(xml, set(payload.get("grups", DEFAULT_GRUPS))))
    print(f"写入 {n} 条 -> {xml_path}；剩余待译 {left}")


def cmd_rewrite(pending_file: str) -> None:
    """Overwrite already-translated records from pending.json (polishing pass)."""
    with open(pending_file, encoding="utf-8") as f:
        payload = json.load(f)
    xml_path = payload["xml"]
    if not os.path.isabs(xml_path):
        xml_path = os.path.join(ROOT, xml_path)
    xml, has_bom = read_xml(xml_path)
    xml, n = rewrite_pending(xml, payload.get("items", []), payload.get("groups", []))
    write_xml(xml_path, xml, has_bom)
    print(f"改写 {n} 条 -> {xml_path}")


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

    # rewrite 覆盖已译记录，apply 不碰；这是润色已译条目所需的路径。
    done = sample.replace("<TRADUIT />", "<TRADUIT>旧译</TRADUIT>").replace("<STATUS>0</STATUS>", "<STATUS>90</STATUS>")
    rewritten, n4 = rewrite_pending(done, pending)
    assert n4 == 1 and "<TRADUIT>你好&amp;我</TRADUIT>" in rewritten, rewritten
    unchanged, n5 = rewrite_pending(rewritten, pending)
    assert n5 == 0, "重复改写必须无变化"

    import tempfile

    for has_bom in (False, True):
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "t.xml")
            write_xml(target, sample, has_bom)
            text, seen_bom = read_xml(target)
            assert seen_bom is has_bom and text == sample

    # bdd.tsv 的字段可带引号并跨行；旧的逐行拆分会丢掉这些记录。
    with tempfile.TemporaryDirectory() as tmp:
        bdd = os.path.join(tmp, "bdd.tsv")
        with open(bdd, "w", encoding="utf-8", newline="") as handle:
            handle.write("grup\toriginal\ttraduit\n")
            handle.write('BOOK\t"line one\n\nline two"\t"段落一\n\n段落二"\n')
            handle.write("ACTI\tButton\t按钮\n")
            handle.write("ACTI\tButton\t按钮\n")
        index = load_bdd(bdd)
        assert index[("BOOK", "line one\n\nline two")] == ["段落一\n\n段落二"], index
        assert index[("ACTI", "Button")] == ["按钮"]
        summary = scan_bdd(bdd)
        assert summary == {
            "records": 3, "malformed": 0, "unique": 2, "duplicates": 1,
            "keys": 2, "ambiguous": 0, "fillable": 2, "multi_line": 1,
        }, summary
        with contextlib.redirect_stdout(io.StringIO()):
            assert cmd_bdd(bdd, check=True) == 1
            assert cmd_bdd(bdd, normalize=True) == 0
            assert cmd_bdd(bdd, check=True) == 0
        assert scan_bdd(bdd)["duplicates"] == 0
        with open(bdd, encoding="utf-8", newline="") as handle:
            assert handle.read().endswith("ACTI\tButton\t按钮\n")
        # CRLF checkout：键必须与 LF 一致，且规范化不得改写换行
        crlf = os.path.join(tmp, "crlf.tsv")
        sample_crlf = 'grup\toriginal\ttraduit\nBOOK\t"line one\n\nline two"\t"段落一\n\n段落二"\nACTI\tButton\t按钮\n'
        with open(crlf, "wb") as handle:
            handle.write(sample_crlf.replace("\n", "\r\n").encode("utf-8"))
        assert load_bdd(crlf) == {("BOOK", "line one\n\nline two"): ["段落一\n\n段落二"], ("ACTI", "Button"): ["按钮"]}
        with open(crlf, "rb") as handle:
            before = handle.read()
        with contextlib.redirect_stdout(io.StringIO()):
            assert cmd_bdd(crlf, normalize=True) == 0
        with open(crlf, "rb") as handle:
            assert handle.read() == before
    print("self-check OK")


def parse_grups(arg: str | None) -> set[str]:
    if not arg:
        return set(DEFAULT_GRUPS)
    return {g.strip() for g in arg.split(",") if g.strip()}


def main(argv: list[str]) -> None:
    _utf8_stdio()
    if "--self-check" in argv:
        _self_check()
        return
    if len(argv) >= 2 and argv[1] == "bdd":
        path = argv[argv.index("--bdd") + 1] if "--bdd" in argv else BDD_PATH
        sys.exit(cmd_bdd(path, check="--check" in argv, normalize="--normalize" in argv))
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
            stats(read_xml(path)[0], grups)
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
    if cmd == "rewrite":
        cmd_rewrite(argv[2])
        return
    if cmd == "fill-bdd":
        cmd_pending(argv[2], grups, do_fill=True, out_path=pending_path_for(argv[2]))
        return
    print(f"unknown command: {cmd}", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main(sys.argv)
