---
name: game-translation
description: Translate English game text into natural Simplified Chinese. Use for dialogue, UI, quests, descriptions, and proofreading.
---

# English-to-Chinese Game Translation

Read the file workflow in `AGENTS.md`. Write changes to repository files, not
only to chat.

## Translate

- Read the speaker or user, purpose, tone, and context first. Preserve meaning,
  logic, scope, conditions, tense, modality, and attitude: omit and invent
  nothing.
- Make dialogue sound spoken, keep UI concise, preserve imagery and voice in
  literary text. Use natural Chinese grammar, not literal English syntax or
  redundant pronouns and articles.
- Terminology order: mod-local glossary or profile > nearby translations >
  `bdd.tsv` (dialogue XML) > established game translations.
- `perk` stays English unless the surrounding game context localizes the term.

## Do not translate

Keys, code, links, paths, numbers, units, comments, and structural fields.
Preserve placeholders and markup exactly, unless the source format translates
them: `{name}`, `{0}`, `%s`, `%llu`, Qt `%1`, `$PLAYER$`, `<color>`, `[br]`,
and literal `\n`.

## Before finishing

Re-read the Chinese for naturalness and register consistency, confirm every
placeholder and tag survived, resolve ambiguity from context, then run the
AGENTS.md gate and require exit code 0. Report only ambiguity that context
cannot resolve.
