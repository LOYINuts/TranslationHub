---
name: game-translation
description: Translate English game text into natural Simplified Chinese. Use for dialogue, UI, quests, descriptions, and proofreading.
---

# 英译中

先按 `AGENTS.md` 路由加载文件流程。改仓库文件时写回文件，不只在聊天中输出。

## Translation

- First infer purpose, speaker/user, tone, and context; then write natural Simplified Chinese.
- Preserve meaning, logic, scope, conditions, tense, modality, and attitude. Do not omit or invent content.
- Dialogue should sound spoken; UI should be concise; literary text should preserve imagery and voice.
- Terminology priority: mod-local glossary/profile, nearby existing translation, repository terminology, established game translation.
- Reorder grammar freely for Chinese. Avoid literal English syntax and redundant pronouns/articles.

## Immutable Content

Preserve keys, code, links, paths, numbers, units, placeholders, escapes, and markup unless source format explicitly localizes them.

Examples: `{name}`, `{0}`, `%s`, `%llu`, Qt `%1`, `$PLAYER$`, `<color>`, `</color>`, `[br]`, literal `\\n`.

## Final Check

1. Natural and accurate Chinese; consistent names, terminology, and register.
2. Numbers, tags, placeholders, escapes, and structural fields preserved.
3. Resolve context-supported ambiguity directly; report only ambiguity that cannot be resolved.
4. Run format-specific verification and require exit code 0.
