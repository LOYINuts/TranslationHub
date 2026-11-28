"""把翻译产物按游戏加载路径打包，供 Nexus 上传。

中文玩家既可能在英文环境（游戏读 `*_english.*` / `*_EN.*`），也可能在中文
环境（读 `*_chinese.*` / `*_ZH.*`），所以两个文件都打包，内容都是中文。

产物落到 dist/<mod>/；要 dist/<mod>.7z 就加 --archive。
打包后还会同步一份到 MO2 里对应的汉化目录（`--no-deploy` 可关），
并把汉化目录 meta.ini 的 `version=` 改成与本体一致。
汉化目录名默认从 upstream 的 MO2 目录名推导（`<目录> 汉化` / `<目录> 和光汉化`），
推不出来或对上多个时在 `mods.toml` 条目里写 `deploy = "<目录名>"` 指定。

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
import re
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass

from config import (
    ModConfig,
    ModJson,
    ModQt,
    load_repo_configs,
    matches_filter,
    setup_cli_logging,
)
from locale_utils import glob_line_sources

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


HAN_SUFFIXES = (" 和光汉化", " 汉化")


def load_deploy_meta() -> tuple[str | None, dict[str, str | bool], dict[str, str]]:
    """MO2 mods 根目录、deploy 覆盖表、各模组 upstream 的 MO2 目录名。

    `deploy` 写目录名 = 指定落点，写 `false` = 不部署（如自己维护 FOMOD 的模组）。
    """
    with open(os.path.join(REPO, "mods.toml"), "rb") as file:
        data = tomllib.load(file)
    roots = data.get("upstream", {}).get("local_roots", [])
    deploy: dict[str, str | bool] = {}
    upstream: dict[str, str] = {}
    for kind in ("line", "json", "qt"):
        for item in data.get(kind, []):
            if "deploy" in item:
                deploy[item["dir"]] = item["deploy"]
            target = item.get("upstream")
            if target and not target.startswith(("http://", "https://")):
                upstream.setdefault(item["dir"], target.split("/")[0])
    return (roots[0] if roots else None), deploy, upstream


def resolve_deploy(mod_dir: str, root: str | None, deploy: dict[str, str | bool],
                   upstream: dict[str, str]) -> str | None:
    """找到该模组在 MO2 里的汉化目录；找不到或对上多个就返回 None。"""
    if not root or not os.path.isdir(root):
        return None
    override = deploy.get(mod_dir)
    if isinstance(override, str):
        path = os.path.join(root, override)
        return path if os.path.isdir(path) else None
    base = upstream.get(mod_dir)
    if not base:
        return None
    folded = base.casefold()
    exact, prefixed = [], []
    for name in os.listdir(root):
        if not os.path.isdir(os.path.join(root, name)):
            continue
        for suffix in HAN_SUFFIXES:
            if not name.endswith(suffix):
                continue
            stem = name[: -len(suffix)].casefold()
            if len(stem) >= 5 and folded == stem:
                exact.append(os.path.join(root, name))
            elif len(stem) >= 5 and folded.startswith(stem):
                prefixed.append(os.path.join(root, name))
            break
    hits = exact or prefixed
    return hits[0] if len(hits) == 1 else None


def read_version(meta_path: str) -> str | None:
    """meta.ini 里的 version=；文件或字段缺失就返回 None。"""
    try:
        # newline="" 保住原有的 CRLF，不能依赖默认的通用换行（会把 \r 吃掉）
        with open(meta_path, encoding="utf-8", errors="surrogateescape", newline="") as file:
            text = file.read()
    except OSError:
        return None
    match = re.search(r"^version=([^\r\n]*)", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def sync_version(target: str, base: str) -> None:
    """汉化目录 meta.ini 的 version 跟本体对齐，MO2 列表才不会显示旧版本。"""
    version = read_version(os.path.join(base, "meta.ini"))
    if not version:
        log.debug("[版本] %s: 本体没有 version=，跳过", os.path.basename(base))
        return
    path = os.path.join(target, "meta.ini")
    if read_version(path) == version:
        return
    try:
        with open(path, encoding="utf-8", errors="surrogateescape", newline="") as file:
            text = file.read()
    except OSError:
        text = ""
    if re.search(r"^version=", text, re.MULTILINE):
        text = re.sub(r"^version=[^\r\n]*", f"version={version}", text, count=1, flags=re.MULTILINE)
    elif "[General]" in text:
        text = text.replace("[General]", f"[General]\r\nversion={version}", 1)
    else:
        text = f"[General]\r\nversion={version}\r\n" + text
    with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as file:
        file.write(text)
    log.info("[版本] %s: version=%s", os.path.basename(target), version)


def deploy_to(stage: str, target: str) -> int:
    """把 dist 内容覆盖拷贝到汉化目录，只覆盖同名文件。"""
    copied = 0
    for folder, _, files in os.walk(stage):
        for name in files:
            source = os.path.join(folder, name)
            relative = os.path.relpath(source, stage)
            destination = os.path.join(target, relative)
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(source, destination)
            copied += 1
    return copied


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
    if glob.has_magic(cfg.source) or not os.path.splitext(cfg.output)[1]:
        # glob 型：产物是平铺的 <源名>_zh<扩展名>，落在 output 目录
        if cfg.package:
            return _resolve(cfg, cfg.output, cfg.package)
        items = []
        mod_path = os.path.join(REPO, cfg.dir)
        for source in glob_line_sources(mod_path, cfg.source):
            stem, ext = os.path.splitext(os.path.basename(source))
            built = os.path.normpath(os.path.join(cfg.output, f"{stem}_zh{ext}"))
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
        # qm 是独立产物，打包的对象是它而不是 ts
        return _resolve(cfg, cfg.qm or cfg.output, cfg.package)
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

    if not items:
        log.error(f"[失败] {mod_dir}: 没有可打包的产物")
        return False
    missing = [
        item.built for item in items
        if not os.path.isfile(os.path.join(REPO, mod_dir, item.built))
    ]
    if missing:
        log.error(f"[失败] {mod_dir}: 产物缺失 {', '.join(missing)}，先运行 build_all.py")
        return False

    if os.path.isdir(stage):
        shutil.rmtree(stage)

    for item in items:
        source = os.path.join(REPO, mod_dir, item.built)
        target = os.path.join(stage, item.package_path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(source, target)
        log.debug(f"    {item.built} -> {item.package_path}")

    log.info(f"[OK] {mod_dir}: {len(items)} 个文件 -> dist/{mod_name}/")

    if archive and seven_zip:
        archive_path = os.path.join(DIST, f"{mod_name}.7z")
        if os.path.exists(archive_path):
            os.remove(archive_path)
        result = subprocess.run(
            [seven_zip, "a", "-t7z", "-mx=9", archive_path, "."],
            cwd=stage, capture_output=True, text=True, check=False,
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
    parser.add_argument("--no-deploy", action="store_true", help="不同步到 MO2 汉化目录")
    parser.add_argument("--verbose", action="store_true", help="输出 DEBUG 日志")
    parser.add_argument("--self-check", action="store_true", help="运行打包逻辑自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        return 0

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
        command = [sys.executable, os.path.join(REPO, "build_all.py")] + [c.dir for c in targets]
        result = subprocess.run(command, cwd=REPO, check=False)
        if result.returncode != 0:
            log.error("构建失败，终止打包")
            return 1

    if not args.list:
        os.makedirs(DIST, exist_ok=True)
    else:
        log.info("--list：只列计划，不写 dist，不部署")

    # 同一个模组目录下的多个配置条目要合成一个包
    grouped: dict[str, list[PackItem]] = {}
    skipped: set[str] = set()
    for cfg in targets:
        items = plan_for(cfg)
        if items:
            grouped.setdefault(cfg.dir, []).extend(items)
        else:
            skipped.add(cfg.dir)

    for mod_dir in sorted(skipped - set(grouped)):
        log.info(f"[跳过] {mod_dir}: 未配置 package，没有可打包的产物")

    if not grouped:
        log.error("没有可打包的产物")
        return 1

    ok = 0
    root, deploy, upstream = load_deploy_meta()
    failed_deploy = []
    for mod_dir, items in grouped.items():
        if not pack_group(mod_dir, items, args.archive, seven_zip, args.list):
            continue
        ok += 1
        if args.no_deploy:
            continue
        if deploy.get(mod_dir) is False:
            log.info(f"[{'部署计划' if args.list else '部署'}] {mod_dir}: 跳过（mods.toml 里 deploy = false）")
            continue
        target = resolve_deploy(mod_dir, root, deploy, upstream)
        if not target:
            message = (
                f"[{'部署计划' if args.list else '部署'}] {mod_dir}: 找不到对应汉化目录，"
                "请在 mods.toml 里加 deploy = \"<目录名>\""
            )
            if args.list:
                log.warning(message)
            else:
                log.error(message)
                failed_deploy.append(mod_dir)
            continue
        if args.list:
            planned = [item.package_path for item in items]
            existing = [p for p in planned if os.path.exists(os.path.join(target, p))]
            log.info(
                f"[部署计划] {mod_dir} -> {os.path.basename(target)}/（覆盖 {len(existing)} / 新增 "
                f"{len(planned) - len(existing)}）"
            )
            for path in planned:
                log.debug(f"    {'覆盖' if path in existing else '新增'} {path}")
            continue
        count = deploy_to(os.path.join(DIST, dist_name(mod_dir)), target)
        log.info(f"[部署] {mod_dir} -> {os.path.basename(target)}/（{count} 个文件）")
        base = os.path.join(root, upstream[mod_dir]) if root and mod_dir in upstream else None
        if base and os.path.isdir(base):
            sync_version(target, base)

    log.info(f"打包完成：{ok}/{len(grouped)}")
    if failed_deploy:
        return 1
    return 0 if ok == len(grouped) else 1


def _self_check() -> None:
    """产物缺失必须失败，且不能清空已有 dist 目录。"""
    global DIST
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        saved = DIST
        DIST = tmp
        log.disabled = True
        try:
            assert pack_group(
                "__self_check__",
                [PackItem("missing.txt", "x/missing.txt")],
                False, None, False,
            ) is False
        finally:
            log.disabled = False
            DIST = saved

    with tempfile.TemporaryDirectory() as tmp:
        log.disabled = True
        try:
            base = os.path.join(tmp, "base")
            target = os.path.join(tmp, "target")
            os.makedirs(base)
            os.makedirs(target)
            with open(os.path.join(base, "meta.ini"), "w", encoding="utf-8", newline="") as file:
                file.write("[General]\r\nversion=2.0\r\n")
            with open(os.path.join(target, "meta.ini"), "w", encoding="utf-8", newline="") as file:
                file.write("[General]\r\nmodid=0\r\nversion=1.0\r\n")
            sync_version(target, base)
            assert read_version(os.path.join(target, "meta.ini")) == "2.0"
            with open(os.path.join(target, "meta.ini"), "rb") as file:
                raw = file.read()
            assert b"modid=0" in raw, "只改 version 行"
            assert raw.count(b"\n") == raw.count(b"\r\n"), "CRLF 不能变成 LF"
            os.remove(os.path.join(base, "meta.ini"))
            sync_version(target, base)
            assert read_version(os.path.join(target, "meta.ini")) == "2.0", "本体无 version 时不碰"
        finally:
            log.disabled = False
    print("self-check OK")


if __name__ == "__main__":
    raise SystemExit(main())
