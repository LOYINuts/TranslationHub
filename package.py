"""把翻译产物按游戏加载路径打包，供 Nexus 上传。

中文玩家既可能在英文环境（游戏读 `*_english.*` / `*_EN.*`），也可能在中文
环境（读 `*_chinese.*` / `*_ZH.*`），所以两个文件都打包，内容都是中文。

产物落到 dist/<mod>/；要 dist/<mod>.7z 就加 --archive。

用法:
    uv run package.py achievementinjector
    uv run package.py achievementinjector obodyng
    uv run package.py --all
    uv run package.py --all --archive     # 额外压成 dist/<mod>.7z
    uv run package.py --all --list        # 只列出会打包什么，不执行
"""

from __future__ import annotations

import argparse
import glob
import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass

from config import ModConfig, ModJson, ModQt, load_repo_configs, matches_filter, setup_cli_logging

log = logging.getLogger(__name__)

REPO = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(REPO, "dist")

# 未配置 package 时的默认落点目录
DEFAULT_DIR = "interface/translations"


@dataclass
class PackItem:
    """一个待打包的文件：把 built 的内容写到 package_path。"""

    built: str
    package_path: str


def dist_name(mod_dir: str) -> str:
    """dist 目录名。

    嵌套目录（如 statstracker/localization）的 basename 会撞名，所以把
    menu_translation/ 之后的各级用 - 连起来。
    """
    parts = mod_dir.replace("\\", "/").rstrip("/").split("/")
    if len(parts) > 1:
        parts = parts[1:]
    return "-".join(parts)


def _resolve(cfg, built: str, targets: list[str]) -> list[PackItem]:
    """把 package 配置解析成 (产物, 落点) 列表。

    package 里写的是落点路径；写目录（以 / 结尾或无扩展名）时，用 built 的
    文件名补全。
    """
    items = []
    for target in targets:
        if target.endswith("/") or not os.path.splitext(target)[1]:
            filename = os.path.basename(built)
            target = f"{target.rstrip('/')}/{filename}"
        items.append(PackItem(built=built, package_path=target))
    return items



# 插件按固定文件名读取，不认语言后缀，只放源文件名那一份
PLUGIN_PREFIXES = ("skse/", "viny mods/", "nemesis_engine/")


def _is_plugin_path(path: str) -> bool:
    return path.replace("\\", "/").lower().startswith(PLUGIN_PREFIXES)


def _default_items(built: str, source: str, output: str, mod_dir: str) -> list[PackItem]:
    """未配 package 时的落点。

    落点文件名用**源文件名**，也就是游戏本来就认的那个名字（如 Language.json、
    OBody_ENGLISH.txt），内容换成译文。

    interface/translations/ 下游戏按语言挑文件，英文名与中文名各需要一份，
    所以额外再落一份产物名。SKSE/、Viny Mods/ 下插件按固定文件名读取，
    多放一份中文名不会被加载，因此只出源文件名。
    """
    directory, output_name = os.path.split(output)
    if not directory:
        directory = DEFAULT_DIR
        log.warning(
            f"  [未配 package] {mod_dir}: output 没有游戏路径，按 {DEFAULT_DIR}/ 推测"
        )
    source_name = os.path.basename(source)

    items = [PackItem(built=built, package_path=f"{directory}/{source_name}")]
    if not _is_plugin_path(output) and output_name != source_name:
        items.append(PackItem(built=built, package_path=f"{directory}/{output_name}"))
    return items


def plan_line(cfg: ModConfig) -> list[PackItem]:
    """line 模组的打包计划。"""
    if "*" in cfg.source or not os.path.splitext(cfg.output)[1]:
        # glob 型：产物是平铺的 <源名>_zh<扩展名>，与源同目录
        if cfg.package:
            return _resolve(cfg, cfg.output, cfg.package)
        items = []
        mod_path = os.path.join(REPO, cfg.dir)
        for source in sorted(glob.glob(os.path.join(mod_path, cfg.source), recursive=True)):
            if not os.path.isfile(source):
                continue
            stem, ext = os.path.splitext(os.path.basename(source))
            if stem.endswith("_zh"):
                continue
            built = f"{stem}_zh{ext}"
            # 游戏读的是源文件名，打包时去掉 _zh 后缀，与源同名
            items.append(PackItem(built=built, package_path=f"{stem}{ext}"))
        return items

    if cfg.package:
        return _resolve(cfg, cfg.output, cfg.package)
    return _default_items(cfg.output, cfg.source, cfg.output, cfg.dir)


def plan_json(cfg: ModJson) -> list[PackItem]:
    if not cfg.output:
        return []
    if cfg.package:
        return _resolve(cfg, cfg.output, cfg.package)
    return _default_items(cfg.output, cfg.source, cfg.output, cfg.dir)


