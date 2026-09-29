"""
统一构建脚本：批量生成所有模组的中文翻译文件。

用法：
  uv run python build_all.py          # 构建所有模组
  uv run python build_all.py --stats   # 仅统计，不生成
  uv run python build_all.py FUCK KillFeed  # 短名或完整相对路径均可

数据驱动：翻译源位于各模组的 translations.json，构建配置位于 mods.toml。
数据源统一为各模组的 `translations.json`，配置统一放在 `mods.toml`。
支持 `line`、`json` 和单一共享的 `qt` 处理器。
"""

import json
import xml.etree.ElementTree as ET
import os
import glob
from typing import Optional

import logging
import argparse
from locale_utils import (
    read_lines,
    read_text,
    write_utf16le_bom,
    write_utf8_bom,
    write_utf8,
    split_line,
    resolve_key_with_section,
    load_json,
    translation_format_issues,
)

from config import setup_cli_logging
setup_cli_logging()  # ponytail: single logging setup, stdout stays UTF-8

# ── 模组构建配置 ─────────────────────────────────────────────────────────────


from config import ModConfig, ModJson, ModQt, load_repo_configs, matches_filter

# 模组配置从 mods.toml 加载，这些全局变量在 main() 中赋值
MOD_CONFIGS: list[ModConfig] = []
JSON_MODS: list = []
QT_MODS: list[ModQt] = []

# 写入器映射
WRITERS = {
    "utf16-le-bom": write_utf16le_bom,
    "utf-8-bom": write_utf8_bom,
    "utf-8": write_utf8,
}

def count_leaves(value):
    """统计嵌套字典和列表中的翻译值。"""
    if isinstance(value, dict):
        return sum(count_leaves(item) for item in value.values())
    if isinstance(value, list):
        return sum(count_leaves(item) for item in value)
    return 1


# ── 构建函数 ──────────────────────────────────────────────────────────────────



def render_line_one(cfg: ModConfig, root_dir: str) -> tuple[str, int]:
    """Render one line-based mod without writing its output file."""
    mod_path = os.path.join(root_dir, cfg.dir)
    trans_path = os.path.join(mod_path, "translations.json")
    src_path = os.path.join(mod_path, cfg.source)
    if not os.path.exists(trans_path):
        raise FileNotFoundError(f"未找到翻译源: {trans_path}")
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"未找到源文件: {src_path}")

    translations = load_json(trans_path)
    lines = read_lines(src_path)
    out_lines = []
    current_section = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1]
            out_lines.append(line)
            continue
        if stripped.startswith(";"):
            out_lines.append(line)
            continue

        key, value = split_line(line, cfg.sep)
        if key is not None:
            lookup_key = key.strip()
            resolved = resolve_key_with_section(lookup_key, current_section, translations)
            if resolved:
                translated = translations[resolved]
                format_issues = translation_format_issues(value, translated, line_based=True)
                if format_issues:
                    raise ValueError(f"{cfg.dir} {lookup_key}: {'; '.join(format_issues)}")
                out_lines.append(f"{key}{cfg.output_sep}{translated}")
                continue
        out_lines.append(line)
    return "\r\n".join(out_lines) + "\r\n", len(translations)

def render_line_group(cfg: ModConfig, root_dir: str) -> tuple[list[tuple[str, str]], int]:
    """Render a configured line-file glob with file-scoped translation keys."""
    mod_path = os.path.join(root_dir, cfg.dir)
    trans_path = os.path.join(mod_path, "translations.json")
    translations = load_json(trans_path)
    output_root = os.path.join(mod_path, cfg.output)
    source_paths = sorted(glob.glob(os.path.join(mod_path, cfg.source), recursive=True))
    source_paths = [
        path for path in source_paths
        if os.path.isfile(path)
        and os.path.commonpath([os.path.abspath(output_root), os.path.abspath(path)])
        != os.path.abspath(output_root)
    ]
    if not source_paths:
        raise FileNotFoundError(f"No files match: {os.path.join(mod_path, cfg.source)}")
    artifacts = []
    used = set()
    count = 0
    for source_path in source_paths:
        relative = os.path.relpath(source_path, mod_path).replace(os.sep, "/")
        occurrences = {}
        output_lines = []
        for line in read_lines(source_path):
            if not line or (line.startswith("#") and cfg.sep not in line) or cfg.sep not in line:
                output_lines.append(line)
                continue
            fields = line.split(cfg.sep)
            if cfg.value_field >= len(fields):
                raise ValueError(f"Missing field {cfg.value_field}: {relative}")
            key = fields[0].strip()
            index = occurrences.get(key, 0)
            occurrences[key] = index + 1
            lookup = f"{relative}::{key}#{index}"
            if lookup not in translations:
                raise ValueError(f"Missing translation: {lookup}")
            translated = translations[lookup]
            issues = translation_format_issues(fields[cfg.value_field], translated, line_based=True)
            if issues:
                raise ValueError(f"{lookup}: {'; '.join(issues)}")
            fields[cfg.value_field] = translated
            if cfg.trim_trailing_fields:
                fields[cfg.value_field + 1:] = [field.rstrip() for field in fields[cfg.value_field + 1:]]
            output_lines.append(cfg.sep.join(fields))
            used.add(lookup)
            count += 1
        artifacts.append((os.path.join(output_root, relative), "\r\n".join(output_lines) + "\r\n"))
    extra = set(translations) - used
    if extra:
        raise ValueError(f"Unused scoped translation keys: {sorted(extra)[:10]}")
    return artifacts, count



