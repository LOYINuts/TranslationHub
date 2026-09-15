# 对话模组翻译

每个模组一个子目录，丢入 xTranslator 导出的 XML：

```
dialogue_mod_translation/<mod>/Something_XXXXXXXX.xml
```

对 agent 说「翻译 smalltalk」或「翻译这个 XML」。流程见 `.agents/skills/dialogue-xml/SKILL.md`。

手工命令：

```
python dialogue_mod_translation/translate.py stats <xml>
python dialogue_mod_translation/translate.py pending <xml> --fill-bdd
python dialogue_mod_translation/translate.py apply <mod>/pending.json
```

默认只动 `BOOK` `INFO` `DIAL` `NPC_`。词典：仓库根目录 `bdd.tsv`。
