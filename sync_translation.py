"""
同步翻译工具：检测英文源文件中的新词条，更新 translations.json

用法：
  python sync_translation.py custommarkers --check        # 检查缺失的词条
  python sync_translation.py custommarkers --sync         # 自动添加缺失词条（英文原文作为占位）
  python sync_translation.py custommarkers --interactive  # 交互式添加翻译
  python sync_translation.py --all --check                # 检查所有模组
"""

import json
import os
import sys
import glob
import logging
from typing import Optional

from locale_utils import read_lines, split_line, load_json
from config import ModConfig, ModJson, ModQt, load_repo_configs, matches_filter, setup_cli_logging
from build_all import flatten_json_values
setup_cli_logging()  # ponytail: single logging setup


def extract_keys_from_source(source_path: str, sep: Optional[str]) -> dict[str, str]:
    """从英文源文件提取所有 key=value 对。
    
    返回: {完整键: 英文值} 字典
    """
    lines = read_lines(source_path)
    keys = {}
    current_section = ""
    
    for line in lines:
        stripped = line.strip()
        
        # 跟踪节
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1]
            continue
        
        # 跳过注释
        if stripped.startswith(";"):
            continue
        
        # 解析键值对
        key, val = split_line(line, sep)
        if key is not None and val is not None:
            lookup_key = key.strip()
            # 构建完整键（带节前缀）
            if current_section and not lookup_key.startswith(f"{current_section}."):
                full_key = f"{current_section}.{lookup_key}"
            else:
                full_key = lookup_key
            keys[full_key] = val.strip()
    
    return keys


def find_missing_keys(mod_config: ModConfig, mod_path: str) -> tuple[dict[str, str], set[str]]:
    """找出 translations.json 中缺失的键。
    
    返回: (缺失的 {key: 英文值}, translations.json 中存在的键集合)
    """
    if glob.has_magic(mod_config.source):
        source_keys = {}
        source_paths = sorted(glob.glob(os.path.join(mod_path, mod_config.source), recursive=True))
        output_root = os.path.join(mod_path, mod_config.output)
        source_paths = [
            path for path in source_paths
            if os.path.isfile(path)
            and os.path.commonpath([os.path.abspath(output_root), os.path.abspath(path)])
            != os.path.abspath(output_root)
        ]
        if not source_paths:
            raise FileNotFoundError(f"没有文件匹配: {mod_config.source}")
        for source_path in source_paths:
            relative = os.path.relpath(source_path, mod_path).replace(os.sep, "/")
            occurrences = {}
            for line in read_lines(source_path):
                if mod_config.sep not in line:
                    continue
                fields = line.split(mod_config.sep)
                if mod_config.value_field >= len(fields):
                    continue
                key = fields[0].strip()
                index = occurrences.get(key, 0)
                occurrences[key] = index + 1
                source_key = f"{relative}::{key}#{index}"
                source_keys[source_key] = fields[mod_config.value_field].strip()
    else:
        source_path = os.path.join(mod_path, mod_config.source)
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"源文件不存在: {source_path}")
        source_keys = extract_keys_from_source(source_path, mod_config.sep)
    trans_path = os.path.join(mod_path, "translations.json")
    translations = load_json(trans_path) if os.path.exists(trans_path) else {}
    if not isinstance(translations, dict):
        raise ValueError(f"翻译源必须是 JSON 对象: {trans_path}")

    trans_keys = set(translations)
    missing = {}
    for full_key, en_value in source_keys.items():
        bare_key = full_key.split(".", 1)[-1] if "." in full_key else full_key
        if full_key not in trans_keys and (glob.has_magic(mod_config.source) or bare_key not in trans_keys):
            missing[full_key] = en_value
    return missing, trans_keys

def find_missing_json(jcfg: ModJson, mod_path: str):
    """Diff flat source keys vs flat translation keys. ponytail: reuse build flatten."""
    src = flatten_json_values(load_json(os.path.join(mod_path, jcfg.source)))
    trans_path = os.path.join(mod_path, "translations.json")
    trans = flatten_json_values(load_json(trans_path)) if os.path.exists(trans_path) else {}
    want = {k for k, v in src.items() if isinstance(v, str)}
    missing = {k: src[k] for k in sorted(want - set(trans))}
    return missing, set(trans)


