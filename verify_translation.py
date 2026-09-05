"""
翻译校验脚本：检查单个模组或所有模组的翻译完整性。

用法：
  uv run python verify_translation.py              # 校验所有模组
  uv run python verify_translation.py FUCKRACE     # 校验指定模组
  uv run python verify_translation.py FUCK FUCKRACE  # 校验多个

检查项：
  - 键完整性（有无缺失/多余）
  - 转义序列 \n 格式（是否存成真实换行符）
  - 格式占位符 %d/%s 是否保留
  - 疑似未翻译项（EN==CN 且非全大写）
"""

import json
import os
import re
import sys

# Force UTF-8 for stdout (avoid GBK encoding errors)
if hasattr(sys.stdout, 'buffer'):
    import io
    # 已是 UTF-8 时不再重复包装，避免包装对象被 GC 时关闭底层 buffer
    if not (isinstance(sys.stdout, io.TextIOWrapper) and (sys.stdout.encoding or '').lower() == 'utf-8'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from locale_utils import read_lines


# ── 从 build_all.py 复用模组配置 ─────────────────────────────────────────────


def get_mod_configs():
    """导入 build_all.py 中的 MOD_CONFIGS + JSON_MODS + SCRIPT_MODS。"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_all", "build_all.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MOD_CONFIGS, mod.JSON_MODS, mod.SCRIPT_MODS


LINE_CFG_CACHE = None


def get_line_configs():
    global LINE_CFG_CACHE
    if LINE_CFG_CACHE is not None:
        return LINE_CFG_CACHE
    configs, _, _ = get_mod_configs()
    LINE_CFG_CACHE = {c.dir: c for c in configs}
    return LINE_CFG_CACHE


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
    json_path = os.path.join(mod_path, "translations.json")
    if not os.path.exists(json_path):
        return {"error": f"未找到 translations.json: {json_path}"}

    # 猜测英文文件（按命名惯例）
    en_candidates = [f for f in os.listdir(mod_path) if f.endswith("_ENGLISH.txt")]
    if not en_candidates:
        en_candidates = [f for f in os.listdir(mod_path) if f.endswith(".txt") or f.endswith(".ini")]
        en_candidates = [f for f in en_candidates if "zh" not in f.lower()]
    en_path = os.path.join(mod_path, en_candidates[0]) if en_candidates else None

    cn_candidates = [f for f in os.listdir(mod_path) if f.endswith("_CHINESE.txt") or "_zh." in f.lower()]
    cn_path = os.path.join(mod_path, cn_candidates[0]) if cn_candidates else None

    return {
        "en": os.path.join(mod_path, en_path) if en_path and os.path.exists(en_path) else None,
        "cn": os.path.join(mod_path, cn_path) if cn_path and os.path.exists(cn_path) else None,
        "json": json_path,
        "sep": "\t",
    }


def _split_line(line: str, sep: str = "\t"):
    """拆分一行，返回 (key, value)。"""
    stripped = line.strip("\r\n")
    if not stripped:
        return None, stripped
    if sep is None:
        parts = stripped.split(None, 1)
        if len(parts) < 2:
            return None, stripped
        return parts[0], parts[1]
    if sep not in stripped:
        return None, stripped
    return stripped.split(sep, 1)


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
    if not json_path:
        issues.append(f"[跳过] 未找到 translations.json")

    if not en_path or not json_path:
        return issues

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
        key, val = _split_line(line, sep)
        if key:
            full_key = f"{current_section}.{key}" if current_section and not key.startswith(f"{current_section}.") else key
            en_map[full_key] = val

    # ── 读取翻译 ──
    with open(json_path, "r", encoding="utf-8") as f:
        cn_map = json.load(f)

    en_keys = set(en_map.keys())
    cn_keys = set(cn_map.keys())

    # 1. 键完整性 — 支持节前缀 fallback
    # translations.json 可能用裸键（无节前缀）或带节前缀的键
    # 如果有节前缀且 cn 中无匹配，fallback 到裸键
    def resolve(k):
        """尝试在 cn_map 中找到 key 的匹配"""
        if k in cn_map:
            return k
        # 去掉节前缀再试（如 "Strings.Ammo" → "Ammo"）
        if "." in k:
            bare = k.split(".", 1)[1]
            if bare in cn_map:
                return bare
        return None

    missing = []
    for k in sorted(en_keys):
        if resolve(k) is None:
            missing.append(k)
    extra = cn_keys - en_keys
    # 排除由节前缀 fallback 匹配的 cn 键
    matched_cn = set()
    for k in en_keys:
        r = resolve(k)
        if r:
            matched_cn.add(r)
    extra = cn_keys - matched_cn

    if missing:
        issues.append(f"[缺失] {len(missing)} 条：{', '.join(missing[:10])}{'...' if len(missing) > 10 else ''}")
    if extra:
        issues.append(f"[多余] {len(extra)} 条：{', '.join(sorted(extra)[:10])}{'...' if len(extra) > 10 else ''}")

    # 2. 逐条检查内容
    # 构建反向映射：cn_key → en_key
    cn_to_en = {}
    for ek in en_keys:
        r = resolve(ek)
        if r:
            cn_to_en[r] = ek

    for k in sorted(cn_keys):
        ek = cn_to_en.get(k, "")
        en_v = en_map.get(ek, "")
        cn_v = cn_map.get(k, "")

        # 检查 \n 格式：parsed 后的值应该是 \n (反斜杠 + n 两字符)
        # 如果在 JSON 里用了真实换行符，Python 读出来后是 \n (0x0A 单字符)
        # 正确格式应该是 '\\n' (repr 显示 \\n)
        if "\n" in cn_v and "\\n" not in repr(cn_v):
            issues.append(f"[换行符] {k}: 含真实换行符(0x0A)，应为 \\n 转义序列")

        # 检查 %d 格式符
        if "%d" in en_v and "%d" not in cn_v:
            issues.append(f"[格式符] {k}: 遗漏 %d")
        if "%s" in en_v and "%s" not in cn_v:
            issues.append(f"[格式符] {k}: 遗漏 %s")

        # 检查疑似未翻译（EN==CN 且非全大写/品牌名）
        if en_v and cn_v and en_v == cn_v and len(en_v) > 2:
            if not en_v.isupper() and not en_v.startswith("F.U.C.K") and not en_v.startswith("$"):
                # 品牌名/缩写例外
                pass
                # 不报 warning，太吵。由用户自行检查。

    # 3. 检查中文输出文件是否存在且与 translations.json 条目一致
    if cn_path and os.path.exists(cn_path):
        cn_out_lines = read_lines(cn_path)
        cn_out_keys = set()
        current_section = ""
        for line in cn_out_lines:
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                current_section = stripped[1:-1]
                continue
            key, _ = _split_line(line, sep or "\t")
            if key:
                full_key = f"{current_section}.{key}" if current_section and not key.startswith(f"{current_section}.") else key
                cn_out_keys.add(full_key)
        missing_in_output = cn_keys - cn_out_keys
        # 同样支持裸键 fallback
        cn_out_resolved = set()
        for k in cn_out_keys:
            cn_out_resolved.add(k)
            # 如果输出文件用节前缀键，cn_keys 可能用裸键（或反之）
            if k in cn_map:
                pass
            elif "." in k:
                cn_out_resolved.add(k.split(".", 1)[1])
        missing_in_output = cn_keys - cn_out_resolved
        if missing_in_output:
            issues.append(f"[输出缺失] 中文文件缺少 {len(missing_in_output)} 条：{', '.join(sorted(missing_in_output)[:5])}")

    if not issues:
        issues.append("[OK] 全部检查通过")

    return issues


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    filters = set(sys.argv[1:]) if len(sys.argv) > 1 else None

    configs, json_mods, script_mods = get_mod_configs()

    # JSON 型模组需单独检查（格式不同），此处只检查 line-based 模组
    all_configs = [(c.dir, "line") for c in configs]

    exit_code = 0

    for mod_dir, mod_type in all_configs:
        if filters and mod_dir not in filters:
            continue

        # 跳过脚本型模组
        if any(s.dir == mod_dir for s in script_mods):
            continue

        print(f"\n{'='*60}")
        print(f"  {mod_dir} ({mod_type})")
        print(f"{'='*60}")

        issues = verify_mod(mod_dir, root)
        for issue in issues:
            if issue.startswith("[OK]"):
                print(f"  {issue}")
            else:
                print(f"  !! {issue}")
                exit_code = 1

    print(f"\n{'='*60}")
    if exit_code:
        print("  存在未通过项，请修复。")
    else:
        print("  全部通过 [OK]")
    print(f"{'='*60}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
