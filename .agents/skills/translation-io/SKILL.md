---
name: translation-io
description: Read and write Skyrim translation TXT/INI files safely, including UTF-16 BOM and UTF-8. Use for *_translation directories and Descriptionmods.
---

# 翻译文件读写

## First Decision

1. For configured mods, edit only `translations.json`. Build the output files.
2. For `Descriptionmods`, edit `Descriptionmods/translations.json`, then run
   `python build_all.py Descriptionmods`.

## Encoding

Read source encoding before you inspect TXT/INI files:

```bash
python locale_utils.py detect PATH
python locale_utils.py dump PATH
```

Do not use Pi `read` for UTF-16 files. Generated output keeps the source
encoding and newline convention. Use `build_all.py` to make output files.

## Configured Mods

```bash
python sync_translation.py <name> --check
python sync_translation.py <name> --sync
python build_all.py --dry-run <name>
python build_all.py <name>
python verify_translation.py <name>
```

Separator and encoding come from `mods.toml`. Do not infer a global `=` rule.
Preserve keys, sections, order, comments, placeholders, tags, escaped `\\n`,
and other nontranslated fields.

For `Descriptionmods`, preserve every `key|description|metadata...` record.
Build and verify it with:

```bash
python build_all.py Descriptionmods
python verify_translation.py Descriptionmods
```

Any nonzero exit means incomplete work.
