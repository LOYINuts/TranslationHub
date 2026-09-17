---
name: dialogue-xml
description: Translate Skyrim xTranslator XML under dialogue_mod_translation/. Use for BOOK, INFO, DIAL, and NPC_ records, with context and existing terminology.
---

# 对话 XML 翻译

先读 `game-translation`，再按本流程改文件。译文写入 XML 或 `pending.json`，不要只在聊天中输出。

## 范围

- 输入：`dialogue_mod_translation/<mod>/*.xml`
- 词典：仓库根 `bdd.tsv`；模组目录内对照表、角色档案优先
- 默认 GRUP：`BOOK`、`INFO`、`DIAL`、`NPC_`。`SCPT`、`TES4`、`MESG`、`QUST`、`FACT` 仅按用户要求处理
- STATUS `0` 待译；`80`、`98`、`99` 是已有译文，只作样本；写回使用 `90`

## 流程

```bash
python dialogue_mod_translation/translate.py stats XML_OR_DIR
python dialogue_mod_translation/translate.py pending XML --fill-bdd
python dialogue_mod_translation/translate.py apply MOD/pending.json
python dialogue_mod_translation/translate.py stats XML_OR_DIR
python dialogue_mod_translation/translate.py --self-check
```

先读上下文和已有译文，再翻译 `pending.json` 的 `groups[].traduit`。按 `edids` 连贯处理；同一组可复用，但有语境差异时拆开。`BOOK DESC` 保留 HTML、`[pagebreak]` 和段落结构；`INFO NAM1` 按说话者调整口吻。

可用 `jaq` 查看/更新 JSON；不可用时用 Python 标准库 `json`，不要因此停工。`sd` 只用于确认后的固定文本替换；不可用时手动精确修改 JSON。不要用正则改 XML。

## 保护与检查

不改 `ORIGINAL`、`ID`、`EDID`、`CHAMP`、`GRUP`、标签或占位符（如 `<mag>`、`%s`、`{...}`、`$Player`）。不使用 ElementTree 整文件重写；只用 `translate.py` 写回。解码失败、标签/占位符校验失败或默认待译数非零时停止并报告。
