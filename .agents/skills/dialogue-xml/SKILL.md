---
name: dialogue-xml
description: Translate Skyrim xTranslator XML under dialogue_mod_translation/. Use for BOOK, INFO, DIAL, and NPC_ records, with context and existing terminology.
---

# Dialogue XML Translation

Read `game-translation` first. Write translations to XML or `pending.json`,
not only in chat.

## Scope

- Input: `dialogue_mod_translation/<mod>/*.xml`.
- Glossary: repository-root `bdd.tsv`. Prefer mod-local references and
  character profiles when they exist.
- Default GRUP types: `BOOK`, `INFO`, `DIAL`, and `NPC_`. Process `SCPT`,
  `TES4`, `MESG`, `QUST`, and `FACT` only when the user asks.
- STATUS `0` means pending. STATUS `80`, `98`, and `99` contain existing
  translations for reference. Write translated records with STATUS `90`.

## Workflow (same gate shape: stats → pending → apply → stats)

```bash
python dialogue_mod_translation/translate.py stats XML_OR_DIR
python dialogue_mod_translation/translate.py pending XML --fill-bdd
python dialogue_mod_translation/translate.py apply MOD/pending.json
python dialogue_mod_translation/translate.py stats XML_OR_DIR
```

Read context and existing translations before translating `groups[].traduit` in
`pending.json`. Keep translations consistent across `edids` in the same group.
Split a group when context changes. Preserve HTML, `[pagebreak]`, and paragraph
structure in `BOOK DESC`. Match the speaker's voice in `INFO NAM1`.

Use `jq` to inspect or update JSON when available. Otherwise, use Python's
standard-library `json` module. Use `sd` only for confirmed literal replacements.
Otherwise, edit the JSON precisely. Never use regex to edit XML.

## Protection and Checks

Do not change `ORIGINAL`, `ID`, `EDID`, `CHAMP`, `GRUP`, tags, or placeholders
such as `<mag>`, `%s`, `{...}`, and `$Player`. Do not rewrite the full XML with
ElementTree. Use only `translate.py` to write XML. Stop and report decoding
errors, tag or placeholder check failures, or pending records that remain after
the final stats check.
