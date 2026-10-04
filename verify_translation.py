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
import logging
log = logging.getLogger(__name__)  # ponytail: named logger per spec

from locale_utils import read_text, load_json
from build_all import flatten_json_values, render_json_one, render_line_group, render_line_one, render_qt_one, translation_data
from config import setup_cli_logging
setup_cli_logging()  # ponytail: single logging setup


# ── 从 config.py 加载配置 ─────────────────────────────────────────────────

from config import ModJson, ModQt, load_repo_configs, matches_filter
from sync_translation import find_missing_keys, find_missing_json, find_missing_qt

# ── 校验函数 ─────────────────────────────────────────────────────────────────


def verify_line_single(config, root: str) -> list[str]:
    """Single path: sync diff + render rebuild. ponytail: kills guess + 3-way split."""
    mod_path = os.path.join(root, config.dir)
    if not os.path.isdir(mod_path):
        return [f"[错误] 目录不存在: {mod_path}"]
    try:
        missing, _ = find_missing_keys(config, mod_path)
        expected, _ = render_line_one(config, root)
    except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"[错误] 无法重建行文件: {exc}"]
    issues = []
    if missing:
        issues.append(f"[缺失] {len(missing)} 条：{', '.join(sorted(missing)[:10])}")
    out_path = os.path.join(mod_path, config.output)
    if not os.path.exists(out_path):
        issues.append(f"[缺失] 未找到中文输出文件: {out_path}")
    elif read_text(out_path) != expected:
        issues.append("[过期] 中文文件与 translations.json 构建结果不一致")
    return issues or ["[OK] 全部检查通过"]


def verify_line_group(config, root: str) -> list[str]:
    """Verify glob line task via render rebuild only."""
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


def verify_line_config(config, root: str) -> list[str]:
    if glob.has_magic(config.source):
        return verify_line_group(config, root)
    return verify_line_single(config, root)

def verify_json_mod(mod_config, root: str) -> list[str]:
    """Coverage via sync diff, freshness via render rebuild. ponytail: extra keys ride along per dir."""
    mod_path = os.path.join(root, mod_config.dir)
    try:
        missing, _ = find_missing_json(mod_config, mod_path)
        expected, _ = render_json_one(mod_config, root)
        actual = load_json(os.path.join(mod_path, mod_config.output))
    except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"[错误] JSON 无法验证: {exc}"]
    issues = []
    if missing:
        issues.append(f"[缺失] {len(missing)} 个翻译键：{', '.join(sorted(missing)[:10])}")
    if actual != expected:
        issues.append("[过期] 中文 JSON 与 translations.json 构建结果不一致")
    return issues or ["[OK] 全部检查通过"]


def verify_json_dir_extra(all_json: list, root: str, filters) -> list[str]:
    """One extra-key pass per dir for shared translations.json. Runs only on full verify."""
    seen: dict[str, list] = {}
    for cfg in all_json:
        seen.setdefault(cfg.dir, []).append(cfg)
    issues = []
    for mod_dir, group in sorted(seen.items()):
        if filters and not matches_filter(mod_dir, filters):
            continue
        if len(group) < 2:
            continue
        mod_path = os.path.join(root, mod_dir)
        try:
            translated_keys: set[str] = set()
            want: set[str] = set()
            for cfg in group:
                translated_keys.update(flatten_json_values(translation_data(cfg, root)))
                src = flatten_json_values(load_json(os.path.join(mod_path, cfg.source)))
                want.update(k for k, v in src.items() if isinstance(v, str))
        except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            issues.append(f"[错误] {mod_dir}: {exc}")
            continue
        extra = sorted(translated_keys - want)
        if extra:
            issues.append(f"[多余] {mod_dir}: {len(extra)} 个键：{', '.join(extra[:5])}")
    return issues




def verify_qt_ts(config: ModQt, root: str) -> list[str]:
    """Coverage via sync diff, freshness via render rebuild."""
    mod_path = os.path.join(root, config.dir)
    try:
        missing, _ = find_missing_qt(config, mod_path)
        expected, _ = render_qt_one(config, root)
        actual = read_text(os.path.join(mod_path, config.output))
    except (OSError, ET.ParseError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"[错误] Qt TS 无法验证: {exc}"]
    issues = []
    if missing:
        issues.append(f"[缺失] {len(missing)} 条 Qt 消息未登记")
    if actual != expected:
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


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="校验翻译完整性：sync 缺键 + render 新鲜度")
    parser.add_argument("mods", nargs="*", help="模组名（完整路径或 basename），留空校验全部")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args(argv)
    if args.self_check:
        _self_check()
        return 0
    root = os.path.dirname(os.path.abspath(__file__))
    filters = set(args.mods) if args.mods else None
    configs, json_mods, qt_mods = load_repo_configs(root)
    tasks = ([(config.dir, "line", config) for config in configs]
             + [(config.dir, "json", config) for config in json_mods]
             + [(config.dir, "qt", config) for config in qt_mods])
    if filters and not any(matches_filter(mod_dir, filters) for mod_dir, _, _ in tasks):
        log.error(f"未找到模组: {', '.join(sorted(filters))}")
        return 2
    exit_code = 0
    if filters is None:
        print(f"\n{'='*60}")
        log.info("translations.json registration")
        registered_dirs = {config.dir for config in configs + json_mods + qt_mods}
        for issue in verify_translation_registry(root, registered_dirs):
            if issue.startswith("[OK]"):
                log.info(issue)
            else:
                log.error(issue)
                exit_code = 1

    for mod_dir, mod_type, config in tasks:
        if not matches_filter(mod_dir, filters):
            continue

        print(f"\n{'='*60}")
        log.info(f"{mod_dir} ({mod_type})")
        print(f"{'='*60}")

        if mod_type == "line":
            issues = verify_line_config(config, root)
        elif mod_type == "json":
            issues = verify_json_mod(config, root)
        else:
            issues = verify_qt_ts(config, root)
        for issue in issues:
            if issue.startswith("[OK]"):
                log.info(issue)
            else:
                log.error(issue)
                exit_code = 1

    for issue in verify_json_dir_extra(json_mods, root, filters):
        log.error(issue)
        exit_code = 1
    print(f"\n{'='*60}")
    if exit_code:
        log.error("存在未通过项，请修复。")
    else:
        log.info("全部通过 [OK]")
    print(f"{'='*60}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
