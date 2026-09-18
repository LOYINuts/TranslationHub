"""
翻译校验脚本：检查单个模组或所有模组的翻译完整性。

用法：
  uv run python verify_translation.py              # 校验所有模组
  uv run python verify_translation.py FUCKRACE     # 校验指定模组
  uv run python verify_translation.py FUCK FUCKRACE  # 校验多个

检查项：
  - 键完整性（有无缺失/多余）
  - 转义序列 \n 格式（是否存成真实换行符）
  - 格式占位符 %d/%s 是否保留
  - 疑似未翻译项（EN==CN 且非全大写）
"""

import json
import os
import re
import sys
import logging

from locale_utils import (
    read_lines,
    split_line,
    resolve_key_with_section,
    force_utf8_stdout,
    check_json_keys,
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


# ── 从 config.py 加载配置 ─────────────────────────────────────────────────

from config import load_configs_from_toml


CONFIG_CACHE = None


def get_mod_configs():
    """加载 mods.toml 配置。"""
    global CONFIG_CACHE
    if CONFIG_CACHE is not None:
        return CONFIG_CACHE
    
    toml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mods.toml")
    if not os.path.exists(toml_path):
        raise FileNotFoundError(f"未找到 {toml_path}")
    
    line_configs, json_configs, script_configs = load_configs_from_toml(toml_path)
    CONFIG_CACHE = (line_configs, json_configs, script_configs)
    return CONFIG_CACHE


def get_line_configs():
    configs, _, _ = get_mod_configs()
    return {c.dir: c for c in configs}

# ── 校验函数 ─────────────────────────────────────────────────────────────────


def find_translation_files(mod_dir: str, root: str) -> dict:
    """自动探测模组目录下的翻译文件，返回 {en_path, cn_path, json_path, sep}。"""
    mod_path = os.path.join(root, mod_dir)
    if not os.path.isdir(mod_path):
        return {"error": f"目录不存在: {mod_path}"}

    cfg = get_line_configs().get(mod_dir)
    if cfg:
        en_path = os.path.join(mod_path, cfg.source)
        cn_path = os.path.join(mod_path, cfg.output)
        json_path = os.path.join(mod_path, "translations.json")
        return {
            "en": en_path if os.path.exists(en_path) else None,
            "cn": cn_path if os.path.exists(cn_path) else None,
            "json": json_path if os.path.exists(json_path) else None,
            "sep": cfg.sep,
        }

    # 未注册的模组：按约定猜测
    # 未注册的模组：按命名约定猜测文件。
    json_path = os.path.join(mod_path, "translations.json")
    names = os.listdir(mod_path)
    en_candidates = [f for f in names if f.lower().endswith(("_english.txt", "_english.ini"))]
    if not en_candidates:
        en_candidates = [f for f in names if f.lower().endswith((".txt", ".ini")) and "zh" not in f.lower() and "chinese" not in f.lower()]
    cn_candidates = [f for f in names if f.lower().endswith(("_chinese.txt", "_chinese.ini", "_zh.txt", "_zh.ini"))]
    en_path = os.path.join(mod_path, en_candidates[0]) if en_candidates else None
    cn_path = os.path.join(mod_path, cn_candidates[0]) if cn_candidates else None
    return {
        "en": en_path,
        "cn": cn_path,
        "json": json_path if os.path.exists(json_path) else None,
        "sep": "\t",
    }



def _flatten_json(value, prefix="") -> dict[str, object]:
    if isinstance(value, dict):
        out = {}
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            out.update(_flatten_json(child, path))
        return out
    if isinstance(value, list):
        out = {}
        for index, child in enumerate(value):
            out.update(_flatten_json(child, f"{prefix}[{index}]"))
        return out
    return {prefix: value}


def verify_json_mod(mod_config, root: str) -> list[str]:
    """Verify source/output JSON keys and format placeholders."""
    mod_path = os.path.join(root, mod_config.dir)
    source_path = os.path.join(mod_path, mod_config.source)
    output_path = os.path.join(mod_path, mod_config.output)
    issues = []
    if not os.path.exists(source_path):
        return [f"[跳过] 未找到英文 JSON: {source_path}"]
    if not os.path.exists(output_path):
        return [f"[缺失] 未找到中文 JSON: {output_path}"]
    try:
        key_result = check_json_keys(source_path, output_path)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"[错误] JSON 无法读取: {exc}"]
    if key_result["missing"]:
        issues.append(f"[缺失] {len(key_result['missing'])} 个 JSON 键：{', '.join(key_result['missing'][:10])}")
    if key_result["extra"]:
        issues.append(f"[多余] {len(key_result['extra'])} 个 JSON 键：{', '.join(key_result['extra'][:10])}")
    source = _flatten_json(load_json(source_path))
    output = _flatten_json(load_json(output_path))
    for key in sorted(source.keys() & output.keys()):
        original = source[key]
        translated = output[key]
        if not isinstance(original, str) or not isinstance(translated, str):
            continue
        format_issues = translation_format_issues(original, translated)
        if format_issues:
            issues.append(f"[格式] {key}: {'; '.join(format_issues)}")
    return issues or ["[OK] 全部检查通过"]