def plan_qt(cfg: ModQt) -> list[PackItem]:
    if cfg.package:
        return _resolve(cfg, cfg.output, cfg.package)
    return []


def plan_for(cfg) -> list[PackItem]:
    if isinstance(cfg, ModConfig):
        return plan_line(cfg)
    if isinstance(cfg, ModJson):
        return plan_json(cfg)
    if isinstance(cfg, ModQt):
        return plan_qt(cfg)
    return []


def find_seven_zip() -> str | None:
    for name in ("7z", "7za", "7zr"):
        found = shutil.which(name)
        if found:
            return found
    return None


def pack_group(mod_dir: str, items: list[PackItem], archive: bool,
               seven_zip: str | None, dry_run: bool) -> bool:
    """把一个模组的所有产物打到同一个 dist 目录。"""
    mod_name = dist_name(mod_dir)
    stage = os.path.join(DIST, mod_name)

    if dry_run:
        log.info(f"[计划] {mod_dir} -> dist/{mod_name}/")
        for item in items:
            log.info(f"    {item.built}  ->  {item.package_path}")
        return True

    if os.path.isdir(stage):
        shutil.rmtree(stage)

    copied = 0
    missing = []
    for item in items:
        source = os.path.join(REPO, mod_dir, item.built)
        if not os.path.isfile(source):
            missing.append(item.built)
            continue
        target = os.path.join(stage, item.package_path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(source, target)
        copied += 1
        log.debug(f"    {item.built} -> {item.package_path}")

    if missing:
        log.warning(f"  [缺失] {mod_dir}: {', '.join(missing)}，先运行 build_all.py")

    if copied == 0:
        log.error(f"[失败] {mod_dir}: 没有可打包的产物")
        return False

    log.info(f"[OK] {mod_dir}: {copied} 个文件 -> dist/{mod_name}/")

    if archive and seven_zip:
        archive_path = os.path.join(DIST, f"{mod_name}.7z")
        if os.path.exists(archive_path):
            os.remove(archive_path)
        result = subprocess.run(
            [seven_zip, "a", "-t7z", "-mx=9", archive_path, "."],
            cwd=stage, capture_output=True, text=True,
        )
        if result.returncode != 0:
            log.error(f"[失败] 压缩 {mod_name}: {result.stderr.strip()[:200]}")
            return False
        log.info(f"[OK] dist/{mod_name}.7z ({os.path.getsize(archive_path) // 1024} KB)")

    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="按游戏加载路径打包翻译产物",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("mods", nargs="*", help="模组目录名或 basename")
    parser.add_argument("--all", action="store_true", help="打包全部已登记模组")
    parser.add_argument("--archive", action="store_true", help="额外压成 dist/<mod>.7z")
    parser.add_argument("--list", action="store_true", help="只列出打包计划，不执行")
    parser.add_argument("--skip-build", action="store_true", help="不重新构建，直接用现有产物")
    parser.add_argument("--verbose", action="store_true", help="输出 DEBUG 日志")
    args = parser.parse_args()

    setup_cli_logging(args.verbose)
    line_mods, json_mods, qt_mods = load_repo_configs(REPO)
    configs = list(line_mods) + list(json_mods) + list(qt_mods)

    if not args.all and not args.mods:
        parser.error("请指定模组名，或使用 --all")

    targets = [c for c in configs if args.all or matches_filter(c.dir, args.mods)]
    if not targets:
        log.error("没有匹配的模组")
        return 1

    seven_zip = None if (args.list or not args.archive) else find_seven_zip()
    if args.archive and not args.list and not seven_zip:
        log.error("未找到 7z 命令，请安装 7-Zip 或去掉 --archive")
        return 1

    if not args.skip_build and not args.list:
        log.info("先构建产物")
        from build_all import main as build_main
        build_args = ["build_all.py"] + [c.dir for c in targets]
        old_argv = sys.argv
        try:
            sys.argv = build_args
            if build_main() != 0:
                log.error("构建失败，终止打包")
                return 1
        finally:
            sys.argv = old_argv

    if not args.list:
        os.makedirs(DIST, exist_ok=True)

    # 同一个模组目录下的多个配置条目要合成一个包
    grouped: dict[str, list[PackItem]] = {}
    for cfg in targets:
        items = plan_for(cfg)
        if items:
            grouped.setdefault(cfg.dir, []).extend(items)

    ok = 0
    for mod_dir, items in grouped.items():
        if pack_group(mod_dir, items, args.archive, seven_zip, args.list):
            ok += 1

    log.info(f"打包完成：{ok}/{len(grouped)}")
    return 0 if ok == len(grouped) else 1


if __name__ == "__main__":
    raise SystemExit(main())
