"""
翻译校验脚本：检查单个模组或所有模组的翻译完整性。

用法：
  uv run verify_translation.py              # 校验所有模组
  uv run verify_translation.py FUCKRACE     # 校验指定模组
  uv run verify_translation.py FUCK FUCKRACE  # 校验多个

检查项：
  - 翻译键覆盖
  - 转义、printf/Python/Qt 占位符和标记
  - 生成产物是否等于当前 translations.json 构建结果
  - translations.json 键覆盖、格式和构建产物状态
  - Eslifer Qt TS 结构和占位符
"""

import glob
import json
import logging
import os
import xml.etree.ElementTree as ET

from build_all import (
    dir_extra_keys,
    render_json_one,
    render_line_group,
    render_line_one,
    render_qt_one,
)

# ── 从 config.py 加载配置 ─────────────────────────────────────────────────
from config import ModConfig, ModJson, ModQt, load_repo_configs, matches_filter, setup_cli_logging
from locale_utils import load_json, read_text
from source_baseline import (
    baseline_issues,
    baseline_path,
    compare_baseline,
    source_key,
    update_baseline,
)
from sync_translation import find_missing_json, find_missing_keys, find_missing_qt

log = logging.getLogger(__name__)  # ponytail: named logger per spec

# ── 校验函数 ─────────────────────────────────────────────────────────────────


def verify_line_single(config, root: str) -> list[str]:
    """Single path: sync diff + render rebuild. ponytail: kills guess + 3-way split."""
    mod_path = os.path.join(root, config.dir)
    if not os.path.isdir(mod_path):
        return [f"[错误] 目录不存在: {mod_path}"]
    try:
        missing, _, current = find_missing_keys(config, mod_path)
        expected, _, _ = render_line_one(config, root)
        baseline = baseline_issues("line", config, mod_path, current)
    except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"[错误] 无法重建行文件: {exc}"]
    issues = list(baseline)
    if missing:
        issues.append(f"[缺失] {len(missing)} 条：{', '.join(sorted(missing)[:10])}")
    out_path = os.path.join(mod_path, config.output)
    if not os.path.exists(out_path):
        issues.append(f"[缺失] 未找到中文输出文件: {out_path}")
    elif read_text(out_path) != expected:
        issues.append("[过期] 中文文件与 translations.json 构建结果不一致")
    return issues or ["[OK] 全部检查通过"]


def verify_line_group(config, root: str) -> list[str]:
    """Verify glob line task via render rebuild and baseline."""
    try:
        _, _, current = find_missing_keys(config, os.path.join(root, config.dir))
        artifacts, _, _ = render_line_group(config, root)
        baseline = baseline_issues("line", config, os.path.join(root, config.dir), current)
    except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"[错误] 无法重建行文件: {exc}"]
    expected = {os.path.normcase(path): content for path, content in artifacts}
    issues = list(baseline)
    for path, content in artifacts:
        if not os.path.exists(path):
            issues.append(f"[缺失] {path}")
        elif read_text(path) != content:
            issues.append(f"[过期] {path}")
    output_root = os.path.join(root, config.dir, config.output)
    expected_suffixes = {os.path.splitext(path)[1].lower() for path in expected}
    for dirpath, _, filenames in os.walk(output_root):
        for name in filenames:
            path = os.path.join(dirpath, name)
            if os.path.splitext(name)[1].lower() in expected_suffixes and os.path.normcase(path) not in expected:
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
        missing, _, current = find_missing_json(mod_config, mod_path)
        expected, _, _ = render_json_one(mod_config, root)
        actual = load_json(os.path.join(mod_path, mod_config.output))
        baseline = baseline_issues("json", mod_config, mod_path, current)
    except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"[错误] JSON 无法验证: {exc}"]
    issues = list(baseline)
    if missing:
        issues.append(f"[缺失] {len(missing)} 个翻译键：{', '.join(sorted(missing)[:10])}")
    if actual != expected:
        issues.append("[过期] 中文 JSON 与 translations.json 构建结果不一致")
    return issues or ["[OK] 全部检查通过"]


