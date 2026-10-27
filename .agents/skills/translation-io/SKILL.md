---
name: translation-io
description: Inspect and process translation text files safely, including UTF-16 BOM and UTF-8, in configured or new mod folders.
---

# Translation File I/O

## First Decision

1. For configured mods, edit only `translations.json`, then build the output
   files.
2. For `descriptionmods`, edit `descriptionmods/translations.json`, then run
   `uv run build_all.py descriptionmods`.

## New or Unconfigured Folders

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
   encoding is unclear.
   Do not try random encodings or edit the source to make parsing succeed.
6. Register the mod in `mods.toml` as `line`, `json`, or `qt`. Keep dialogue
   XML separate.
7. Create and translate `translations.json` from confirmed source keys.
   Run `uv run build_all.py --dry-run <mod>`, then build and verify.

## Encoding

Check source encoding before inspecting TXT or INI files:

```bash
uv run locale_utils.py detect PATH
uv run locale_utils.py dump PATH
```

Do not use Pi `read` for UTF-16 files. The generated output keeps the configured
encoding and newline convention. Use `build_all.py` to generate output files.

## Commands (see AGENTS.md for the full gate)

```bash
uv run sync_translation.py <name> --check
uv run build_all.py --dry-run <name>
uv run build_all.py <name>
uv run verify_translation.py <name>
```

Use the separator and encoding in `mods.toml`. Do not assume that all files use
`=`.
Preserve keys, sections, order, comments, placeholders, tags, escaped `\\n`,
and other non-translated fields.

For `descriptionmods`, preserve every `key|description|metadata...` record.
Run the same gate with `<name>` = `descriptionmods`.

Any nonzero exit code means the work is incomplete.
