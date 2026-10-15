# Project Translation Rules

Run local gates in order. Any nonzero exit code means failure.

```bash
python sync_translation.py <mod> --check
python build_all.py --dry-run <mod> && python build_all.py <mod>
python verify_translation.py <mod>
```

For dialogue XML, use `translate.py` in this order: `stats → pending --fill-bdd → apply → stats`.

## Routing

| File type | Path | Required skill or process |
|---|---|---|
| xTranslator XML | `dialogue_mod_translation/` | `dialogue-xml` + `game-translation` |
| Qt Linguist TS | `Eslifer/*.ts` | `translations.json` → generated TS |
| TXT/INI | Any mod folder | `translation-io` + `game-translation` |
| Description files | `Descriptionmods/` | `translation-io` + `game-translation` |
| JSON localization | Any configured mod | Shared `json` builder + `game-translation` |
| New or unknown files | Any mod folder | `translation-io` intake, then type-specific process |
| Any game text | Any path | `game-translation` |

## Source Of Truth

- `translations.json` is the source for every configured non-dialogue mod. Edit it, then build output files.
- Register each new non-dialogue mod in `mods.toml`. Create its `translations.json` before translation. Use `line` or `json`. Qt TS uses the shared `qt` handler.
- `Descriptionmods/`: edit `Descriptionmods/translations.json`. Build files under `Descriptionmods/zh/`.
- `Eslifer/`: edit `Eslifer/translations.json`. Build the TS file from `origin/eslifier_translation.ts`.
- Dialogue XML stays outside `mods.toml`. Use `pending.json` and `dialogue_mod_translation/translate.py`.
- Do not edit generated TXT/INI/JSON/TS files. Preserve source format.

## New Mod Intake

Before translating a new mod, inspect its folder and classify every candidate source and target file. Do not infer file type or encoding from a filename alone.

1. List files with `rg --files <mod-dir>`. Exclude archives and binaries from text parsing.
2. Run these commands for each likely text file:
   `python locale_utils.py detect <file>`
   `python locale_utils.py dump <file>`
   `detect` checks BOMs only. `dump` strictly decodes BOM-less files as UTF-8. Successful decoding does not prove the source encoding.
3. Inspect a text dump and file structure. Use JSON/XML parsers for structured files. Compare source and target samples to identify keys, separators, comments, and line endings.
4. If decoding fails or file type, source, target, or output encoding is unclear, stop and ask. Do not guess another encoding. Do not edit or build an unclassified file.
5. Register the mod in `mods.toml` as `line`, `json`, or `qt`. Keep dialogue XML separate. Create and translate `translations.json` from confirmed source keys. Run `python build_all.py --dry-run <mod>`, then build and verify.

## Required Workflow

1. For a new mod, follow New Mod Intake. Never guess file type or encoding.
2. Use terminology in this order: mod glossary/profile > nearby translations > `bdd.tsv` (dialogue XML) > established game terms.
3. Preserve keys, order, format, tags, placeholders, escapes, and line structure.
4. Keep `perk` in English by default. Translate it only when game context requires a localized term.
5. Edit translation sources, not generated output.
6. Run the smallest relevant build and verification commands.
7. Treat any nonzero command exit as failure. Do not report completion.
8. Write changes to repository files; never return a translation-only dump in chat.
9. After completing a requested repository update and passing its checks, create a commit and push it to the current branch's tracked remote. Stage only files related to the requested work; preserve unrelated worktree changes. Never force-push. If the remote has diverged, inspect and integrate its changes without rewriting published history before pushing.

## Logging

All CLIs use `config.setup_cli_logging`:

- One UTF-8 stdout handler. INFO by default, DEBUG with `--verbose`.
- Use named loggers only: `log = logging.getLogger(__name__)`.
- Use `print` only for tables, summaries, and user prompts.
- Never log `translations.json` values. Gate reads should depend on exit codes, not output text.

## Gate

Run these commands in order. Any nonzero exit code means failure.

```bash
python sync_translation.py <name> --check
python build_all.py --dry-run <name>
python build_all.py <name1> <name2>
python verify_translation.py <name>
```

`verify_translation.py` covers configured mods, Eslifer, and Descriptionmods. Dialogue XML uses its own checks.

All build configuration lives in `mods.toml`. Never hard-code mod lists. Do not create the unused `config.toml`. Python 3.11+ and the standard library are the only requirements.
