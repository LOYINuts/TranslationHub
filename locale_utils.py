"""
本地化文件处理工具函数。

提供 BOM 自动检测、UTF-16 LE/BE/8 读写、制表符分割行解析等
在多个翻译脚本中重复出现的功能。
"""

import json
from collections import Counter
import re
import os

import sys
from typing import Optional
# ── BOM 常量 ──────────────────────────────────────────────────────────────────
BOM_UTF16_LE = b"\xff\xfe"
BOM_UTF16_BE = b"\xfe\xff"
BOM_UTF8 = b"\xef\xbb\xbf"


# ── UTF-8 强制 ────────────────────────────────────────────────────────────────


def force_utf8_stdout() -> None:
    """Force stdout/stderr to UTF-8. ponytail: one helper, all CLIs use it."""
    import io
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name)
        if hasattr(stream, "buffer") and (stream.encoding or "").lower() != "utf-8":
            setattr(sys, name, io.TextIOWrapper(stream.buffer, encoding="utf-8"))
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


def split_line(line: str, sep: Optional[str] = "\t") -> tuple[Optional[str], str]:
    """按分隔符拆分一行，返回 (key, value)。
    
    sep=None 按任意空白拆分。不含分隔符的行返回 (None, line)。
    """
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


def resolve_key_with_section(key: str, current_section: str, translations: dict[str, str]) -> Optional[str]:
    """尝试在翻译字典中解析键（支持节前缀 fallback）。
    
    优先级：
    1. 完整键（key 本身）
    2. 带节前缀（section.key）
    3. 裸键（去掉节前缀后的部分）
    
    返回找到的键名，或 None。
    """
    # 直接匹配
    if key in translations:
        return key
    
    # 尝试添加节前缀
    if current_section and not key.startswith(f"{current_section}."):
        prefixed = f"{current_section}.{key}"
        if prefixed in translations:
            return prefixed
    
    # 尝试去掉节前缀
    if "." in key:
        bare = key.split(".", 1)[1]
        if bare in translations:
            return bare
    
    return None


_PRINTF_TOKEN_RE = re.compile(
    r"%(?:\d+\$)?[-+#0']*\d*(?:\.\d+)?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
_QT_TOKEN_RE = re.compile(r"%(?:L)?[1-9]\d*")
_BRACE_TOKEN_RE = re.compile(r"\{[^{}\r\n]*\}")
_DOLLAR_TOKEN_RE = re.compile(r"\$[A-Za-z_][A-Za-z0-9_]*\$")
_MARKUP_TOKEN_RE = re.compile(r"</?([A-Za-z][\w:-]*)(?:\s+[^<>]*)?>")
_BRACKET_TAG_RE = re.compile(r"\[/?(?:br|pagebreak)\]", re.IGNORECASE)


def format_tokens(text: str) -> list[str]:
    """Extract placeholders and real paired/attributed markup tags."""
    tokens: list[str] = []
    for regex in (_PRINTF_TOKEN_RE, _QT_TOKEN_RE, _BRACE_TOKEN_RE, _DOLLAR_TOKEN_RE):
        tokens.extend(regex.findall(text))
    tokens.extend(_BRACKET_TAG_RE.findall(text))

    markup = list(_MARKUP_TOKEN_RE.finditer(text))
    closing_names = {m.group(1).lower() for m in markup if m.group(0).startswith("</")}
    for match in markup:
        token = match.group(0)
        name = match.group(1).lower()
        if token.startswith("</") or name in closing_names or "=" in token:
            tokens.append(token)
    return tokens


def translation_format_issues(source: str, translated: str, line_based: bool = False) -> list[str]:
    """Return format-preservation errors for one translated value."""
    issues: list[str] = []
    if line_based:
        if "\n" in translated:
            issues.append("real newline")
        if r"\n" in source and r"\n" not in translated:
            issues.append("missing \\n escape")
    if Counter(format_tokens(source)) != Counter(format_tokens(translated)):
        issues.append("placeholder or tag mismatch")
    return issues


def load_json(path: str):
    """Load JSON and tolerate // or /* */ comments used by mod sources."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    out = []
    i = 0
    in_string = False
    escaped = False
    block_comment = False
    line_comment = False
    while i < len(text):
        char = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if line_comment:
            if char == "\n":
                line_comment = False
                out.append(char)
            i += 1
            continue
        if block_comment:
            if char == "*" and nxt == "/":
                block_comment = False
                i += 2
            else:
                i += 1
            continue
        if in_string:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            i += 1
            continue
        if char == '"':
            in_string = True
            out.append(char)
        elif char == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue
        elif char == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue
        else:
            out.append(char)
        i += 1
    return json.loads("".join(out))


def detect_encoding(path: str) -> str:
    """BOM sniff. utf16-le-bom | utf16-be-bom | utf-8-bom | utf-8."""
    with open(path, "rb") as f:
        raw = f.read(4)
    if raw.startswith(BOM_UTF16_LE):
        return "utf16-le-bom"
    if raw.startswith(BOM_UTF16_BE):
        return "utf16-be-bom"
    if raw.startswith(BOM_UTF8):
        return "utf-8-bom"
    return "utf-8"



def _self_check() -> None:
    import tempfile

    dir_ = tempfile.mkdtemp()
    path = os.path.join(dir_, "t.txt")
    write_utf16le_bom(path, "k\tv\r\n")
    assert detect_encoding(path) == "utf16-le-bom"
    assert read_text(path) == "k\tv\r\n"
    assert read_lines(path) == ["k\tv"]
    assert translation_format_issues(r"a\n", r"中\n", line_based=True) == []
    assert translation_format_issues(r"a\n", "中\n", line_based=True) == ["real newline", "missing \\n escape"]
    assert translation_format_issues("%llu %zu %1 {name}", "%llu %zu %1 {name}") == []
    assert translation_format_issues("<Select Type>", "<选择类型>") == []
    assert translation_format_issues("<font color='red'>x</font>", "<font color='red'>中</font>") == []
    assert translation_format_issues("a[br]b", "甲[br]乙") == []
    assert translation_format_issues("a[br]b", "甲乙") == ["placeholder or tag mismatch"]
    print("ok")


def main(argv: list[str] | None = None) -> int:
    import sys

    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print("usage: python locale_utils.py detect PATH")
        print("       python locale_utils.py dump PATH [-o OUT.txt]")
        print("       python locale_utils.py --self-check")
        return 0
    if args[0] == "--self-check":
        _self_check()
        return 0
    cmd, *rest = args
    if cmd == "detect" and len(rest) == 1:
        force_utf8_stdout()
        print(detect_encoding(rest[0]))
        return 0
    if cmd == "dump" and rest:
        path = rest[0]
        out = None
        if len(rest) == 3 and rest[1] == "-o":
            out = rest[2]
        elif len(rest) != 1:
            print("usage: python locale_utils.py dump PATH [-o OUT.txt]")
            return 2
        text = read_text(path)
        if out:
            write_utf8(out, text)
            return 0
        force_utf8_stdout()
        import sys

        sys.stdout.write(text)
        if text and not text.endswith("\n"):
            sys.stdout.write("\n")
        return 0
    print("usage: python locale_utils.py detect|dump PATH")
    return 2


if __name__ == "__main__":
    import sys

    raise SystemExit(main())
