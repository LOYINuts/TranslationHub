"""
翻译校验脚本：检查单个模组或所有模组的翻译完整性。

用法：
  uv run python verify_translation.py              # 校验所有模组
  uv run python verify_translation.py FUCKRACE     # 校验指定模组
  uv run python verify_translation.py FUCK FUCKRACE  # 校验多个

检查项：
  - 翻译键覆盖
  - 转义、printf/Python/Qt 占位符和标记
  - 生成产物是否等于当前 translations.json 构建结果
  - script 模组声明的验证脚本
  - Eslifer Qt TS 和 Descriptionmods 结构
"""

import json
import os
import subprocess
import xml.etree.ElementTree as ET
import sys
import logging

from locale_utils import (
    read_lines,
    read_text,
    split_line,
    resolve_key_with_section,
    force_utf8_stdout,
    load_json,
    translation_format_issues,
 )
from build_all import flatten_json_values, render_json_one, render_line_one
force_utf8_stdout()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)


# ── 从 config.py 加载配置 ─────────────────────────────────────────────────

from config import ModJson, load_configs_from_toml


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



def verify_json_mod(mod_config, root: str) -> list[str]:
    """Verify translation coverage, formatting, and generated JSON output."""
    mod_path = os.path.join(root, mod_config.dir)
    source_path = os.path.join(mod_path, mod_config.source)
    output_path = os.path.join(mod_path, mod_config.output)
    trans_path = os.path.join(mod_path, "translations.json")
    for label, path in (("英文 JSON", source_path), ("翻译源", trans_path), ("中文 JSON", output_path)):
        if not os.path.exists(path):
            return [f"[缺失] 未找到{label}: {path}"]

    try:
        source = flatten_json_values(load_json(source_path))
        translations = flatten_json_values(load_json(trans_path))
        expected, _ = render_json_one(mod_config, root)
        actual = load_json(output_path)
    except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"[错误] JSON 无法验证: {exc}"]

    missing = sorted(
        path for path, value in source.items()
        if isinstance(value, str) and path not in translations
    )
    issues = []
    if missing:
        issues.append(f"[缺失] {len(missing)} 个翻译键：{', '.join(missing[:10])}")
    if actual != expected:
        issues.append("[过期] 中文 JSON 与 translations.json 构建结果不一致")
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

    # 3. Confirm generated output is current.
    try:
        expected, _ = render_line_one(get_line_configs()[mod_dir], root)
        if read_text(cn_path) != expected:
            issues.append("[过期] 中文文件与 translations.json 构建结果不一致")
    except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        issues.append(f"[错误] 无法重建预期输出: {exc}")
    if not issues:
        issues.append("[OK] 全部检查通过")

    return issues


def verify_script_mod(mod_config, root: str) -> list[str]:
    """Run configured verifier for a script-built mod."""
    if not mod_config.verify:
        return ["[缺失] script 配置未声明 verify"]
    mod_path = os.path.join(root, mod_config.dir)
    verify_path = os.path.join(mod_path, mod_config.verify)
    if not os.path.exists(verify_path):
        return [f"[缺失] 未找到验证脚本: {verify_path}"]
    result = subprocess.run(
        [sys.executable, verify_path],
        cwd=mod_path,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        return [f"[错误] 验证脚本失败: {detail or f'exit {result.returncode}'}"]
    return ["[OK] 全部检查通过"]


def verify_qt_ts(root: str) -> list[str]:
    """Verify Eslifer Qt TS source/translation pairing and placeholders."""
    source_path = os.path.join(root, "Eslifer", "origin", "eslifier_translation.ts")
    target_path = os.path.join(root, "Eslifer", "eslifier_translation.ts")
    try:
        source_messages = ET.parse(source_path).getroot().findall(".//message")
        target_messages = ET.parse(target_path).getroot().findall(".//message")
    except (OSError, ET.ParseError) as exc:
        return [f"[错误] Qt TS 无法读取: {exc}"]
    if len(source_messages) != len(target_messages):
        return [f"[结构] Qt TS 条目数不同：源 {len(source_messages)}，译文 {len(target_messages)}"]

    issues = []
    for index, (source_message, target_message) in enumerate(zip(source_messages, target_messages), 1):
        source = "".join(source_message.findtext("source", default=""))
        target_source = "".join(target_message.findtext("source", default=""))
        translation_node = target_message.find("translation")
        translation = "" if translation_node is None else "".join(translation_node.itertext())
        if source != target_source:
            issues.append(f"[结构] Qt TS 第 {index} 条 source 不一致")
        if not translation.strip() or (translation_node is not None and translation_node.get("type") == "unfinished"):
            issues.append(f"[缺失] Qt TS 第 {index} 条未翻译")
            continue
        format_issues = translation_format_issues(source, translation)
        if format_issues:
            issues.append(f"[格式] Qt TS 第 {index} 条: {'; '.join(format_issues)}")
    return issues or ["[OK] 全部检查通过"]

def find_unregistered_translation_dirs(root: str, registered_dirs: set[str]) -> list[str]:
    """Find translations.json directories that have no build configuration."""
    normalize = lambda path: os.path.normcase(os.path.normpath(path))
    registered = {normalize(path) for path in registered_dirs}
    unregistered = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name != ".git"]
        if "translations.json" in filenames:
            relative = os.path.relpath(dirpath, root)
            if normalize(relative) not in registered:
                unregistered.append(relative.replace(os.sep, "/"))
    return sorted(unregistered)


