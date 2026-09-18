# Project Translation Rules


| File Type | Path Pattern | Skill |
|-----------|--------------|-------|
| xTranslator XML | `dialogue_mod_translation/` | dialogue-xml |
| TXT/INI translation | `*_translation/` directories | translation-io |
| Descriptionmods | `Descriptionmods/` | translation-io |
| Any game text | - | game-translation |


1. Inspect source encoding, target convention, and existing terminology
2. Translate in place or generate matching Chinese output
3. Preserve: keys, order, separators, tags, placeholders, escapes, line structure
4. Run smallest verification command before completion
5. Write files; never return translation-only dump in chat

## Build & Verification

All mod configs live in `mods.toml`. `config.py` defines config data classes and TOML loading; `locale_utils.py` owns shared encoding, parsing, and JSON helpers.

`config.toml` is not used by project code and is not present in repository. `.gitignore` keeps its name ignored as a defensive rule for local/private configuration; do not create or use it for mod configuration.
### 文件角色：源 vs 产物

**有 translations.json**：
- `translations.json` = 翻译源（可编辑）
- `*_zh.txt` / `*.ini` = 构建产物（只读，自动生成）
- 更新翻译：编辑 JSON → build → verify
- **不要直接改生成的 TXT/INI**，下次 build 会覆盖

**无 translations.json**：
- Descriptionmods: 直接编辑 `Descriptionmods/zh/` 下文件
- 成对 TXT/INI: 直接编辑中文文件，无构建步骤

```bash
# 检查英文源文件新增的词条
python sync_translation.py <name> --check

# 自动添加缺失词条（英文占位）
python sync_translation.py <name> --sync

# 交互式添加翻译
python sync_translation.py <name> --interactive

# 检查所有模组
python sync_translation.py --all --check

# Preview build
python build_all.py --dry-run <name>

# Build specific mods (supports basename or full path)
python build_all.py <name1> <name2>

# Show stats
python build_all.py --stats

# Verify (supports basename)
python verify_translation.py <name>

# Verbose output
python build_all.py -v <name>
```

### 验证范围
`verify_translation.py` 同时检查 line-based TXT/INI 和 JSON 模组：
- 键缺失与多余键
- `%s`、`%d`、`%f` 占位符
- 中文输出文件是否存在
- JSON 源文件允许 `//` 与 `/* ... */` 注释
- XML 与特殊脚本使用各自流程，不由该命令验证

不要直接修改 `build_all.py` 中的模组列表；新增模组应编辑 `mods.toml`。


Dialogue XML: Follow dialogue-xml skill checks.
Dependencies: Use `locale_utils.py` and Python stdlib only.
