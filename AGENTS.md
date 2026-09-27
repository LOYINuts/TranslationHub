# Project Translation Rules

## Routing

| File type | Path | Required skill/process |
|---|---|---|
| xTranslator XML | `dialogue_mod_translation/` | `dialogue-xml` + `game-translation` |
| TXT/INI | `*_translation/` | `translation-io` + `game-translation` |
| Description files | `Descriptionmods/` | `translations.json` → `zh/` |
| Qt Linguist TS | `Eslifer/*.ts` | `translations.json` → generated TS |
| Any game text | any | `game-translation` |

## Source Of Truth

- `translations.json` is the source for every configured non-dialogue mod.
  Edit it, then build output.
- Register each new non-dialogue mod in `mods.toml`. Create its
  `translations.json` before translation. Use `line`, `json`, or `script`.
- `Descriptionmods/`: edit `Descriptionmods/translations.json`.
  Build files under `Descriptionmods/zh/`.
- `Eslifer/`: edit `Eslifer/translations.json`. Build the TS file from
  `origin/eslifier_translation.ts`.
- Dialogue XML stays outside `mods.toml`. Use `pending.json` and
  `dialogue_mod_translation/translate.py`.
- Do not edit generated TXT/INI/JSON/TS files. Preserve source format.

## Required Workflow

1. Inspect source encoding, target convention, context, and existing terminology.
2. Preserve keys, order, format, tags, placeholders, escapes, and line structure.
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

`verify_translation.py` covers configured mods, Eslifer, and Descriptionmods.
Dialogue XML uses its own checks.

All build configuration lives in `mods.toml`. Never hard-code mod lists.
Do not create the unused `config.toml`. Python 3.11+ and the standard library
are the only requirements.
