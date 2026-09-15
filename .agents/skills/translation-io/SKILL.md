---
name: translation-io
description: Read/write Skyrim translation .txt/.ini of any encoding (UTF-16 LE/BE BOM or UTF-8). Always locale_utils dump; never Read txt/ini; never guess encoding; never write a decoder. Use for interface_translation/, skse_menu_translation/, *_ENGLISH.txt, *_CHINESE.txt, translations.json, or Descriptionmods.
---

# 翻译文件读写

**通用读法：任意 `.txt` / `.ini` 一律 `dump`，不要猜是不是 UTF-16，不要 `Read`。**

`locale_utils.py` 按 BOM 自动选 UTF-16 LE / UTF-16 BE / UTF-8。Pi `Read` 会把 UTF-16 当二进制拒读；UTF-8 文件 `dump` 也同样能看，所以不要分支。

禁止新写解码器。编码失败就停，不要再开一轮 Python。遣词读 `.agents/skills/game-translation/SKILL.md`。

## 怎么读（唯一路径）

```bash
python locale_utils.py detect PATH            # 可选：看编码，不靠它决定读法
python locale_utils.py dump PATH              # stdout 已是 UTF-8 — 就用这个
python locale_utils.py dump PATH -o OUT.txt   # 太大再 Read 这个 UTF-8 文件
```

只有这些可以直接 `Read`：`.json`、`translations.json`。

`detect` 只认 BOM：`utf16-le-bom` / `utf16-be-bom` / `utf-8-bom` / 其余报 `utf-8`。

## 禁区

- 不 `Read` `.txt` / `.ini`（包括你觉得是 UTF-8 的）。
- 不新写解码器，不 `open(..., encoding="utf-16")`，不 `Path.write_text(..., encoding="utf-16")`（Windows 会 `\r\r\n`）。
- 不 dump 完改 txt 再写回。有 `translations.json` 的模组，json 才是译文源。
- 不默认当 UTF-16 写。写之前 `detect` 源文件，或看 `build_all.py` 的 `ModConfig.encoding`。

## 目录怎么走

**`interface_translation/`**

1. `Read` 同目录 `translations.json`（UTF-8，译文源）。
2. 对照英文：`python locale_utils.py dump <ENGLISH.txt>`。
3. 改 json 的中文值。键、占位符、`\n` 转义原样留。
4. `uv run python build_all.py <短名或路径>` 生成中文文件（脚本自己按配置选编码）。
5. `uv run python verify_translation.py <短名或路径>`。

**`skse_menu_translation/`**

无额外规矩。JSON 直接 `Read` / 改。`.txt` / `.ini` 仍走 `dump`。有 `translations.json` 的同样改 json 再 `build_all.py`。

**`Descriptionmods/`**

无 json 流水线。`dump` 看英文 ini，改 `zh/` 对应文件（UTF-8，`key|html`，保留 `<font>`）。不走 `build_all.py`。

## 必须手写 txt/ini 时

先 `detect` 要覆盖的那个文件（或英文源），按同一编码写：

```python
from locale_utils import detect_encoding, write_utf16le_bom, write_utf8_bom, write_utf8

enc = detect_encoding(src_path)
text = "\r\n".join(lines) + "\r\n"
if enc == "utf16-le-bom":
    write_utf16le_bom(path, text)
elif enc == "utf-8-bom":
    write_utf8_bom(path, text)
else:
    write_utf8(path, text)
```

有 `ModConfig` 的模组优先让 `build_all.py` 写，不要手写。
