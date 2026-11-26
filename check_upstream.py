"""拉上游源文件覆盖本地，再交给 sync_translation 判断变没变。

不解析格式：源文件原样覆盖，`sync_translation.py --check` 按条目类型自己比缺键 / 原文变更 / 无基线。

用法：
    uv run check_upstream.py orbit-menu-ng          # 拉取、有变化就覆盖、再跑 --check
    uv run check_upstream.py orbit-menu-ng --dry    # 只比字节，不写文件
    uv run check_upstream.py --all                  # 所有配了 upstream 的模组

退出码沿用 sync 的语义：0 无差异、1 有差异、2 网络或写入失败。
默认走本地代理 http://127.0.0.1:7890，用 UPSTREAM_PROXY 覆盖（空字符串 = 直连）。
"""

import argparse
import logging
import os
import subprocess
import sys
import tomllib
import urllib.request

from config import matches_filter, repo_root, setup_cli_logging

log = logging.getLogger("check_upstream")
DEFAULT_PROXY = "http://127.0.0.1:7890"
TIMEOUT = 30


def load_upstream_entries() -> list[dict]:
    """mods.toml 里带 upstream 字段的条目。"""
    with open(os.path.join(repo_root(), "mods.toml"), "rb") as file:
        data = tomllib.load(file)
    entries = []
    for kind in ("line", "json", "qt"):
        entries.extend(item for item in data.get(kind, []) if item.get("upstream"))
    return entries


def fetch(url: str) -> bytes:
    """下载 upstream 源文件，失败直接抛错（不静默当作没有更新）。"""
    proxy = os.environ.get("UPSTREAM_PROXY", DEFAULT_PROXY)
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy, "https": proxy} if proxy else {})
    )
    request = urllib.request.Request(url, headers={"User-Agent": "TranslationHub-upstream-check"})
    with opener.open(request, timeout=TIMEOUT) as response:
        return response.read()


def run_check(mod_dir: str) -> int:
    """写完后用 sync_translation 判断差异，返回它的退出码。"""
    result = subprocess.run(
        [sys.executable, "sync_translation.py", mod_dir, "--check"], cwd=repo_root()
    )
    return result.returncode


def process(entry: dict, dry: bool) -> int:
    """返回该模组的退出码：0 无差异、1 有差异、2 失败。"""
    source_path = os.path.join(repo_root(), entry["dir"], entry["source"])
    log.info("检查模组: %s (%s)", entry["dir"], entry["upstream"])
    raw = fetch(entry["upstream"])
    local = b""
    if os.path.exists(source_path):
        with open(source_path, "rb") as file:
            local = file.read()
    if local == raw:
        log.info("[OK] 与 upstream 一致")
        return 0
    log.warning(
        "[变化] upstream %d 字节 / 本地 %d 字节", len(raw), len(local)
    )
    if dry:
        log.warning("--dry：没有写入，去掉 --dry 才覆盖")
        return 1
    os.makedirs(os.path.dirname(source_path), exist_ok=True)
    with open(source_path, "wb") as file:
        file.write(raw)
    log.info("[写入] %s", entry["source"])
    return run_check(entry["dir"])


def main() -> int:
    parser = argparse.ArgumentParser(description="拉取 upstream 源文件并检查译文差异")
    parser.add_argument("names", nargs="*", help="模组目录或 basename，留空等于 --all")
    parser.add_argument("--all", action="store_true", help="检查所有配了 upstream 的模组")
    parser.add_argument("--dry", action="store_true", help="只比字节，不覆盖本地源")
    parser.add_argument("--verbose", action="store_true", help="输出 DEBUG 日志")
    args = parser.parse_args()
    setup_cli_logging(args.verbose)

    entries = load_upstream_entries()
    if not args.all and args.names:
        entries = [entry for entry in entries if matches_filter(entry["dir"], args.names)]
    if not entries:
        log.warning("没有配 upstream 的模组")
        return 0

    codes = []
    for entry in entries:
        try:
            codes.append(process(entry, args.dry))
        except Exception as error:  # 网络或写入错误要说清是哪个模组
            log.error("%s: %s", entry["dir"], error)
            codes.append(2)
    if 2 in codes:
        return 2
    return 1 if 1 in codes else 0


if __name__ == "__main__":
    sys.exit(main())