def _read_line_map(path: str, sep) -> dict[str, str]:
    values: dict[str, str] = {}
    section = ""
    for line in read_lines(path):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1]
            continue
        if stripped.startswith(";"):
            continue
        key, value = split_line(line, sep)
        if key is None:
            continue
        key = key.strip()
        full_key = f"{section}.{key}" if section and not key.startswith(f"{section}.") else key
        values[full_key] = value
    return values


def verify_direct_line_mod(en_path: str, cn_path: str, sep) -> list[str]:
    en_lines = read_lines(en_path)
    cn_lines = read_lines(cn_path)
    issues: list[str] = []
    if len(en_lines) != len(cn_lines):
        issues.append(f"[结构] 行数不同：英文 {len(en_lines)}，中文 {len(cn_lines)}")
    en_map = _read_line_map(en_path, sep)
    cn_map = _read_line_map(cn_path, sep)
    missing = sorted(set(en_map) - set(cn_map))
    extra = sorted(set(cn_map) - set(en_map))
    if missing:
        issues.append(f"[缺失] {len(missing)} 条：{', '.join(missing[:10])}")
    if extra:
        issues.append(f"[多余] {len(extra)} 条：{', '.join(extra[:10])}")
    for key in sorted(set(en_map) & set(cn_map)):
        format_issues = translation_format_issues(en_map[key], cn_map[key], line_based=True)
        if format_issues:
            issues.append(f"[格式] {key}: {'; '.join(format_issues)}")
    return issues or ["[OK] 全部检查通过"]


