"""一次性本地门禁：自检 + 词典检查 + 同步检查 + 构建 + 校验。

用法：
  uv run check_all.py              # 全部门禁
  uv run check_all.py --self-check # 只跑四个脚本的自检
  uv run check_all.py --verbose    # DEBUG 日志

每一步都按 AGENTS.md 的 gate 顺序执行，任一非零退出码即失败。
只使用标准库；子进程直接用当前解释器，保证 uv 环境一致。
"""

import argparse
import logging
import os
import subprocess
import sys

from config import setup_cli_logging

log = logging.getLogger(__name__)

ROOT = os.path.dirname(os.path.abspath(__file__))

SELF_CHECKS = (
    ("locale_utils.py", "--self-check"),
    ("build_all.py", "--self-check"),
    ("verify_translation.py", "--self-check"),
    ("dialogue_mod_translation/translate.py", "--self-check"),
)

GATE = (
    ("dialogue_mod_translation/translate.py", "bdd", "--check"),
    ("sync_translation.py", "--all", "--check"),
    ("build_all.py",),
    ("verify_translation.py",),
)


def run(script: str, *args: str) -> int:
    """Run one project CLI with the current interpreter. Return its exit code."""
    command = [sys.executable, os.path.join(ROOT, script), *args]
    log.info("uv run %s", " ".join((script, *args)))
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        log.error("%s %s -> exit %d", script, " ".join(args), result.returncode)
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="运行全部本地门禁：自检 → bdd → sync → build → verify")
    parser.add_argument("--self-check", action="store_true", help="只运行脚本自检")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")
    args = parser.parse_args(argv)
    setup_cli_logging(verbose=args.verbose)

    steps = list(SELF_CHECKS)
    if not args.self_check:
        steps += list(GATE)

    for step in steps:
        code = run(*step)
        if code != 0:
            return code
    log.info("全部门禁通过（%d 步）", len(steps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
