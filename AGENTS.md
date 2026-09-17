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

All mod configs live in `mods.toml`. Core logic in `config.py` + `locale_utils.py`.

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

Dialogue XML: Follow dialogue-xml skill checks.
Dependencies: Use `locale_utils.py` and Python stdlib only.
