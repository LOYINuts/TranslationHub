---
name: translation-io
description: Inspect and process translation text files safely, including UTF-16 BOM and UTF-8, in configured or new mod folders.
---

# Translation File I/O

## Configured mods

Edit only `translations.json`, then build. `descriptionmods` uses
`descriptionmods/translations.json` with `uv run build_all.py descriptionmods`.

## New or unconfigured folders

1. List files with `rg --files <mod-dir>`. Do not use Pi `read` before you
   know the encoding.
2. For likely text files, run:
   `uv run locale_utils.py detect PATH`
   `uv run locale_utils.py dump PATH`
3. `detect` checks BOMs only. `dump` strictly decodes BOM-less files as UTF-8.
   A successful decode does not prove the original encoding.
4. Inspect the file structure and compare source and target files. Parse JSON
   and XML as structured data.
5. Stop and ask if the encoding, file type, source/target roles, or output
   encoding is unclear. Do not try random encodings, and do not edit the source
   to make parsing succeed.
6. Register the mod in `mods.toml` (see AGENTS.md), then create and translate
   `translations.json` from confirmed source keys. Run
   `uv run build_all.py --dry-run <mod>`, then build and verify.

## Format

Use the separator and encoding in `mods.toml`; do not assume all files use `=`.
The generated output keeps the configured encoding and newline convention.
For `descriptionmods`, preserve every `key|description|metadata...` record.
Preserve keys, sections, order, comments, placeholders, tags, and escaped `\n`.