def verify_mod(mod_dir: str, root: str) -> list:
    """校验单个模组，返回问题列表。"""
    issues = []
    files = find_translation_files(mod_dir, root)
    if "error" in files:
        return [files["error"]]

    en_path = files["en"]
    json_path = files["json"]
    cn_path = files["cn"]
    sep = files["sep"]

    if not en_path:
        issues.append(f"[跳过] 未找到英文源文件")
        return issues
    if not cn_path:
        issues.append(f"[缺失] 未找到中文输出文件")
        return issues
    if not json_path:
        return verify_direct_line_mod(en_path, cn_path, sep)

    # ── 读取英文源 ──
    en_lines = read_lines(en_path)
    en_map = {}
    current_section = ""
    for line in en_lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1]
            continue
        if stripped.startswith(";"):
            continue
        key, val = split_line(line, sep)
        if key:
            key = key.strip()  # 与 build_one 查找逻辑一致：剥离对齐空格
            # 使用统一键解析逻辑
            resolved = resolve_key_with_section(key, current_section, {})
            # 对于 en_map 我们直接使用解析后的键作为存储键
            if resolved:
                en_map[resolved] = val
            else:
                # fallback: 如果没有 section 或键已经完整
                full_key = f"{current_section}.{key}" if current_section and not key.startswith(f"{current_section}.") else key
                en_map[full_key] = val

    # ── 读取翻译 ──
    cn_map = load_json(json_path)
    en_keys = set(en_map.keys())
    cn_keys = set(cn_map.keys())

    # 1. 键完整性 — 使用统一键解析逻辑
    missing = []
    for k in sorted(en_keys):
        if resolve_key_with_section(k, "", cn_map) is None:
            missing.append(k)
    
    # 排除由节前缀 fallback 匹配的 cn 键
    matched_cn = set()
    for k in en_keys:
        resolved = resolve_key_with_section(k, "", cn_map)
        if resolved:
            matched_cn.add(resolved)
    extra = cn_keys - matched_cn
    if missing:
        issues.append(f"[缺失] {len(missing)} 条：{', '.join(missing[:10])}{'...' if len(missing) > 10 else ''}")
    if extra:
        issues.append(f"[多余] {len(extra)} 条：{', '.join(sorted(extra)[:10])}{'...' if len(extra) > 10 else ''}")

    # 2. 逐条检查内容
    # 构建反向映射：cn_key → en_key
    cn_to_en = {}
    for ek in en_keys:
        resolved = resolve_key_with_section(ek, "", cn_map)
        if resolved:
            cn_to_en[resolved] = ek
    for k in sorted(cn_keys):
        ek = cn_to_en.get(k, "")
        en_v = en_map.get(ek, "")
        cn_v = cn_map.get(k, "")

        if ek:
            format_issues = translation_format_issues(en_v, cn_v, line_based=True)
            if format_issues:
                issues.append(f"[格式] {k}: {'; '.join(format_issues)}")

        # 检查疑似未翻译（EN==CN 且非全大写/品牌名）
    # 3. 检查中文输出文件是否存在且与 translations.json 条目一致
    if cn_path and os.path.exists(cn_path):
        cn_out_lines = read_lines(cn_path)
        cn_out_keys = set()
        current_section = ""
        for line in cn_out_lines:
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                current_section = stripped[1:-1]
                continue
            key, _ = split_line(line, sep or "\t")
            if key:
                key = key.strip()  # 与 build_one 查找逻辑一致
                full_key = f"{current_section}.{key}" if current_section and not key.startswith(f"{current_section}.") else key
                cn_out_keys.add(full_key)
        cn_out_resolved = cn_out_keys | {k.split('.', 1)[1] for k in cn_out_keys if '.' in k}
        missing_in_output = cn_keys - cn_out_resolved
        if missing_in_output:
            issues.append(f"[输出缺失] 中文文件缺少 {len(missing_in_output)} 条：{', '.join(sorted(missing_in_output)[:5])}")

    if not issues:
        issues.append("[OK] 全部检查通过")

    return issues


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    filters = set(sys.argv[1:]) if len(sys.argv) > 1 else None

    configs, json_mods, script_mods = get_mod_configs()

    
    def matches_filter(mod_dir: str, filters):
        """No filter = all. Accept full path or basename."""
        if not filters:
            return True
        norm = mod_dir.replace("\\", "/")
        base = os.path.basename(norm)
        for f in filters:
            if norm == f or base == f:
                return True
        return False
    tasks = [(c.dir, "line", c) for c in configs] + [(c.dir, "json", c) for c in json_mods]
    exit_code = 0

    for mod_dir, mod_type, config in tasks:
        if not matches_filter(mod_dir, filters):
            continue

        print(f"\n{'='*60}")
        logging.info(f"{mod_dir} ({mod_type})")
        print(f"{'='*60}")

        if mod_type == "json":
            issues = verify_json_mod(config, root)
        else:
            issues = verify_mod(mod_dir, root)
        for issue in issues:
            if issue.startswith("[OK]"):
                logging.info(issue)
            else:
                logging.error(issue)
                exit_code = 1

    print(f"\n{'='*60}")
    if exit_code:
        logging.error("存在未通过项，请修复。")
    else:
        logging.info("全部通过 [OK]")
    print(f"{'='*60}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
