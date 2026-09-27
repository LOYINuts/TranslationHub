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
  - translations.json 键覆盖、格式和构建产物状态
  - Eslifer Qt TS 结构和占位符
"""

import json
import os
import glob
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
from build_all import flatten_json_values, render_json_one, render_line_group, render_line_one, render_qt_one
force_utf8_stdout()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)


# ── 从 config.py 加载配置 ─────────────────────────────────────────────────

from config import ModJson, ModQt, load_configs_from_toml


CONFIG_CACHE = None


def get_mod_configs():
    """加载 mods.toml 配置。"""
    global CONFIG_CACHE
    if CONFIG_CACHE is not None:
        return CONFIG_CACHE
    
    toml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mods.toml")
    if not os.path.exists(toml_path):
        raise FileNotFoundError(f"未找到 {toml_path}")
    
    line_configs, json_configs, qt_configs = load_configs_from_toml(toml_path)
    CONFIG_CACHE = (line_configs, json_configs, qt_configs)
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
def verify_json_translation_registry(mod_configs, root: str) -> list[str]:
    """Check that a shared JSON map covers exactly its configured sources."""
    if not mod_configs:
        return ["[OK] 没有 JSON 源"]
    mod_dir = mod_configs[0].dir
    mod_path = os.path.join(root, mod_dir)
    source_keys = set()
    try:
        translations = flatten_json_values(load_json(os.path.join(mod_path, "translations.json")))
        for config in mod_configs:
            source = flatten_json_values(load_json(os.path.join(mod_path, config.source)))
            source_keys.update(key for key, value in source.items() if isinstance(value, str))
    except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"[错误] 无法检查 JSON 译文键: {exc}"]
    missing = sorted(source_keys - translations.keys())
    extra = sorted(translations.keys() - source_keys)
    issues = []
    if missing:
        issues.append(f"[缺失] {len(missing)} 个 JSON 翻译键：{', '.join(missing[:10])}")
    if extra:
        issues.append(f"[多余] {len(extra)} 个 JSON 翻译键：{', '.join(extra[:10])}")
    return issues or ["[OK] 全部 JSON 翻译键已登记"]




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


def verify_line_config(config, root: str) -> list[str]:
    if not glob.has_magic(config.source):
        return verify_mod(config.dir, root)
    try:
        artifacts, _ = render_line_group(config, root)
    except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"[错误] 无法重建行文件: {exc}"]
    expected = {os.path.normcase(path): content for path, content in artifacts}
    issues = []
    for path, content in artifacts:
        if not os.path.exists(path):
            issues.append(f"[缺失] {path}")
        elif read_text(path) != content:
            issues.append(f"[过期] {path}")
    output_root = os.path.join(root, config.dir, config.output)
    for dirpath, _, filenames in os.walk(output_root):
        for name in filenames:
            path = os.path.join(dirpath, name)
            if name.lower().endswith(".ini") and os.path.normcase(path) not in expected:
                issues.append(f"[多余] {path}")
    return issues or ["[OK] 全部检查通过"]


def verify_qt_ts(config: ModQt, root: str) -> list[str]:
    """Verify a configured Qt TS source, translation, and generated output."""
    mod_path = os.path.join(root, config.dir)
    source_path = os.path.join(mod_path, config.source)
    target_path = os.path.join(mod_path, config.output)
    try:
        source_messages = ET.parse(source_path).getroot().findall(".//message")
        target_messages = ET.parse(target_path).getroot().findall(".//message")
        expected, _ = render_qt_one(config, root)
    except (OSError, ET.ParseError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"[错误] Qt TS 无法验证: {exc}"]
    if len(source_messages) != len(target_messages):
        return [f"[结构] Qt TS 条目数不同：源 {len(source_messages)}，译文 {len(target_messages)}"]
    issues = []
    for index, (source_message, target_message) in enumerate(zip(source_messages, target_messages), 1):
        source = "".join(source_message.findtext("source", default=""))
        target_source = "".join(target_message.findtext("source", default=""))
        node = target_message.find("translation")
        translated = "" if node is None else "".join(node.itertext())
        if source != target_source:
            issues.append(f"[结构] Qt TS 第 {index} 条 source 不一致")
        if not translated.strip() or (node is not None and node.get("type") == "unfinished"):
            issues.append(f"[缺失] Qt TS 第 {index} 条未翻译")
        elif translation_format_issues(source, translated):
            issues.append(f"[格式] Qt TS 第 {index} 条占位符不一致")
    if read_text(target_path) != expected:
        issues.append("[过期] Qt TS 与 translations.json 构建结果不一致")
    return issues or ["[OK] 全部检查通过"]
def find_unregistered_translation_dirs(root: str, registered_dirs: set[str]) -> list[str]:
    """Find translation sources without a mods.toml entry."""
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

    configs, json_mods, qt_mods = get_mod_configs()

    
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
    json_groups = {}
    for config in json_mods:
        json_groups.setdefault(config.dir, []).append(config)
    tasks = (
        [(config.dir, "line", config) for config in configs]
        + [(config.dir, "json", config) for config in json_mods]
        + [(directory, "json-map", group) for directory, group in json_groups.items()]
        + [(config.dir, "qt", config) for config in qt_mods]
    )
    if filters and not any(matches_filter(mod_dir, filters) for mod_dir, _, _ in tasks):
        logging.error(f"未找到模组: {', '.join(sorted(filters))}")
        return 2
    exit_code = 0
    if filters is None:
        print(f"\n{'='*60}")
        logging.info("translations.json registration")
        registered_dirs = {config.dir for config in configs + json_mods + qt_mods}
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

        if mod_type == "line":
            issues = verify_line_config(config, root)
        elif mod_type == "json":
            issues = verify_json_mod(config, root)
        elif mod_type == "json-map":
            issues = verify_json_translation_registry(config, root)
        else:
            issues = verify_qt_ts(config, root)
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