def find_missing_qt(qcfg: ModQt, mod_path: str):
    import xml.etree.ElementTree as ET
    from locale_utils import read_text
    root = ET.fromstring(read_text(os.path.join(mod_path, qcfg.source)))
    msgs = ["".join(m.find("source").itertext()) for m in root.findall(".//message") if m.find("source") is not None]
    trans_path = os.path.join(mod_path, "translations.json")
    trans = load_json(trans_path) if os.path.exists(trans_path) else {}
    missing = {m: m for m in msgs if m not in trans}
    return missing, set(trans)

def _unflatten(flat: dict) -> dict:
    """Rebuild nested dict from dotted flat keys. ponytail: ceil=flat-only files skip this."""
    out: dict = {}
    for key, value in flat.items():
        node = out
        *heads, tail = key.split(".")
        for head in heads:
            node = node.setdefault(head, {})
        node[tail] = value
    return out


def _nested_shape(translations) -> bool:
    return isinstance(translations, dict) and any(isinstance(v, dict) for v in translations.values())


def sync_translations(mod_path: str, missing: dict, interactive: bool = False):
    """Append missing keys with EN placeholder. Keeps nested shape when present."""
    trans_path = os.path.join(mod_path, "translations.json")
    translations = load_json(trans_path) if os.path.exists(trans_path) else {}
    if _nested_shape(translations):
        flat = flatten_json_values(translations)
        for key in sorted(missing):
            if interactive:
                print(f"\n[{key}]")
                print(f"  英文: {missing[key]}")
                got = input("  中文: ").strip() or missing[key]
            else:
                got = missing[key]
            flat[key] = got
        translations = _unflatten(flat)
    else:
        for key in sorted(missing):
            if interactive:
                print(f"\n[{key}]")
                print(f"  英文: {missing[key]}")
                translations[key] = input("  中文: ").strip() or missing[key]
            else:
                translations[key] = missing[key]
    with open(trans_path, "w", encoding="utf-8") as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)
    logging.info(f"已更新 {trans_path}，新增 {len(missing)} 条")


def process_task(kind: str, cfg, mod_path: str, check_only: bool, interactive: bool) -> bool:
    """Process one task. Return True when keys are missing or processing fails."""
    logging.info(f"\n检查模组: {cfg.dir} ({kind})")
    try:
        if kind == "line":
            missing, existing = find_missing_keys(cfg, mod_path)
        elif kind == "json":
            missing, existing = find_missing_json(cfg, mod_path)
        else:
            missing, existing = find_missing_qt(cfg, mod_path)
    except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        logging.error(f"检查失败: {exc}")
        return True
    if not missing:
        logging.info(f"[OK] 无缺失词条（已有 {len(existing)} 条翻译）")
        return False
    print(f"\n发现 {len(missing)} 个新词条需要翻译：")
    for key, en_value in sorted(missing.items()):
        print(f"  {key} = \"{en_value}\"")
    if check_only:
        return True
    prompt = "交互式添加翻译？[y/N] " if interactive else "自动添加（英文占位）？[y/N] "
    if input(f"\n{prompt}").strip().lower() != "y":
        return True
    sync_translations(mod_path, missing, interactive)
    return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="同步翻译工具")
    parser.add_argument("mods", nargs="*", help="模组名称（支持短名或完整路径）")
    parser.add_argument("--all", action="store_true", help="处理所有模组")
    parser.add_argument("--check", action="store_true", help="仅检查，不修改")
    parser.add_argument("--sync", action="store_true", help="自动同步（英文占位）")
    parser.add_argument("--interactive", action="store_true", help="交互式输入翻译")
    
    args = parser.parse_args()
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    line_configs, json_configs, qt_configs = load_repo_configs(root_dir)
    tasks = [("line", c) for c in line_configs] + [("json", c) for c in json_configs] + [("qt", c) for c in qt_configs]
    selection_failed = False
    if args.all:
        picked = tasks
    elif args.mods:
        picked = []  # placeholder, recomputed below
        # ponytail: one matcher from config.py; report unknown names once
        known = {c.dir for _, c in tasks}
        for name in args.mods:
            if not any(matches_filter(d, {name}) for d in known):
                logging.error(f"未找到模组: {name}")
                selection_failed = True
        picked = [(k, c) for k, c in tasks if any(matches_filter(c.dir, {m}) for m in args.mods)]
    else:
        parser.print_help()
        return 0
    check_only = args.check or not (args.sync or args.interactive)
    failed = False
    for kind, cfg in picked:
        failed = process_task(kind, cfg, os.path.join(root_dir, cfg.dir), check_only, args.interactive) or failed
    return 1 if failed or selection_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
