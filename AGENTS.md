# Project Translation Rules


| File Type | Path Pattern | Skill |
|-----------|--------------|-------|
| xTranslator XML | `dialogue_mod_translation/` | dialogue-xml |
| TXT/INI translation | `*_translation/` directories | translation-io |
| Descriptionmods | `Descriptionmods/` | translation-io |
| Any game text | - | game-translation |


1. Inspect source encoding, target convention, and existing terminology
2. Translate in place or generate matching Chinese output
3. Preserve: keys, order, separators, tags, placeholders, escapes, line structure
4. Run smallest verification command before completion
5. Write files; never return translation-only dump in chat

| Type | Command |
|------|---------|
| JSON project | `python verify_translation.py <name>` |
| Dialogue XML | Follow dialogue-xml skill checks |

Dependencies: Use `locale_utils.py` and Python stdlib only.
