"""检查 mods.toml 里配了 upstream 的模组，源文件在远端有没有变化。

用法：
    uv run check_upstream.py orbit-menu-ng          # 只看差异，有变化退出码 1
    uv run check_upstream.py orbit-menu-ng --write  # 拉取并覆盖本地源文件
    uv run check_upstream.py --all                  # 所有配了 upstream 的模组

默认走本地代理 http://127.0.0.1:7890，用 UPSTREAM_PROXY 覆盖（空字符串 = 直连）。
"""

import argparse
import json
import logging
import os
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
    """下载 upstream 文件，失败直接抛错（不静默当作没有更新）。"""
    proxy = os.environ.get("UPSTREAM_PROXY", DEFAULT_PROXY)
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy, "https": proxy} if proxy else {})
    )
    request = urllib.request.Request(url, headers={"User-Agent": "TranslationHub-upstream-check"})
    with opener.open(request, timeout=TIMEOUT) as response:
        return response.read()


def load_pairs(raw: bytes, label: str) -> dict[str, str]:
    """把 JSON 拍平成 key -> 译文，非扁平结构就在路径里点开。"""
    data = json.loads(raw.decode("utf-8"))
    flat: dict[str, str] = {}

    def walk(node, path: str = "") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}.{key}" if path else key)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]")
        elif isinstance(node, str):
            flat[path] = node

    walk(data)
    if not flat:
        raise ValueError(f"{label}: 没有可比较的字符串")
    return flat


def diff(local: dict[str, str], remote: dict[str, str]) -> tuple[list, list, list]:
    added = sorted(remote.keys() - local.keys())
    removed = sorted(local.keys() - remote.keys())
    changed = sorted(key for key in local.keys() & remote.keys() if local[key] != remote[key])
    return added, removed, changed


def _show(title: str, keys: list[str], remote: dict[str, str]) -> None:
    if not keys:
        return
    log.warning(f"[{title}] {len(keys)} 条")
    for key in keys[:40]:
        print(f"  {key} = {remote.get(key, '')!r}")
    if len(keys) > 40:
        print(f"  …还有 {len(keys) - 40} 条")


def process(entry: dict, write: bool) -> bool:
    """返回是否有差异。"""
    mod_path = os.path.join(repo_root(), entry["dir"])
    source_path = os.path.join(mod_path, entry["source"])
    log.info("检查模组: %s (%s)", entry["dir"], entry["upstream"])
    raw = fetch(entry["upstream"])
    remote = load_pairs(raw, "upstream")
    if not os.path.exists(source_path):
        log.warning("[缺文件] 本地源不存在: %s", entry["source"])
        if write:
            write_source(source_path, raw)
        return True
    with open(source_path, "rb") as file:
        local = load_pairs(file.read(), "local")
    added, removed, changed = diff(local, remote)
    if not (added or removed or changed):
        log.info("[OK] 与 upstream 一致（%d 条）", len(remote))
        return False
    _show("新增", added, remote)
    _show("删除", removed, remote)
    _show("英文改动", changed, remote)
    if write:
        write_source(source_path, raw)
        log.info("[写入] %s", entry["source"])
    else:
        log.warning("本地源与 upstream 不同，加 --write 拉取")
    return True


def write_source(path: str, raw: bytes) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as file:
        file.write(raw if raw.endswith(b"\n") else raw + b"\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="检查配了 upstream 的模组源文件是否有更新")
    parser.add_argument("names", nargs="*", help="模组目录或 basename，留空等于 --all")
    parser.add_argument("--all", action="store_true", help="检查所有配了 upstream 的模组")
    parser.add_argument("--write", action="store_true", help="把 upstream 内容写入本地源文件")
    parser.add_argument("--verbose", action="store_true", help="输出 DEBUG 日志")
    args = parser.parse_args()
    setup_cli_logging(args.verbose)

    entries = load_upstream_entries()
    if not args.all and args.names:
        entries = [entry for entry in entries if matches_filter(entry["dir"], args.names)]
    if not entries:
        log.warning("没有配 upstream 的模组")
        return 0

    changed = 0
    failed = 0
    for entry in entries:
        try:
            changed += 1 if process(entry, args.write) else 0
        except Exception as error:  # 网络或格式错误要说清是哪个模组
            log.error("%s: %s", entry["dir"], error)
            failed += 1
    if failed:
        return 2
    return 1 if changed else 0


if __name__ == "__main__":
    sys.exit(main())
