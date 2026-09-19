# Project Translation Rules

## Routing

| File type | Path | Required skill/process |
|---|---|---|
| xTranslator XML | `dialogue_mod_translation/` | `dialogue-xml` + `game-translation` |
| TXT/INI | `*_translation/` | `translation-io` + `game-translation` |
| Description files | `Descriptionmods/` | `translation-io` + `game-translation` |
| Qt Linguist TS | `Eslifer/*.ts` | `game-translation`; preserve XML and Qt `%1` placeholders |
| Any game text | any | `game-translation` |

## Source Of Truth

- Directory contains `translations.json`: edit it, then build output. Generated TXT/INI/JSON is read-only.
- `Descriptionmods/`: edit matching file under `Descriptionmods/zh/` directly.
- `Eslifer/`: `origin/eslifier_translation.ts` is source; edit `eslifier_translation.ts`.
- Dialogue XML: use `pending.json` and `dialogue_mod_translation/translate.py`; never regex-edit XML.
- Unconfigured paired files: edit Chinese file directly and preserve source encoding/format.

## Required Workflow

1. Inspect source encoding, target convention, context, and existing terminology.
2. Preserve keys, order where required, separators, tags, placeholders, escapes, and line structure.
3. Edit translation source, not generated output.
4. Run smallest relevant build and verification command.
5. Treat any nonzero command exit as failure; do not report completion.
6. Write changes to repository files; never return a translation-only dump in chat.

## Commands

```bash
python sync_translation.py <name> --check
python sync_translation.py <name> --sync
python sync_translation.py --all --check
python build_all.py --dry-run <name>
python build_all.py <name1> <name2>
python build_all.py --stats
python verify_translation.py <name>
python verify_translation.py
```

`verify_translation.py` covers configured line/JSON/script mods, `Eslifer`, and `Descriptionmods`. Dialogue XML uses its skill-specific checks.

All build configuration lives in `mods.toml`. Add mods there; never hard-code lists in scripts. `config.toml` is unused and must not be created. Python requirement: 3.11+. Dependencies: Python standard library only.
