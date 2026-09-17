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
import logging
from typing import Optional

from locale_utils import read_lines, split_line, force_utf8_stdout
from config import ModConfig, load_configs_from_toml

force_utf8_stdout()

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)


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
    # 读取英文源文件
    source_path = os.path.join(mod_path, mod_config.source)
    if not os.path.exists(source_path):
        logging.error(f"源文件不存在: {source_path}")
        return {}, set()
    
    source_keys = extract_keys_from_source(source_path, mod_config.sep)
    
    # 读取 translations.json
    trans_path = os.path.join(mod_path, "translations.json")
    if not os.path.exists(trans_path):
        logging.error(f"translations.json 不存在: {trans_path}")
        return source_keys, set()  # 全部缺失
    
    try:
        with open(trans_path, "r", encoding="utf-8") as f:
            translations = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logging.error(f"无法读取 {trans_path}: {e}")
        return {}, set()
    
    # 对比
    trans_keys = set(translations.keys())
    missing = {}
    
    for full_key, en_value in source_keys.items():
        # 检查完整键或裸键是否存在
        bare_key = full_key.split(".", 1)[-1] if "." in full_key else full_key
        if full_key not in trans_keys and bare_key not in trans_keys:
            missing[full_key] = en_value
    
    return missing, trans_keys


def sync_translations(mod_config: ModConfig, mod_path: str, missing: dict[str, str], interactive: bool = False):
    """将缺失的键添加到 translations.json。
    
    Args:
        mod_config: 模组配置
        mod_path: 模组路径
        missing: 缺失的 {key: 英文值}
        interactive: 是否交互式输入翻译（否则用英文占位）
    """
    trans_path = os.path.join(mod_path, "translations.json")
    
    # 读取现有翻译
    if os.path.exists(trans_path):
        with open(trans_path, "r", encoding="utf-8") as f:
            translations = json.load(f)
    else:
        translations = {}
    
    # 添加缺失项
    for key, en_value in sorted(missing.items()):
        if interactive:
            print(f"\n[{key}]")
            print(f"  英文: {en_value}")
            cn_value = input("  中文: ").strip()
            if not cn_value:
                cn_value = en_value  # 空输入用英文占位
        else:
            cn_value = en_value  # 英文占位
        
        translations[key] = cn_value
    
    # 写回 translations.json（保持排序）
    with open(trans_path, "w", encoding="utf-8") as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)
    
    logging.info(f"已更新 {trans_path}，新增 {len(missing)} 条")


def process_mod(mod_config: ModConfig, root_dir: str, check_only: bool, interactive: bool):
    """处理单个模组。"""
    mod_path = os.path.join(root_dir, mod_config.dir)
    
    if not os.path.exists(mod_path):
        logging.warning(f"模组目录不存在: {mod_path}")
        return
    
    logging.info(f"\n检查模组: {mod_config.dir}")
    
    missing, existing = find_missing_keys(mod_config, mod_path)
    
    if not missing:
        logging.info(f"[✓] 无缺失词条（已有 {len(existing)} 条翻译）")
        return
    
    # 显示缺失词条
    print(f"\n发现 {len(missing)} 个新词条需要翻译：")
    for key, en_value in sorted(missing.items()):
        print(f"  {key} = \"{en_value}\"")
    
    if check_only:
        return
    
    # 同步
    if interactive:
        confirm = input(f"\n交互式添加翻译？[y/N] ").strip().lower()
        if confirm != 'y':
            return
    else:
        confirm = input(f"\n自动添加（英文占位）？[y/N] ").strip().lower()
        if confirm != 'y':
            return
    
    sync_translations(mod_config, mod_path, missing, interactive)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="同步翻译工具")
    parser.add_argument("mods", nargs="*", help="模组名称（支持短名或完整路径）")
    parser.add_argument("--all", action="store_true", help="处理所有模组")
    parser.add_argument("--check", action="store_true", help="仅检查，不修改")
    parser.add_argument("--sync", action="store_true", help="自动同步（英文占位）")
    parser.add_argument("--interactive", action="store_true", help="交互式输入翻译")
    
    args = parser.parse_args()
    
    # 加载配置
    root_dir = os.path.dirname(os.path.abspath(__file__))
    toml_path = os.path.join(root_dir, "mods.toml")
    
    if not os.path.exists(toml_path):
        logging.error(f"未找到 mods.toml: {toml_path}")
        sys.exit(1)
    
    line_configs, json_configs, script_configs = load_configs_from_toml(toml_path)
    
    # 只处理 line-based 模组（TXT/INI）
    all_configs = line_configs
    
    if args.all:
        configs_to_process = all_configs
    elif args.mods:
        configs_to_process = []
        for name in args.mods:
            # 支持短名或完整路径
            matched = [c for c in all_configs if name.lower() in c.dir.lower() or c.dir == name]
            if not matched:
                logging.warning(f"未找到模组: {name}")
                continue
            configs_to_process.extend(matched)
    else:
        parser.print_help()
        sys.exit(0)
    
    # 确定模式
    check_only = args.check or not (args.sync or args.interactive)
    interactive = args.interactive
    
    # 处理
    for cfg in configs_to_process:
        process_mod(cfg, root_dir, check_only, interactive)


if __name__ == "__main__":
    main()
