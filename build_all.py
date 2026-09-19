"""
统一构建脚本：批量生成所有模组的中文翻译文件。

用法：
  uv run python build_all.py          # 构建所有模组
  uv run python build_all.py --stats   # 仅统计，不生成
  uv run python build_all.py FUCK KillFeed  # 短名或完整相对路径均可

数据驱动：翻译源位于各模组的 translations.json，构建配置位于 mods.toml。
支持三种模组类型：
  1. line-based：按行替换（制表符/等号分隔的 .txt/.ini）
  2. json-based：flat JSON 键值替换（.json）
  3. script-based：运行模组目录下的独立脚本（如 IED 的 JSON→JSON 转换）
"""

import json
import os
import subprocess
import sys
from typing import Optional

import logging
import argparse
from locale_utils import (
    read_lines,
    write_utf16le_bom,
    write_utf8_bom,
    write_utf8,
    split_line,
    resolve_key_with_section,
    force_utf8_stdout,
    load_json,
    translation_format_issues,
)

force_utf8_stdout()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# ── 模组构建配置 ─────────────────────────────────────────────────────────────


from config import ModConfig, ModJson, ModScript, load_configs_from_toml

# 模组配置从 mods.toml 加载，这些全局变量在 main() 中赋值
MOD_CONFIGS: list[ModConfig] = []
JSON_MODS: list = []
SCRIPT_MODS: list = []

# 写入器映射
WRITERS = {
    "utf16-le-bom": write_utf16le_bom,
    "utf-8-bom": write_utf8_bom,
    "utf-8": write_utf8,
}

def count_leaves(d):
    """递归统计翻译条目数：嵌套 JSON 按叶子计数。"""
    return sum(count_leaves(v) if isinstance(v, dict) else 1 for v in d.values())


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


def build_one(cfg: ModConfig, root_dir: str) -> int:
    """Build one line-based mod and return its translation count."""
    content, count = render_line_one(cfg, root_dir)
    out_path = os.path.join(root_dir, cfg.dir, cfg.output)
    writer = WRITERS.get(cfg.encoding)
    if writer is None:
        raise ValueError(f"不支持的编码: {cfg.encoding}")
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
def build_script_one(smod: ModScript, root_dir: str) -> int:
    """运行脚本型模组的生成脚本，返回翻译条目数。"""
    mod_path = os.path.join(root_dir, smod.dir)
    script_path = os.path.join(mod_path, smod.script)
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"未找到脚本: {script_path}")

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=mod_path,
            capture_output=True,
            text=True,
            check=True,  # 失败时抛异常
        )
    except subprocess.CalledProcessError as e:
        logging.error(f"{smod.dir} 脚本执行失败: {e.stderr.strip()}")
        raise

    logging.info(f"[OK] {smod.dir}: {result.stdout.strip()}")
    # 从脚本输出解析条目数
    for line in result.stdout.splitlines():
        if "总计:" in line:
            try:
                return int(line.split(":")[1].strip())
            except (ValueError, IndexError):
                pass
    return 0


def matches_filter(mod_dir: str, filters: Optional[set[str]]) -> bool:
    """检查模组是否匹配过滤器。支持完整路径或 basename。"""
    if not filters:
        return True
    norm = mod_dir.replace("\\", "/").lower()
    base = os.path.basename(norm)
    for value in filters:
        filter_norm = value.replace("\\", "/").rstrip("/").lower()
        if norm == filter_norm or base == filter_norm:
            return True
    return False



def iter_all_mods():
    """遍历所有模组配置，返回 (dir, type, config) 元组。
    
    去重：同一 dir 只返回一次。
    """
    seen_dirs: set[str] = set()
    for cfg in MOD_CONFIGS:
        if cfg.dir not in seen_dirs:
            seen_dirs.add(cfg.dir)
            yield (cfg.dir, "line", cfg)
    for jcfg in JSON_MODS:
        if jcfg.dir not in seen_dirs:
            seen_dirs.add(jcfg.dir)
            yield (jcfg.dir, "json", jcfg)
    for smod in SCRIPT_MODS:
        if smod.dir not in seen_dirs:
            seen_dirs.add(smod.dir)
            yield (smod.dir, "script", smod)