def verify_translation_registry(root: str, registered_dirs: set[str]) -> list[str]:
    unregistered = find_unregistered_translation_dirs(root, registered_dirs)
    return (
        [f"[未登记] {path} 包含 translations.json，但未在 mods.toml 注册" for path in unregistered]
        or ["[OK] 所有 translations.json 均已登记"]
    )



def verify_descriptionmods(root: str) -> list[str]:
    """Verify Descriptionmods source/target file and line structure."""
    base = os.path.join(root, "Descriptionmods")
    target_base = os.path.join(base, "zh")
    source_files = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [name for name in dirnames if name != "zh"]
        source_files.extend(os.path.join(dirpath, name) for name in filenames if name.lower().endswith(".ini"))
    issues = []
    expected_targets = set()
    for source_path in sorted(source_files):
        relative = os.path.relpath(source_path, base)
        target_path = os.path.join(target_base, relative)
        expected_targets.add(os.path.normcase(target_path))
        if not os.path.exists(target_path):
            issues.append(f"[缺失] Descriptionmods/zh/{relative}")
            continue
        def entries(path: str) -> dict[str, list[list[str]]]:
            result = {}
            for line in read_lines(path):
                if not line or line.startswith("#"):
                    continue
                parts = line.split("|")
                if len(parts) >= 2:
                    result.setdefault(parts[0], []).append(parts)
            return result

        source_entries = entries(source_path)
        target_entries = entries(target_path)
        missing = sorted(source_entries.keys() - target_entries.keys())
        extra = sorted(target_entries.keys() - source_entries.keys())
        if missing:
            issues.append(f"[缺失] {relative}: {', '.join(missing[:10])}")
        if extra:
            issues.append(f"[多余] {relative}: {', '.join(extra[:10])}")
        for key in sorted(source_entries.keys() & target_entries.keys()):
            source_values = source_entries[key]
            target_values = target_entries[key]
            if len(source_values) != len(target_values):
                issues.append(f"[结构] {relative}:{key} 重复条目数不同")
                continue
            for source_parts, target_parts in zip(source_values, target_values):
                source_meta = [part.strip() for part in source_parts[2:]]
                target_meta = [part.strip() for part in target_parts[2:]]
                if len(source_parts) != len(target_parts) or source_meta != target_meta:
                    issues.append(f"[结构] {relative}:{key} 元字段不一致")
                    continue
                format_issues = translation_format_issues(source_parts[1], target_parts[1])
                if format_issues:
                    issues.append(f"[格式] {relative}:{key}: {'; '.join(format_issues)}")
    for dirpath, _, filenames in os.walk(target_base):
        for name in filenames:
            target_path = os.path.join(dirpath, name)
            if name.lower().endswith(".ini") and os.path.normcase(target_path) not in expected_targets:
                issues.append(f"[多余] {os.path.relpath(target_path, target_base)}")
    return issues or ["[OK] 全部检查通过"]


def _self_check() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as root:
        mod_path = os.path.join(root, "mod")
        os.mkdir(mod_path)
        data = {
            "en.json": {"key": "Value %1"},
            "translations.json": {"key": "值 %1"},
            "zh.json": {"key": "stale %1"},
        }
        for name, value in data.items():
            with open(os.path.join(mod_path, name), "w", encoding="utf-8") as file:
                json.dump(value, file, ensure_ascii=False)
        issues = verify_json_mod(ModJson("mod", "en.json", "zh.json"), root)
        assert any(issue.startswith("[过期]") for issue in issues), issues
        assert find_unregistered_translation_dirs(root, set()) == ["mod"]
        assert find_unregistered_translation_dirs(root, {"mod"}) == []
    print("self-check OK")


def main():
    if sys.argv[1:] == ["--self-check"]:
        _self_check()
        return 0
    root = os.path.dirname(os.path.abspath(__file__))
    filters = set(sys.argv[1:]) if len(sys.argv) > 1 else None

    configs, json_mods, script_mods = get_mod_configs()

    
    def matches_filter(mod_dir: str, filters):
        """No filter = all. Accept full path or basename."""
        if not filters:
            return True
        norm = mod_dir.replace("\\", "/").lower()
        base = os.path.basename(norm)
        for value in filters:
            filter_norm = value.replace("\\", "/").rstrip("/").lower()
            if norm == filter_norm or base == filter_norm:
                return True
        return False
    tasks = (
        [(c.dir, "line", c) for c in configs]
        + [(c.dir, "json", c) for c in json_mods]
        + [(c.dir, "script", c) for c in script_mods]
        + [("Eslifer", "qt", None), ("Descriptionmods", "description", None)]
    )
    if filters and not any(matches_filter(mod_dir, filters) for mod_dir, _, _ in tasks):
        logging.error(f"未找到模组: {', '.join(sorted(filters))}")
        return 2
    exit_code = 0
    if filters is None:
        print(f"\n{'='*60}")
        logging.info("translations.json registration")
        registered_dirs = {config.dir for config in configs + json_mods + script_mods}
        for issue in verify_translation_registry(root, registered_dirs):
            if issue.startswith("[OK]"):
                logging.info(issue)
            else:
                logging.error(issue)
                exit_code = 1

    for mod_dir, mod_type, config in tasks:
        if not matches_filter(mod_dir, filters):
            continue

        print(f"\n{'='*60}")
        logging.info(f"{mod_dir} ({mod_type})")
        print(f"{'='*60}")

        if mod_type == "json":
            issues = verify_json_mod(config, root)
        elif mod_type == "script":
            issues = verify_script_mod(config, root)
        elif mod_type == "qt":
            issues = verify_qt_ts(root)
        elif mod_type == "description":
            issues = verify_descriptionmods(root)
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

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
