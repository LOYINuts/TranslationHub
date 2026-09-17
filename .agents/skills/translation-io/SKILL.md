---
name: translation-io
description: Read and write Skyrim translation TXT/INI files safely, including UTF-16 BOM and UTF-8. Use for *_translation directories and Descriptionmods.
---

# 翻译文件读写

## 编码检测（必须先做）

```bash
python locale_utils.py detect PATH  # 检测编码
python locale_utils.py dump PATH    # 读取内容
```

❌ 禁止：直接用 Pi `read` 读 TXT/INI（会误判 UTF-16）

`locale_utils.py` 自动处理 UTF-16 LE/BE、UTF-8 BOM、UTF-8。
## 决策流程

```
有 translations.json?
├─ 是 → python build_all.py <mod_name>
│       → python verify_translation.py <mod_name>
└─ 否 → Descriptionmods/?
        ├─ 是 → 直接编辑 Descriptionmods/zh/ 对应文件
        └─ 否 → 成对 TXT/INI
                → 读英文，写中文，保持格式
```

分隔符默认 `\t`，等号分隔用 `" = "`。
## 写入

优先 `python build_all.py <name>`。手写时用 `locale_utils.write_utf16le_bom` / `write_utf8_bom` / `write_utf8`。

❌ 禁止：`Path.write_text(..., encoding="utf-16")`（换行会损坏）
## 必须保留

- ✅ 键、顺序、分隔符
- ✅ `%s` `%d` `{0}` `$VAR$` 占位符
- ✅ `\n` 转义（不是真实换行 0x0A）
- ✅ `<font>` `[br]` `<color>` 标签
## 禁止

- ❌ 直接改 UTF-16 原文
- ❌ 改键名或占位符
- ❌ 未验证就报告完成