def iter_build_tasks():
    """Yield every configured build task, including multiple files per directory."""
    yield from ((cfg, "line") for cfg in MOD_CONFIGS)
    yield from ((cfg, "json") for cfg in JSON_MODS)
    yield from ((cfg, "script") for cfg in SCRIPT_MODS)


def build_all(root_dir: str, filters: Optional[set[str]] = None) -> dict:
    """构建所有（或指定）模组，返回统计信息。"""
    # 计算总数用于进度显示
    all_mods = list(iter_build_tasks())
    
    if filters:
        all_mods = [(cfg, typ) for cfg, typ in all_mods if matches_filter(cfg.dir, filters)]
    
    total_count = len(all_mods)
    current = 0
    succeeded = []
    failed = []
    skipped = []
    total_entries = 0
    
    for cfg, mod_type in all_mods:
        current += 1
        logging.info(f"[{current}/{total_count}] {cfg.dir}")
        
        try:
            if mod_type == "line":
                count = build_one(cfg, root_dir)
            elif mod_type == "json":
                count = build_json_one(cfg, root_dir)
            else:  # script
                count = build_script_one(cfg, root_dir)
            
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
    
    for mod_dir, mod_type, cfg in iter_all_mods():
        count = _load_translation_count(os.path.join(root_dir, mod_dir, "translations.json"))
        if count is not None:
            total += count
            print(f"{pad_cjk(mod_dir, name_w)}{count:<8} {mod_type}")
        else:
            print(f"{pad_cjk(mod_dir, name_w)}{'-':<8} MISS")
    
    print("-" * 80)
    print(f"{pad_cjk('总计', name_w)}{total:<8}")

def _self_check() -> None:
    source = {"section": {"label": "nested"}, "label": "root"}
    translations = flatten_json_values({"section": {"label": "嵌套"}, "label": "根"})
    assert apply_translations_to_json(source, translations) == {
        "section": {"label": "嵌套"},
        "label": "根",
    }
    assert apply_translations_to_json(source, {"label": "根"})["section"]["label"] == "nested"
    print("self-check OK")


# ── 入口 ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description='批量生成模组的中文翻译文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s --stats              # 统计所有模组
  %(prog)s                      # 构建所有模组
  %(prog)s FUCK KillFeed        # 只构建指定模组
  %(prog)s --dry-run FUCK       # 预览会构建的模组
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

    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    root = os.path.dirname(os.path.abspath(__file__))
    
    # 加载配置
    toml_path = os.path.join(root, "mods.toml")
    if not os.path.exists(toml_path):
        logging.error(f"未找到 {toml_path}，请创建模组配置文件")
        return 1
    
    global MOD_CONFIGS, JSON_MODS, SCRIPT_MODS
    try:
        MOD_CONFIGS, JSON_MODS, SCRIPT_MODS = load_configs_from_toml(toml_path)
        logging.info(f"从 {toml_path} 加载配置：{len(MOD_CONFIGS)} line + {len(JSON_MODS)} json + {len(SCRIPT_MODS)} script")
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
    print(f"\n{'='*60}")
    print(f"构建完成")
    print(f"{'='*60}")
    print(f"成功: {len(result['succeeded'])}")
    print(f"失败: {len(result['failed'])}")
    print(f"跳过: {len(result['skipped'])}")
    print(f"总翻译条目: {result['total_entries']}")
    
    if result['failed']:
        print(f"\n失败模组:")
        for mod_dir, error in result['failed']:
            print(f"  - {mod_dir}: {error}")
    
    if result['skipped']:
        print(f"\n跳过模组 (无翻译或文件缺失):")
        for mod_dir in result['skipped'][:5]:
            print(f"  - {mod_dir}")
        if len(result['skipped']) > 5:
            print(f"  ... 及其他 {len(result['skipped']) - 5} 个")
    
    print(f"{'='*60}")
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
