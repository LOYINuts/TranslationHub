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
uv run dialogue_mod_translation/translate.py bdd --check
```

默认只动 `BOOK` `INFO` `DIAL` `NPC_`。词典：仓库根目录 `bdd.tsv`。

`bdd.tsv` 是带引号的 TSV，字段可跨行。`bdd` 子命令维护它：

```bash
uv run dialogue_mod_translation/translate.py bdd              # 统计
uv run dialogue_mod_translation/translate.py bdd --check      # 有重复即非零
uv run dialogue_mod_translation/translate.py bdd --normalize  # 删除重复记录
```

追加新记录后跑 `--normalize`，保留记录逐字节不变。`check_all.py` 会跑 `--check`。
