---
name: translation-io
description: Read/write Skyrim translation .txt/.ini. UTF-16 LE BOM vs UTF-8. Use locale_utils; never Read UTF-16 files; never write a decoder.
---

# 翻译文件读写

Pi `Read` 把 UTF-16 当二进制拒读。**禁止**为此写探测/解码脚本。已有 `locale_utils.py`。

## 怎么读

```bash
python locale_utils.py detect PATH
python locale_utils.py dump PATH -o /tmp/locale_dump.txt
```

然后 `Read` 那个 UTF-8 dump。JSON / 无 BOM 的 `.ini` / `translations.json` 可直接 `Read`。

## 编码约定

默认（`*_ENGLISH.txt` `*_CHINESE.txt`、多数界面 txt）：**UTF-16 LE BOM + CRLF + Tab**。

例外以 `build_all.py` 里 `ModConfig(..., encoding=...)` 为准，不要猜：

- `utf-8`：musicconductor、PartySheet、consolecommander、多数 `.ini`
- JSON：一律 UTF-8

`detect` 只认 BOM：`utf16-le-bom` / `utf16-be-bom` / `utf-8-bom` / 其余报 `utf-8`。

## 怎么写

```python
from locale_utils import read_text, read_lines, write_utf16le_bom, write_utf8

write_utf16le_bom(path, "\r\n".join(lines) + "\r\n")  # 走 bytes，不会加倍 CR
```

禁止 `Path.write_text(..., encoding="utf-16")`：Windows 会把已有 `\r\n` 再转成 `\r\r\n`。

译文源一般是同目录 `translations.json`（UTF-8）。改 txt 后用 `build_all.py <mod>` 生成中文文件，或手写时编码必须与英文源一致。
