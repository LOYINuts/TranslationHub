# 对话模组翻译

每个模组一个子目录，丢入 xTranslator 导出的 XML：

```text
dialogue_mod_translation/<mod>/Something_XXXXXXXX.xml
```

Tell the agent "Translate smalltalk" or "Translate this XML". Follow
`.agents/skills/dialogue-xml/SKILL.md` for the process and
`.agents/skills/game-translation/SKILL.md` for translation style.

手工命令：

```bash
uv run dialogue_mod_translation/translate.py stats <xml>
uv run dialogue_mod_translation/translate.py pending <xml> --fill-bdd
uv run dialogue_mod_translation/translate.py apply <mod>/pending.json
```

默认只动 `BOOK` `INFO` `DIAL` `NPC_`。词典：仓库根目录 `bdd.tsv`。