def build_one(cfg: ModConfig, root_dir: str) -> int:
    """Build one configured line task."""
    writer = WRITERS.get(cfg.encoding)
    if writer is None:
        raise ValueError(f"不支持的编码: {cfg.encoding}")
    if glob.has_magic(cfg.source):
        artifacts, count = render_line_group(cfg, root_dir)
        for output_path, content in artifacts:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            writer(output_path, content)
        logging.info(f"[OK] {cfg.dir}: {count} 条 -> {cfg.output}/")
        return count
    content, count = render_line_one(cfg, root_dir)
    out_path = os.path.join(root_dir, cfg.dir, cfg.output)
    writer(out_path, content)
    logging.info(f"[OK] {cfg.dir}: {count} 条 -> {cfg.output}")
    return count
def flatten_json_values(value, prefix: str = "", out: dict | None = None) -> dict:
    """Flatten nested translation JSON to source paths."""
    out = {} if out is None else out
    if isinstance(value, dict):
        for key, child in value.items():
            flatten_json_values(child, f"{prefix}.{key}" if prefix else key, out)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            flatten_json_values(child, f"{prefix}[{index}]", out)
    else:
        out[prefix] = value
    return out


def apply_translations_to_json(obj, translations: dict, path: str = ""):
    """Apply a flat path-to-value translation map to nested JSON."""
    if isinstance(obj, dict):
        return {
            key: apply_translations_to_json(value, translations, f"{path}.{key}" if path else key)
            for key, value in obj.items()
        }
    if isinstance(obj, list):
        return [
            apply_translations_to_json(value, translations, f"{path}[{index}]")
            for index, value in enumerate(obj)
        ]
    return translations.get(path, obj)


def iter_json_string_pairs(source, translated, path=""):
    if isinstance(source, dict) and isinstance(translated, dict):
        for key in source.keys() & translated.keys():
            child_path = f"{path}.{key}" if path else key
            yield from iter_json_string_pairs(source[key], translated[key], child_path)
    elif isinstance(source, list) and isinstance(translated, list):
        for index, (source_item, translated_item) in enumerate(zip(source, translated)):
            yield from iter_json_string_pairs(source_item, translated_item, f"{path}[{index}]")
    elif isinstance(source, str) and isinstance(translated, str):
        yield path, source, translated


def render_json_one(jcfg: ModJson, root_dir: str) -> tuple[object, int]:
    """Render one JSON mod without writing its output file."""
    mod_path = os.path.join(root_dir, jcfg.dir)
    trans_path = os.path.join(mod_path, "translations.json")
    src_path = os.path.join(mod_path, jcfg.source)
    if not os.path.exists(trans_path):
        raise FileNotFoundError(f"未找到翻译源: {trans_path}")
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"未找到源文件: {src_path}")

    translations = load_json(trans_path)
    source_data = load_json(src_path)
    flat_translations = flatten_json_values(translations)
    source_flat = flatten_json_values(source_data)
    expected_keys = {key for key, value in source_flat.items() if isinstance(value, str)}
    missing = expected_keys - flat_translations.keys()
    if missing:
        raise ValueError(f"Missing translation keys: {sorted(missing)[:10]}")
    translated_data = apply_translations_to_json(source_data, flat_translations)
    for path, source_value, translated_value in iter_json_string_pairs(source_data, translated_data):
        format_issues = translation_format_issues(source_value, translated_value)
        if format_issues:
            raise ValueError(f"{jcfg.dir} {path}: {'; '.join(format_issues)}")
    return translated_data, count_leaves(translations)


