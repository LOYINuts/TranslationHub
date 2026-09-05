"""
本地化文件处理工具函数。

提供 BOM 自动检测、UTF-16 LE/BE/8 读写、制表符分割行解析等
在多个翻译脚本中重复出现的功能。
"""

import json
import os

# ── BOM 常量 ──────────────────────────────────────────────────────────────────
BOM_UTF16_LE = b"\xff\xfe"
BOM_UTF16_BE = b"\xfe\xff"
BOM_UTF8 = b"\xef\xbb\xbf"


# ── 读取 ──────────────────────────────────────────────────────────────────────


def read_text(path: str) -> str:
    """自动检测 BOM/编码并读取文本文件。

    检测顺序：UTF-16 LE → UTF-16 BE → UTF-8（含 BOM）。
    始终去除 \ufeff（BOM 字符）。
    """
    raw = open(path, "rb").read()
    if raw[:2] == BOM_UTF16_LE:
        text = raw.decode("utf-16-le")
    elif raw[:2] == BOM_UTF16_BE:
        text = raw.decode("utf-16-be")
    else:
        text = raw.decode("utf-8-sig")
    return text.lstrip("\ufeff")


def read_lines(path: str) -> list[str]:
    """读取文本文件并返回行列表（去除换行符）。"""
    return read_text(path).splitlines()


# ── 写入 ──────────────────────────────────────────────────────────────────────


def write_utf16le_bom(path: str, content: str) -> None:
    """以 UTF-16 LE BOM 格式写入文件。"""
    with open(path, "wb") as f:
        f.write(BOM_UTF16_LE + content.encode("utf-16-le"))


def write_utf8_bom(path: str, content: str) -> None:
    """以 UTF-8 BOM（\xef\xbb\xbf）格式写入文件。"""
    with open(path, "wb") as f:
        f.write(BOM_UTF8 + content.encode("utf-8"))


def write_utf8(path: str, content: str) -> None:
    """以纯 UTF-8 格式写入文件（无 BOM）。"""
    with open(path, "wb") as f:
        f.write(content.encode("utf-8"))


# ── 制表符分割行处理 ─────────────────────────────────────────────────────────


def parse_tab_lines(lines: list[str]) -> list[tuple[str, str]]:
    """从制表符分割的行中提取 (key, value) 对。

    跳过不含制表符的行。
    """
    pairs: list[tuple[str, str]] = []
    for line in lines:
        stripped = line.strip("\r\n")
        if "\t" not in stripped:
            continue
        key, val = stripped.split("\t", 1)
        pairs.append((key, val))
    return pairs


def rebuild_tab_lines_with_translation(
    lines: list[str],
    translation_map: dict[str, str],
    keep_unmatched: bool = True,
    sep: str = "\t",
) -> list[str]:
    """逐行替换制表符分割文件中的翻译。

    lines:             原始行列表
    translation_map:   key → 翻译文本
    keep_unmatched:    未匹配的 key 是否保留原值（否则保留空值）
    sep:               分隔符，默认为制表符

    返回：处理后的行列表（不含尾部换行符）。
    """
    out: list[str] = []
    for line in lines:
        stripped = line.strip("\r\n")
        if sep not in stripped:
            out.append(stripped)
            continue
        key, val = stripped.split(sep, 1)
        if key in translation_map:
            out.append(f"{key}{sep}{translation_map[key]}")
        elif keep_unmatched:
            out.append(stripped)
        else:
            out.append(f"{key}{sep}")
    return out


# ── 等号分隔行处理（INI 风格） ────────────────────────────────────────────────


def parse_eq_lines(
    lines: list[str], sep: str = " = "
) -> list[tuple[str, str]]:
    """从等号分割的行中提取 (key, value) 对。

    跳过不含等号的行。
    """
    pairs: list[tuple[str, str]] = []
    for line in lines:
        stripped = line.strip("\r\n")
        if sep not in stripped:
            continue
        key, val = stripped.split(sep, 1)
        pairs.append((key, val))
    return pairs


def rebuild_eq_lines_with_translation(
    lines: list[str],
    translation_map: dict[str, str],
    sep: str = " = ",
) -> list[str]:
    """逐行替换等号分割文件中的翻译。

    已合并到 rebuild_tab_lines_with_translation，此函数仅为向后兼容的别名。
    """
    return rebuild_tab_lines_with_translation(lines, translation_map, keep_unmatched=True, sep=sep)


# ── JSON 键完整性检查 ─────────────────────────────────────────────────────────


def check_json_keys(english_path: str, chinese_path: str) -> dict:
    """检查中英文 JSON 文件键是否一致。

    返回：
        {
            "en_count": int,
            "zh_count": int,
            "missing": list[str],   # 英文有但中文缺的
            "extra": list[str],     # 中文多出来的
            "match": bool
        }
    """
    with open(english_path, "r", encoding="utf-8") as f:
        en = json.load(f)
    with open(chinese_path, "r", encoding="utf-8") as f:
        zh = json.load(f)

    def _flat_keys(d: dict, prefix: str = "") -> list[str]:
        keys: list[str] = []
        for k, v in d.items():
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.extend(_flat_keys(v, key))
            else:
                keys.append(key)
        return keys

    en_keys = set(_flat_keys(en))
    zh_keys = set(_flat_keys(zh))

    missing = sorted(en_keys - zh_keys)
    extra = sorted(zh_keys - en_keys)

    return {
        "en_count": len(en_keys),
        "zh_count": len(zh_keys),
        "missing": missing,
        "extra": extra,
        "match": not missing and not extra,
    }
