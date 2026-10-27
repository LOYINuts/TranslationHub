---
name: dialogue-xml
description: Translate Skyrim xTranslator XML under dialogue_mod_translation/. Use for BOOK, INFO, DIAL, and NPC_ records, with context and existing terminology.
---

# Dialogue XML Translation

Read `game-translation` first. Write translations to XML or `pending.json`,
not only in chat. Command order and `bdd.tsv` rules are in AGENTS.md.

## Scope

- Input: `dialogue_mod_translation/<mod>/*.xml`.
- Default GRUP types: `BOOK`, `INFO`, `DIAL`, `NPC_`. Process `SCPT`, `TES4`,
  `MESG`, `QUST`, `FACT` only when the user asks.
- STATUS `0` means pending. STATUS `80`, `98`, `99` hold existing translations
  for reference. Write translated records with STATUS `90`.

## Translating

Read context and existing translations before translating `groups[].traduit` in
`pending.json`. Keep translations consistent across `edids` in the same group,
and split a group when context changes. Preserve HTML, `[pagebreak]`, and
paragraph structure in `BOOK DESC`. Match the speaker's voice in `INFO NAM1`.

Use `jq` to inspect or update JSON when available, otherwise Python's
standard-library `json` module. Use `sd` only for confirmed literal
replacements; otherwise edit the JSON precisely. Never use regex to edit XML.

## Protection

Do not change `ORIGINAL`, `ID`, `EDID`, `CHAMP`, `GRUP`, tags, or placeholders
such as `<mag>`, `%s`, `{...}`, `$Player`. Do not rewrite the full XML with
ElementTree; write XML only through `translate.py`.

Stop and report decoding errors, tag or placeholder check failures, or pending
records that remain after the final stats check.

Appending records to `bdd.tsv` needs `translate.py bdd --normalize` afterwards.
It deletes only byte-identical duplicate records, so kept lines never change.
