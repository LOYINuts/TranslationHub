"""
统一构建脚本：批量生成所有模组的中文翻译文件。

用法：
  uv run python build_all.py          # 构建所有模组
  uv run python build_all.py --stats   # 仅统计，不生成
  uv run python build_all.py FLICK/FUCK FLICK/KillFeed  # 只构建指定模组

数据驱动：每个模组的翻译数据存放在 {mod_dir}/translations.json，
构建配置见下方 MOD_CONFIGS 列表。

支持三种模组类型：
  1. line-based：按行替换（制表符/等号分隔的 .txt/.ini）
  2. json-based：flat JSON 键值替换（.json）
  3. script-based：运行模组目录下的独立脚本（如 IED 的 JSON→JSON 转换）
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional

from locale_utils import (
    read_lines,
    write_utf16le_bom,
    write_utf8_bom,
    write_utf8,
    rebuild_tab_lines_with_translation,
)


# Force UTF-8 for stdout (avoid GBK encoding errors on Windows console)
if hasattr(sys.stdout, 'buffer'):
    import io
    # 已是 UTF-8 时不再重复包装，避免包装对象被 GC 时关闭底层 buffer
    if not (isinstance(sys.stdout, io.TextIOWrapper) and (sys.stdout.encoding or '').lower() == 'utf-8'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# ── 模组构建配置 ─────────────────────────────────────────────────────────────


@dataclass
class ModConfig:
    """单个模组的构建配置。

    dir:            模组目录名（相对于项目根目录）
    source:         源文件名（英文）
    output:         输出文件名（中文）
    sep:            行分隔符。'\t' 制表符, ' = ' 等号, None=任意空白
    encoding:       输出编码: 'utf16-le-bom', 'utf-8', 'utf-8-bom'
    output_sep:     输出分隔符（默认与 sep 相同）。用于 sep≠output_sep 的特殊情况
    """

    dir: str
    source: str
    output: str
    sep: Optional[str] = "\t"
    encoding: str = "utf16-le-bom"
    output_sep: Optional[str] = None

    def __post_init__(self):
        if self.output_sep is None:
            self.output_sep = self.sep if self.sep is not None else "\t"


# 所有可构建的模组
MOD_CONFIGS: list[ModConfig] = [
    # ── 制表符分隔 + UTF-16 LE BOM ──
    ModConfig("FLICK/FUCK", "FUCK_ENGLISH.txt", "FUCK_CHINESE.txt"),
    ModConfig("skyprompt", "SkyPrompt_ENGLISH.txt", "SkyPrompt_CHINESE.txt"),
    ModConfig("ostim", "OStim_ENGLISH.txt", "OStim_CHINESE.txt"),
    ModConfig("FLICK/FUCKQTY", "FUCK-QTY_ENGLISH.txt", "FUCK-QTY_CHINESE.txt"),
    ModConfig("FLICK/FUCKRACE", "FUCK-RACE_ENGLISH.txt", "FUCK-RACE_CHINESE.txt"),
    ModConfig("FLICK/KillFeed", "KillFeed_ENGLISH.txt", "KillFeed_CHINESE.txt"),
    ModConfig("feetofskyrim", "FeetOfSkyrim_ENGLISH.txt", "FeetOfSkyrim_CHINESE.txt"),
    ModConfig("FLICK/fittingroom", "Fitting Room_ENGLISH.txt", "Fitting Room_CHINESE.txt"),
    ModConfig("morehud", "ahzmorehud_english.txt", "ahzmorehud_chinese.txt"),
    # ── 等号分隔 + UTF-8 ──
    ModConfig(
        "Press F To Pay Respects",
        "PressFtoPayRespects_Translation.ini",
        "PressFtoPayRespects_Translation_zh.ini",
        sep="=",
        encoding="utf-8",
    ),
    ModConfig(
        "RealTimeNPCStatScaler",
        "RealTimeNPCStatScaler_Translation.ini",
        "RealTimeNPCStatScaler_Translation_zh.ini",
        sep=" = ",
        encoding="utf-8",
    ),
    ModConfig(
        "PartySheet",
        "PartySheet_en.txt",
        "PartySheet_zh.txt",
        sep="=",
        encoding="utf-8",
    ),
    ModConfig(
        "consolecommander",
        "ConsoleCommander_Translation.txt",
        "ConsoleCommander_Translation_zh.txt",
        sep=" = ",
        encoding="utf-8",
    ),
    # ── 等号分隔 + UTF-8 BOM ──
    ModConfig(
        "pickupradius",
        "PickUpRadiusSKSE_Translation.ini",
        "PickUpRadiusSKSE_Translation_zh.ini",
        sep=" = ",
        encoding="utf-8",
    ),
    # ── 空白分隔（3 空格）→ 制表符输出 ──
    ModConfig(
        "FLICK/speedofstrolling",
        "styyx-move-speed_ENGLISH.txt",
        "styyx-move-speed_CHINESE.txt",
        sep=None,  # 按任意空白拆分
        output_sep="\t",
        encoding="utf16-le-bom",
    ),
]


# ── 写入器映射 ───────────────────────────────────────────────────────────────

WRITERS = {
    "utf16-le-bom": write_utf16le_bom,
    "utf-8-bom": write_utf8_bom,
    "utf-8": write_utf8,
}


# ── 脚本型模组配置 ─────────────────────────────────────────────────────────────


# ── JSON 型模组配置 ───────────────────────────────────────────────────────────


@dataclass
class ModJson:
    """flat JSON 文件，源和目标均为 JSON 键值对。"""

    dir: str
    source: str
    output: str = ""

    def __post_init__(self):
        if not self.output:
            # 自动生成 _zh.json 文件名
            base, ext = os.path.splitext(self.source)
            self.output = f"{base}_zh{ext}"


JSON_MODS: list[ModJson] = [
    ModJson("SKSE Menu Framework", "SKSEMenuFrameworkStrings.json"),
    ModJson("MCMMemory", "Translation.json"),

    ModJson("Risas All In One Menu/RisaAllInOneMenu", "en.json", "zh-cn.json"),
    ModJson("Risas All In One Menu/RisaUI", "en.json", "zh-cn.json"),
    ModJson("swiftpotionng", "SwiftPotionNG_Translation.json"),
    ModJson("Viny Mods/timecontrol", "Language.json", "Language_zh.json"),
    ModJson("Viny Mods/timeisticking", "en.json", "zh.json"),
    ModJson("Viny Mods/Input Manager", "Language.json", "Language_zh.json"),
    ModJson("Viny Mods/DMK", "Language.json", "Language_zh.json"),
    ModJson("Viny Mods/NPC Visual Editor - NVE", "Language.json", "Language_zh.json"),
    ModJson("Viny Mods/NPC Stats Editor", "Language.json", "Language_zh.json"),
    ModJson("Viny Mods/NPC Senses", "Language.json", "Language_zh.json"),
    ModJson("Viny Mods/DFG", "Language.json", "Language_zh.json"),
    ModJson("Viny Mods/Parryall", "Language.json", "Language_zh.json"),
    ModJson("Viny Mods/EDF", "Language.json", "Language_zh.json"),
    ModJson("Viny Mods/quickcommands", "Language.json", "Language_zh.json"),
]


# ── 脚本型模组配置 ─────────────────────────────────────────────────────────────


@dataclass
class ModScript:
    """需要运行独立脚本的模组（如 IED 的 JSON→JSON 转换）。"""

    dir: str
    script: str = "generate_zh.py"


SCRIPT_MODS: list[ModScript] = [
    ModScript("Viny Mods/Dodgeall"),
]


def count_leaves(d):
    """递归统计翻译条目数：嵌套 JSON 按叶子计数。"""
    return sum(count_leaves(v) if isinstance(v, dict) else 1 for v in d.values())


# ── 构建函数 ──────────────────────────────────────────────────────────────────


def _split_line(line: str, sep: Optional[str] = None) -> tuple[Optional[str], str]:
    """按分隔符拆分一行，返回 (key, value)。sep=None 按任意空白拆分。"""
    stripped = line.strip("\r\n")
    if not stripped:
        return None, stripped
    if sep is None:
        parts = stripped.split(None, 1)
        if len(parts) < 2:
            return None, stripped
        return parts[0], parts[1]
    else:
        if sep not in stripped:
            return None, stripped
        return stripped.split(sep, 1)


def build_one(cfg: ModConfig, root_dir: str) -> int:
    """构建单个模组，返回翻译条目数。"""
    mod_path = os.path.join(root_dir, cfg.dir)

    # 读取 translations.json
    trans_path = os.path.join(mod_path, "translations.json")
    if not os.path.exists(trans_path):
        print(f"  [跳过] 未找到 {trans_path}")
        return 0

    with open(trans_path, "r", encoding="utf-8") as f:
        translations = json.load(f)

    # 读取源文件
    src_path = os.path.join(mod_path, cfg.source)
    if not os.path.exists(src_path):
        print(f"  [跳过] 未找到源文件 {src_path}")
        return 0

    lines = read_lines(src_path)
    out_lines = []
    current_section = ""

    for line in lines:
        # 跟踪章节头 [Section]
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1]
            out_lines.append(line)
            continue
        if stripped.startswith(";"):
            out_lines.append(line)
            continue

        key, val = _split_line(line, cfg.sep)
        if key is not None:
            lookup = key
            if current_section:
                # key 可能已含节名前缀（如 AI 节内 AI.Aggression.Aggressive），避免重复
                if not key.startswith(f"{current_section}."):
                    prefixed = f"{current_section}.{key}"
                    if prefixed in translations:
                        lookup = prefixed
            if lookup in translations:
                out_lines.append(f"{key}{cfg.output_sep}{translations[lookup]}")
                continue
        out_lines.append(line)

    # 写入输出文件
    content = "\r\n".join(out_lines) + "\r\n"
    out_path = os.path.join(mod_path, cfg.output)
    writer = WRITERS.get(cfg.encoding)
    if writer is None:
        print(f"  [错误] 未知编码: {cfg.encoding}")
        return 0
    writer(out_path, content)

    print(f"  [OK] {cfg.dir}: {len(translations)} 条 -> {cfg.output}")
    return len(translations)


def build_json_one(jcfg: ModJson, root_dir: str) -> int:
    """构建 flat JSON 模组，返回翻译条目数。

    按行读取源 JSON，只替换翻译的值，保留原格式（空行、缩进、逗号等）。
    """
    import re

    mod_path = os.path.join(root_dir, jcfg.dir)

    # 读取 translations.json
    trans_path = os.path.join(mod_path, "translations.json")
    if not os.path.exists(trans_path):
        print(f"  [跳过] 未找到 {trans_path}")
        return 0

    with open(trans_path, "r", encoding="utf-8") as f:
        translations = json.load(f)

    # 按行读取源 JSON，保留原格式
    src_path = os.path.join(mod_path, jcfg.source)
    if not os.path.exists(src_path):
        print(f"  [跳过] 未找到源文件 {src_path}")
        return 0

    with open(src_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 逐行替换值
    # 匹配 "key": "value" 或 "key": "value", 格式
    kv_pattern = re.compile(
        r'^(\s*"(?:[^"\\]|\\.)*"\s*:\s*)"(?:[^"\\]|\\.)*"(\s*,?\s*)$'
    )

    out_lines = []
    # 跟踪 translations.json 的嵌套层级
    # trans_scope[-1] 是当前层级的翻译字典
    trans_scope: list[dict | None] = [translations]

    for line in lines:
        # 匹配 "key": { 模式 → 嵌套对象，进入子层级
        nest_match = re.match(r'\s*"([^"]+)"\s*:\s*\{', line)
        if nest_match:
            k = nest_match.group(1)
            child = trans_scope[-1].get(k) if isinstance(trans_scope[-1], dict) else None
            trans_scope.append(child if isinstance(child, dict) else None)
            out_lines.append(line)
            continue

        m = kv_pattern.match(line)
        if m and isinstance(trans_scope[-1], dict):
            prefix = m.group(1)
            suffix = m.group(2)
            key_match = re.match(r'\s*"([^"]+)"\s*:\s*', prefix)
            if key_match:
                k = key_match.group(1)
                if k in trans_scope[-1]:
                    new_val = json.dumps(trans_scope[-1][k], ensure_ascii=False)
                    out_lines.append(f"{prefix}{new_val}{suffix}")
                    continue

        # 独立的 } 或 }, → 退出嵌套
        if line.strip().rstrip(',') == '}':
            if len(trans_scope) > 1:
                trans_scope.pop()

        out_lines.append(line)

    # 写入输出
    out_path = os.path.join(mod_path, jcfg.output)
    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(out_lines)

    print(f"  [OK] {jcfg.dir}: {count_leaves(translations)} 条 -> {jcfg.output}")
    return count_leaves(translations)


def build_script_one(smod: ModScript, root_dir: str) -> int:
    """运行脚本型模组的生成脚本，返回翻译条目数。"""
    mod_path = os.path.join(root_dir, smod.dir)
    script_path = os.path.join(mod_path, smod.script)
    if not os.path.exists(script_path):
        print(f"  [跳过] 未找到脚本 {script_path}")
        return 0

    result = subprocess.run(
        [sys.executable, script_path],
        cwd=mod_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  [错误] {smod.dir}: {result.stderr.strip()}")
        return 0

    print(f"  [OK] {smod.dir}: {result.stdout.strip()}")
    # 从脚本输出解析条目数
    for line in result.stdout.splitlines():
        if "总计:" in line:
            try:
                return int(line.split(":")[1].strip())
            except (ValueError, IndexError):
                pass
    return 0


def build_all(root_dir: str, filters: Optional[set[str]] = None) -> int:
    """构建所有（或指定）模组，返回总翻译条目数。"""
    total = 0
    for cfg in MOD_CONFIGS:
        if filters and cfg.dir not in filters:
            continue
        total += build_one(cfg, root_dir)
    for jcfg in JSON_MODS:
        if filters and jcfg.dir not in filters:
            continue
        total += build_json_one(jcfg, root_dir)
    for smod in SCRIPT_MODS:
        if filters and smod.dir not in filters:
            continue
        total += build_script_one(smod, root_dir)
    return total


def display_width(s: str) -> int:
    """终端显示宽度：CJK 字符占 2 格。"""
    return sum(2 if ord(ch) > 0x2E7F else 1 for ch in s)


def pad_cjk(s: str, width: int) -> str:
    """按显示宽度右补空格对齐。"""
    return s + " " * max(0, width - display_width(s))


def _load_translation_count(path: str) -> Optional[int]:
    """读取 translations.json 并统计条目数（嵌套 JSON 按叶子计数）。"""
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return count_leaves(json.load(f))


def show_stats(root_dir: str):
    """统计各模组翻译数据"""
    print(f"{pad_cjk('模组', 26)}{pad_cjk('条目数', 8)} 类型")
    print("-" * 46)
    total = 0
    for cfg in MOD_CONFIGS:
        count = _load_translation_count(os.path.join(root_dir, cfg.dir, "translations.json"))
        if count is not None:
            total += count
            print(f"{pad_cjk(cfg.dir, 26)}{count:<8} line")
        else:
            print(f"{pad_cjk(cfg.dir, 26)}{'-':<8} MISS")
    for jcfg in JSON_MODS:
        count = _load_translation_count(os.path.join(root_dir, jcfg.dir, "translations.json"))
        if count is not None:
            total += count
            print(f"{pad_cjk(jcfg.dir, 26)}{count:<8} json")
        else:
            print(f"{pad_cjk(jcfg.dir, 26)}{'-':<8} MISS")
    for smod in SCRIPT_MODS:
        count = _load_translation_count(os.path.join(root_dir, smod.dir, "translations.json"))
        if count is not None:
            total += count
            print(f"{pad_cjk(smod.dir, 26)}{count:<8} script")
        else:
            print(f"{pad_cjk(smod.dir, 26)}{'-':<8} MISS")
    print("-" * 46)
    print(f"{pad_cjk('总计', 26)}{total:<8}")


# ── 入口 ─────────────────────────────────────────────────────────────────────


def main():
    root = os.path.dirname(os.path.abspath(__file__))

    if "--stats" in sys.argv:
        show_stats(root)
        return

    filters: Optional[set[str]] = None
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        filters = set(args)

    total = build_all(root, filters)
    print(f"\n完成，共 {total} 条翻译已生成")


if __name__ == "__main__":
    main()