def build_json_one(jcfg: ModJson, root_dir: str) -> int:
    """Build one JSON mod and return its translation count."""
    translated_data, count = render_json_one(jcfg, root_dir)
    out_path = os.path.join(root_dir, jcfg.dir, jcfg.output)
    with open(out_path, "w", encoding="utf-8", newline="\n") as file:
        json.dump(translated_data, file, ensure_ascii=False, indent=2)
        file.write("\n")
    logging.info(f"[OK] {jcfg.dir}: {count} 条 -> {jcfg.output}")
    return count
def render_qt_one(config: ModQt, root_dir: str) -> tuple[str, int]:
    mod_path = os.path.join(root_dir, config.dir)
    source_path = os.path.join(mod_path, config.source)
    translation_path = os.path.join(mod_path, "translations.json")
    source_text = read_text(source_path)
    translations = load_json(translation_path)
    root = ET.fromstring(source_text)
    used = set()
    for message in root.findall(".//message"):
        source_node = message.find("source")
        if source_node is None:
            raise ValueError("Qt TS message has no source element")
        source = "".join(source_node.itertext())
        if source not in translations:
            raise ValueError(f"Missing Qt translation: {source}")
        translated = translations[source]
        issues = translation_format_issues(source, translated)
        if issues:
            raise ValueError(f"{source}: {'; '.join(issues)}")
        node = message.find("translation")
        if node is None:
            node = ET.SubElement(message, "translation")
        node.attrib.pop("type", None)
        node.text = translated
        used.add(source)
    extra = set(translations) - used
    if extra:
        raise ValueError(f"Unused Qt translation keys: {len(extra)}")
    start = source_text.find("<TS")
    closing = "</TS>"
    end = source_text.rfind(closing)
    if start < 0 or end < 0:
        raise ValueError("Invalid Qt TS root")
    end += len(closing)
    newline = "\r\n" if "\r\n" in source_text else "\n"
    body = ET.tostring(root, encoding="unicode", short_empty_elements=True)
    body = body.replace("\r\n", "\n").replace("\n", newline)
    return source_text[:start] + body + source_text[end:], len(translations)


def build_qt_one(config: ModQt, root_dir: str) -> int:
    content, count = render_qt_one(config, root_dir)
    output_path = os.path.join(root_dir, config.dir, config.output)
    write_utf8(output_path, content)
    logging.info(f"[OK] {config.dir}: {count} 条 -> {config.output}")
    return count


def iter_build_tasks():
    """Yield every configured build task, including multiple files per directory."""
    yield from ((cfg, "line") for cfg in MOD_CONFIGS)
    yield from ((cfg, "json") for cfg in JSON_MODS)
    yield from ((cfg, "qt") for cfg in QT_MODS)


def build_all(root_dir: str, filters: Optional[set[str]] = None) -> dict:
    """构建所有（或指定）模组，返回统计信息。"""
    # 计算总数用于进度显示
    all_mods = list(iter_build_tasks())
    
    if filters:
        all_mods = [(cfg, typ) for cfg, typ in all_mods if matches_filter(cfg.dir, filters)]
    
    total_count = len(all_mods)
    succeeded = []
    failed = []
    skipped = []
    total_entries = 0
    for current, (cfg, mod_type) in enumerate(all_mods, 1):
        logging.info(f"[{current}/{total_count}] {cfg.dir}")
        
        try:
            if mod_type == "line":
                count = build_one(cfg, root_dir)
            elif mod_type == "json":
                count = build_json_one(cfg, root_dir)
            elif mod_type == "qt":
                count = build_qt_one(cfg, root_dir)
            
            if count > 0:
                succeeded.append(cfg.dir)
                total_entries += count
            else:
                skipped.append(cfg.dir)
        except Exception as e:
            logging.error(f"构建失败 {cfg.dir}: {e}")
            failed.append((cfg.dir, str(e)))
    
    return {
        "succeeded": succeeded,
        "failed": failed,
        "skipped": skipped,
        "total_entries": total_entries,
    }


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
    return count_leaves(load_json(path))


