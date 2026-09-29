---
name: game-translation
description: Translate English game text into natural Simplified Chinese. Use for dialogue, UI, quests, descriptions, and proofreading.
---

# English-to-Chinese Game Translation

Follow the file workflow selected by `AGENTS.md`. Write changes to repository
files, not only to chat.

## Translation

- Identify the purpose, speaker or user, tone, and context before translating
  into natural Simplified Chinese.
- Preserve meaning, logic, scope, conditions, tense, modality, and attitude.
  Do not omit or invent content.
- Make dialogue sound spoken. Keep UI concise. Preserve imagery and voice in
  literary text.
- Use terminology in this order: mod-local glossary or profile, nearby
  translations, repository terminology, then established game translations.
- Use natural Chinese grammar. Avoid literal English syntax and redundant
  pronouns or articles.

## Immutable Content

Preserve keys, code, links, paths, numbers, units, placeholders, escapes, and
markup unless the source format explicitly translates them.

Examples: `{name}`, `{0}`, `%s`, `%llu`, Qt `%1`, `$PLAYER$`, `<color>`,
`</color>`, `[br]`, and literal `\\n`.

## Final Check

1. Confirm the Chinese is natural and accurate. Keep names, terms, and register
   consistent.
2. Preserve numbers, tags, placeholders, escapes, and structural fields.
3. Resolve ambiguity from context. Report only ambiguity that context cannot
   resolve.
4. Run the AGENTS.md gate for the file type and require exit code 0.
