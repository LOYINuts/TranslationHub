"""英文源基线：记录上次确认时每个已翻译键对应的英文原文。

基线文件位于各 line/json 模组目录下的 .translations.source.json，由
sync_translation.py 生成和维护，提交到仓库，不要手改。
Qt 不使用基线：Qt 的键就是英文原文，源文一变就会同时报缺失和多余键。
"""

import json
import os

from locale_utils import load_json

BASELINE_NAME = ".translations.source.json"
BASELINE_VERSION = 1
_COMMENT = "由 sync_translation.py 维护，请勿手改。记录上次确认时每个已翻译键的英文原文。"


def baseline_path(mod_path: str) -> str:
    return os.path.join(mod_path, BASELINE_NAME)


def _normalize(value: str) -> str:
    return value.replace("\\", "/")


def source_key(kind: str, cfg) -> str:
    """Stable identity for one configured source inside one mod directory."""
    return f"{kind}:{_normalize(cfg.dir)}:{_normalize(cfg.source)}"


def _validate_sources(data: dict, path: str) -> dict:
    sources = data.get("sources")
    if not isinstance(sources, dict):
        raise ValueError(f"英文基线缺少 sources 对象: {path}")
    for source, mapping in sources.items():
        if not isinstance(source, str) or not isinstance(mapping, dict):
            raise ValueError(f"英文基线格式无效: {path}")
        for key, value in mapping.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError(f"英文基线条目格式无效: {path}")
    return sources


def load_baseline(mod_path: str) -> dict:
    """Load one mod's baseline; a missing file is an empty baseline."""
    path = baseline_path(mod_path)
    if not os.path.exists(path):
        return {"version": BASELINE_VERSION, "sources": {}}
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"英文基线必须是 JSON 对象: {path}")
    if data.get("version") != BASELINE_VERSION:
        raise ValueError(f"英文基线版本不支持: {path}")
    _validate_sources(data, path)
    return data


def save_baseline(mod_path: str, data: dict) -> None:
    """Write the baseline atomically, with stable key order and LF newlines."""
    path = baseline_path(mod_path)
    sources = _validate_sources(data, path)
    payload = {"_comment": _COMMENT, "version": BASELINE_VERSION, "sources": sources}
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2, sort_keys=True)
            file.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def compare_baseline(
    mod_path: str,
    key: str,
    current: dict[str, str],
) -> tuple[dict[str, tuple[str, str]], list[str], bool]:
    """Compare current English with the last accepted baseline.

    Returns (changed {key: (old, new)}, unbaselined keys, baseline exists).
    """
    data = load_baseline(mod_path)
    stored = data["sources"].get(key)
    if stored is None:
        return {}, sorted(current), False
    changed = {
        item: (stored[item], current[item])
        for item in current
        if item in stored and stored[item] != current[item]
    }
    unbaselined = sorted(item for item in current if item not in stored)
    return changed, unbaselined, True


def update_baseline(
    mod_path: str,
    key: str,
    values: dict[str, str],
    *,
    replace: bool = False,
) -> None:
    """Seed new keys, or replace the whole source map after an explicit review."""
    path = baseline_path(mod_path)
    existed = os.path.exists(path)
    data = load_baseline(mod_path)
    if replace:
        if values:
            data["sources"][key] = dict(values)
        else:
            data["sources"].pop(key, None)
    else:
        if not values:
            return
        stored = data["sources"].setdefault(key, {})
        for item, value in values.items():
            stored.setdefault(item, value)
    if not data["sources"]:
        if existed:
            os.remove(path)
        return
    save_baseline(mod_path, data)


def _short(value: str, limit: int = 90) -> str:
    text = value.replace("\r", " ").replace("\n", " ")
    return text if len(text) <= limit else text[:limit] + "…"


def describe_baseline(
    changed: dict[str, tuple[str, str]],
    unbaselined: list[str],
    initialized: bool,
    limit: int = 10,
) -> list[str]:
    """Human-readable issue lines; no translation values are printed."""
    if not initialized:
        return ["[未基线] 缺少英文基线；先运行 sync_translation.py <mod> --accept-source 初始化"]
    lines = []
    if changed:
        lines.append(f"[变更] {len(changed)} 个已翻译键的英文原文已变化：")
        for key, (old, new) in sorted(changed.items())[:limit]:
            lines.append(f"  {key}: {_short(old)!r} -> {_short(new)!r}")
        if len(changed) > limit:
            lines.append(f"  …还有 {len(changed) - limit} 个")
    if unbaselined:
        names = sorted(unbaselined)
        lines.append(f"[未基线] {len(names)} 个已翻译键没有基线：{', '.join(names[:limit])}")
        if len(names) > limit:
            lines.append(f"  …还有 {len(names) - limit} 个")
    return lines


def baseline_issues(kind: str, cfg, mod_path: str, current: dict[str, str]) -> list[str]:
    """Compare one configured source and return issue lines."""
    if not current:
        return []
    changed, unbaselined, initialized = compare_baseline(
        mod_path, source_key(kind, cfg), current
    )
    return describe_baseline(changed, unbaselined, initialized)