def verify_dir_extra_keys(configs, root: str, filters) -> list[str]:
    """Report translation keys no config in the same directory consumes."""
    return [
        f"[多余] {mod_dir}: {len(extra)} 个未使用键：{', '.join(extra[:5])}"
        for mod_dir, extra in dir_extra_keys(root, configs, filters).items()
    ]




def verify_qt_ts(config: ModQt, root: str) -> list[str]:
    """Coverage via sync diff, freshness via render rebuild."""
    mod_path = os.path.join(root, config.dir)
    try:
        missing, _ = find_missing_qt(config, mod_path)
        expected, _, _ = render_qt_one(config, root)
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
    def normalize(path: str) -> str:
        return os.path.normcase(os.path.normpath(path))

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
            "translations.json": {"key": "值 %1", "stale": "旧键 %1"},
            "zh.json": {"key": "stale %1"},
        }
        for name, value in data.items():
            with open(os.path.join(mod_path, name), "w", encoding="utf-8") as file:
                json.dump(value, file, ensure_ascii=False)
        cfg = ModJson("mod", "en.json", "zh.json")
        key = source_key("json", cfg)
        update_baseline(mod_path, key, {"key": "Value %1"}, replace=True)
        issues = verify_json_mod(cfg, root)
        assert any(issue.startswith("[过期]") for issue in issues), issues
        assert not any(
            issue.startswith("[变更]") or issue.startswith("[未基线]") for issue in issues
        ), issues

        changed, unbaselined, initialized = compare_baseline(
            mod_path, key, {"key": "Changed"}
        )
        assert initialized and changed == {"key": ("Value %1", "Changed")}, changed
        assert not unbaselined, unbaselined

        changed, unbaselined, _ = compare_baseline(
            mod_path, key, {"key": "Value %1", "new": "N"}
        )
        assert not changed and unbaselined == ["new"], (changed, unbaselined)

        update_baseline(mod_path, key, {"key": "Changed"}, replace=True)
        changed, unbaselined, initialized = compare_baseline(
            mod_path, key, {"key": "Changed"}
        )
        assert initialized and not changed and not unbaselined

        os.remove(baseline_path(mod_path))
        changed, unbaselined, initialized = compare_baseline(
            mod_path, key, {"key": "Changed"}
        )
        assert not initialized and sorted(unbaselined) == ["key"]

        extra = verify_dir_extra_keys([ModJson("mod", "en.json", "zh.json")], root, None)
        assert extra and "stale" in extra[0], extra
        assert find_unregistered_translation_dirs(root, set()) == ["mod"]
        assert find_unregistered_translation_dirs(root, {"mod"}) == []

        # A glob line config and a json config may share one translations.json.
        shared = os.path.join(root, "shared")
        os.makedirs(os.path.join(shared, "src"))
        with open(os.path.join(shared, "src", "a.ini"), "w", encoding="utf-8") as file:
            file.write("k|v\n")
        with open(os.path.join(shared, "en.json"), "w", encoding="utf-8") as file:
            json.dump({"greeting": "Hi"}, file)
        line_cfg = ModConfig("shared", "**/*.ini", "zh", sep="|")
        json_cfg = ModJson("shared", "en.json", "zh.json")
        share_path = os.path.join(shared, "translations.json")
        with open(share_path, "w", encoding="utf-8") as file:
            json.dump({"src/a.ini::k#0": "值", "greeting": "你好"}, file, ensure_ascii=False)
        assert verify_dir_extra_keys([line_cfg, json_cfg], root, None) == [], "共享目录不应误报"
        with open(share_path, "w", encoding="utf-8") as file:
            json.dump({"src/a.ini::k#0": "值", "greeting": "你好", "orphan": "孤儿"}, file, ensure_ascii=False)
        shared_extra = verify_dir_extra_keys([line_cfg, json_cfg], root, None)
        assert shared_extra and "orphan" in shared_extra[0], shared_extra
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
    setup_cli_logging()  # ponytail: logging set up in main, not at import
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

    for issue in verify_dir_extra_keys(configs + json_mods + qt_mods, root, filters):
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
