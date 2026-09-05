"""
从 BDD_LOYI_WL1.51.xml 中按 GRUP 类型提取翻译条目，供后续参考使用。

用法：
  uv run python extract_bdd.py [GRUP...]

示例：
  uv run python extract_bdd.py                                   # 提取所有配置好的类型
  uv run python extract_bdd.py ALCH NPC_                         # 只提取指定类型
  uv run python extract_bdd.py --count                            # 仅统计各类别数量
  uv run python extract_bdd.py --count --all                      # 统计所有类别数量
  uv run python extract_bdd.py --limit 50                         # 每类最多输出 50 条
"""

import json
import os
import sys
import xml.etree.ElementTree as ET

# ── 配置 ─────────────────────────────────────────────────────────────────────

BDD_XML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BDD_LOYI_WL1.51.xml")

# 默认提取的 GRUP 类型
DEFAULT_GRUPS = ["ALCH", "NPC_", "CELL", "LCTN", "KEYM", "MISC", "TREE", "WRLD", "INGR"]

# 输出文件
OUTPUT_FILE = "bdd_extracted.json"


# ── 解析 ──────────────────────────────────────────────────────────────────────


def extract_by_grups(xml_path: str, target_grups: set[str], limit: int = 0) -> dict[str, list[dict]]:
    """从 BDD XML 中按 GRUP 类型提取条目。

    返回 { grup_name: [{original, traduit, edid, id, champ}, ...] }
    """
    result: dict[str, list[dict]] = {g: [] for g in target_grups}

    print(f"正在解析 {xml_path} ...")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    print(f"共 {len(root):,} 条 BDD 条目")

    for entry in root:
        grup_el = entry.find("GRUP")
        if grup_el is None or grup_el.text not in target_grups:
            continue

        grup = grup_el.text
        if limit > 0 and len(result[grup]) >= limit:
            continue

        original = (entry.findtext("ORIGINAL", "") or "").strip()
        traduit = (entry.findtext("TRADUIT", "") or "").strip()
        if not original or not traduit:
            continue

        result[grup].append({
            "original": original,
            "traduit": traduit,
            "edid": (entry.findtext("EDID", "") or "").strip(),
            "id": (entry.findtext("ID", "") or "").strip(),
            "champ": (entry.findtext("CHAMP", "") or "").strip(),
        })

    return result


def count_all(xml_path: str) -> dict[str, int]:
    """统计所有 GRUP 类别的条目数。"""
    counts: dict[str, int] = {}
    tree = ET.parse(xml_path)
    for entry in tree.getroot():
        grup_el = entry.find("GRUP")
        if grup_el is None:
            continue
        g = grup_el.text or ""
        counts[g] = counts.get(g, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


# ── 输出 ──────────────────────────────────────────────────────────────────────


def print_summary(result: dict[str, list[dict]]):
    """打印提取摘要。"""
    total = 0
    print(f"\n{'GRUP':<8} {'条目数':<8} {'译文总字符':<10}")
    print("-" * 30)
    for grup, entries in sorted(result.items()):
        char_count = sum(len(e["traduit"]) for e in entries)
        total += len(entries)
        print(f"{grup:<8} {len(entries):<8} {char_count:<10}")
    print("-" * 30)
    print(f"{'合计':<8} {total:<8}")


def print_count_table(counts: dict[str, int]):
    """打印全类别统计表。"""
    total = sum(counts.values())
    print(f"\n{'GRUP':<8} {'条目数':<10} {'占比':<8}")
    print("-" * 30)
    for g, c in counts.items():
        pct = c / total * 100
        bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
        print(f"{g:<8} {c:<10} {pct:>5.1f}%")
    print("-" * 30)
    print(f"{'总计':<8} {total:<10}")


# ── 入口 ─────────────────────────────────────────────────────────────────────


def parse_args(argv: list[str]) -> tuple[set[str], bool, bool, int]:
    """解析命令行参数，返回 (target_grups, do_count, do_all, limit)"""
    grups: set[str] = set()
    do_count = False
    do_all = False
    limit = 0

    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--count":
            do_count = True
        elif a == "--all":
            do_all = True
        elif a == "--limit" and i + 1 < len(argv):
            i += 1
            limit = int(argv[i])
        elif a.startswith("--limit="):
            limit = int(a.split("=", 1)[1])
        elif a.startswith("--"):
            pass  # 忽略其他未知标志
        else:
            # 只有大写字母构成的 GRUP 类型才算
            if a.isupper() or a.endswith("_") or all(c.isupper() or c.isdigit() for c in a):
                grups.add(a)
        i += 1

    if not grups:
        grups = set(DEFAULT_GRUPS)

    return grups, do_count, do_all, limit


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    xml_path = BDD_XML

    if not os.path.exists(xml_path):
        print(f"[错误] 找不到 BDD XML: {xml_path}", file=sys.stderr)
        sys.exit(1)

    # 解析参数
    target_grups, do_count, do_all, limit = parse_args(sys.argv)

    if do_count:
        counts = count_all(xml_path)
        if do_all:
            print_count_table(counts)
        else:
            total = 0
            print(f"{'GRUP':<8} {'条目数':<10}")
            print("-" * 20)
            for g in sorted(target_grups):
                c = counts.get(g, 0)
                total += c
                print(f"{g:<8} {c:<10}")
            print("-" * 20)
            print(f"{'合计':<8} {total:<10}")
        return

    print(f"目标 GRUP: {', '.join(sorted(target_grups))}")
    if limit > 0:
        print(f"每类上限: {limit} 条")

    result = extract_by_grups(xml_path, target_grups, limit)

    print_summary(result)

    # 输出 JSON
    out_path = os.path.join(script_dir, OUTPUT_FILE)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n已保存 -> {out_path}")


if __name__ == "__main__":
    main()
