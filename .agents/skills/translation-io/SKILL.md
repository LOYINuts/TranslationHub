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
## 决策流程与文件角色

```
有 translations.json?
├─ 是 → translations.json = 翻译源（可编辑）
│       TXT/INI = 构建产物（只读，会被覆盖）
│       
│       更新翻译：
│       1. 编辑 translations.json 添加/修改条目
│       2. python build_all.py <name>  # 生成 TXT/INI
│       3. python verify_translation.py <name>
│       
│       ❌ 禁止：直接编辑生成的 TXT/INI（下次构建会覆盖）
│
└─ 否 → Descriptionmods/?
        ├─ 是 → 直接编辑 Descriptionmods/zh/ 对应文件
        │       （无构建步骤，直接修改）
        │
        └─ 否 → 成对 TXT/INI
                → 读英文源，写中文文件，保持格式
                → 无 JSON，直接编辑 TXT/INI
```

### 同步新词条

```bash
# 检查英文源文件新增的词条
python sync_translation.py <name> --check

# 自动添加缺失词条（英文占位）
python sync_translation.py <name> --sync

# 交互式添加翻译
python sync_translation.py <name> --interactive

# 检查所有模组
python sync_translation.py --all --check
```

### 构建与验证

```bash
# 预览构建
python build_all.py --dry-run <name>

# 构建模组（basename 支持）
python build_all.py FUCK KillFeed

# 显示统计
python build_all.py --stats

# 验证翻译
python verify_translation.py <name>

# 详细输出
python build_all.py -v <name>
```

分隔符默认 `\t`，等号分隔用 `" = "`.

## 写入规则

**有 translations.json**：
- 只编辑 translations.json
- 运行 `python build_all.py <name>` 生成 TXT/INI
- TXT/INI 是自动生成的，不要手动改

**无 translations.json**：
- Descriptionmods：直接编辑 zh/ 下文件
- 成对 TXT/INI：手动写中文文件，用 `locale_utils.write_utf16le_bom` / `write_utf8_bom` / `write_utf8`

分隔符默认 `\t`，等号分隔用 `" = "`。
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