def show_stats(root_dir: str):
    """统计各模组翻译数据。"""
    name_w = 64
    # 为保持表格对齐，用 print 而非 logging
    print(f"{pad_cjk('模组', name_w)}{pad_cjk('条目数', 8)} 类型")
    print("-" * 80)
    total = 0
    
    seen: set[str] = set()
    for cfg, mod_type in iter_build_tasks():
        if cfg.dir in seen:
            continue
        seen.add(cfg.dir)
        count = _load_translation_count(os.path.join(root_dir, cfg.dir, "translations.json"))
        if count is not None:
            total += count
            print(f"{pad_cjk(cfg.dir, name_w)}{count:<8} {mod_type}")
        else:
            print(f"{pad_cjk(cfg.dir, name_w)}{'-':<8} MISS")
    print("-" * 80)
    print(f"{pad_cjk('总计', name_w)}{total:<8}")

def _self_check() -> None:
    source = {"section": {"label": "nested"}, "label": "root"}
    translations = flatten_json_values({"section": {"label": "嵌套"}, "label": "根"})
    assert apply_translations_to_json(source, translations) == {
        "section": {"label": "嵌套"},
        "label": "根",
    }
    assert count_leaves({"records": ["first", "second"], "one": "third"}) == 3
    assert apply_translations_to_json(source, {"label": "根"})["section"]["label"] == "nested"
    print("self-check OK")


# ── 入口 ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description='批量生成模组的中文翻译文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
本地门禁 (sync→build→verify, 非零即失败):
  python sync_translation.py <mod> --check
  %(prog)s --dry-run <mod> && %(prog)s <mod> && python verify_translation.py <mod>
对话 XML 另走 translate.py: stats → pending --fill-bdd → apply → stats
'''
    )
    parser.add_argument('mods', nargs='*', help='要构建的模组（完整路径或 basename），留空则构建所有')
    parser.add_argument('--stats', action='store_true', help='统计模组翻译数据，不执行构建')
    parser.add_argument('--dry-run', action='store_true', help='预览要构建的模组，不实际执行')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细日志')
    parser.add_argument('--self-check', action='store_true', help='运行构建逻辑自检')
    
    args = parser.parse_args()
    
    if args.self_check:
        _self_check()
        return 0

    setup_cli_logging(verbose=args.verbose)

    root = os.path.dirname(os.path.abspath(__file__))
    
    # 加载配置 ponytail: single loader in config.py
    global MOD_CONFIGS, JSON_MODS, QT_MODS
    try:
        MOD_CONFIGS, JSON_MODS, QT_MODS = load_repo_configs(root)
        logging.info(f"从 mods.toml 加载配置：{len(MOD_CONFIGS)} line + {len(JSON_MODS)} json + {len(QT_MODS)} qt")
    except Exception as e:
        logging.error(f"无法加载 mods.toml: {e}")
        return 1
    # 统计模式
    if args.stats:
        show_stats(root)
        return 0
    
    # 过滤器
    filters = set(args.mods) if args.mods else None
    
    if filters and not any(matches_filter(cfg.dir, filters) for cfg, _ in iter_build_tasks()):
        logging.error(f"未找到模组: {', '.join(sorted(filters))}")
        return 2

    # 预览模式
    if args.dry_run:
        all_mods = list(iter_build_tasks())
        
        if filters:
            all_mods = [(cfg, typ) for cfg, typ in all_mods if matches_filter(cfg.dir, filters)]
        
        print(f"将构建 {len(all_mods)} 个模组:")
        for cfg, mod_type in all_mods:
            print(f"  - {cfg.dir} ({mod_type})")
        return 0
    
    # 执行构建
    result = build_all(root, filters)
    
    # 显示详细摘要
    print("\n" + "=" * 60)
    print("构建完成")
    print("=" * 60)
    print(f"成功: {len(result['succeeded'])}")
    print(f"失败: {len(result['failed'])}")
    print(f"跳过: {len(result['skipped'])}")
    print(f"总翻译条目: {result['total_entries']}")
    
    if result['failed']:
        print("\n失败模组:")
        for mod_dir, error in result['failed']:
            print(f"  - {mod_dir}: {error}")
    
    if result['skipped']:
        print("\n跳过模组 (无翻译或文件缺失):")
        for mod_dir in result['skipped'][:5]:
            print(f"  - {mod_dir}")
        if len(result['skipped']) > 5:
            print(f"  ... 及其他 {len(result['skipped']) - 5} 个")
    
    print("=" * 60)
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
