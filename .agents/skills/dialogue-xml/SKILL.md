---
name: dialogue-xml
description: Translate Skyrim xTranslator XML under dialogue_mod_translation/. Use when the user drops an XML, names a folder like smalltalk/Remiel/FDEJenassa, or asks to translate BOOK/INFO/DIAL/NPC_ dialogue records.
---

# 对话 XML 翻译

先读 `.pi/skills/game-translation/SKILL.md`（译法），再按本流程改文件。译文写入 XML / `pending.json`，不要只在聊天里倒译文。

## 输入

- 模组目录：`dialogue_mod_translation/<mod>/`
- XML：同目录下 `*.xml`（xTranslator `<ESP>` 记录）
- 词典：仓库根 `bdd.tsv`（`grup \t original \t traduit`）
- 可选：同目录 `*对照表.md`、`*档案.md`、`*角色*.md` — **对照表优先于 bdd**

默认 GRUP：`BOOK` `INFO` `DIAL` `NPC_`。不要译 `SCPT` `TES4`，除非用户点名。`MESG` `QUST` `FACT` 同样等用户说。

STATUS：`0` 待译；`80`/`98`/`99` 已有译文，勿覆盖；写回用 `90`。

## 步骤

1. `python dialogue_mod_translation/translate.py stats <xml-or-dir>`
   - 支持单个 XML 或目录。先看默认 GRUP 待译数。
   - 输出出现 `�` 时，先检查源文件编码，不要把乱码当正常文本翻译。
2. 读模组目录里的对照表 / 角色档案（有则读）。
3. `python dialogue_mod_translation/translate.py pending <xml> --fill-bdd`
   - `(GRUP, 原文)` 在 bdd 中**唯一**命中的，直接写入 XML。
   - 其余进入同目录 `pending.json`。
   - `pending.json` 同时包含：
     - `items`：全部待译记录，保留精确 XML 写回目标。不要删除、改动其 `id`、`champ`、`original`。
     - `groups`：按 `GRUP + CHAMP + ORIGINAL` 去重后的翻译单元。优先翻译这里。
   - 已有 `pending.json` 且部分 `traduit` 已填：脚本会合并，勿手删。
4. 翻译 `groups[].traduit`，按 `edids` 和 `emotion` 检查上下文：
   - 同组文本默认可复用；存在 `candidates` 或语境差异时，拆分判断，不盲目套用。
   - `DIAL`/`NPC_`/`BOOK` 的 `FULL`：短名，跟已有译名和 bdd。
   - `BOOK` `DESC`：可含 `<font>`、`[pagebreak]`、`<p>`。标签原样留，只译可见英文。
   - `INFO` `NAM1`：台词。按说话者和 `emotion` 调整口吻。同一 `edid` 是同一话题。
   - `bdd` 有多项：选对的，不要盲填。
   - 占位符不改：`<mag>` `%s` `{...}` `$Player` `$HandwrittenFont` 等。
5. 用高性能工具处理待译 JSON：
   - `jaq -r '.groups[] | [.grup, .champ, .count, .original] | @tsv' pending.json`：查看唯一文本。
   - 先用 `jaq` 无写入运行验证过滤器，再用 `jaq -i` 更新 JSON。结构化 JSON 优先用 `jaq`，不要用正则硬改。
   - `sd -p` 预览纯文本替换；确认后才用 `sd -F` 做固定字符串批量替换。不要用 `sd` 改 XML 标签、占位符或 ID。
6. 每完成一批唯一翻译组：
   `python dialogue_mod_translation/translate.py apply <mod>/pending.json`
   - `apply` 会按 `groups` 的精确目标展开译文，并校验标签 / 占位符。
   - 再继续下一批；批次按唯一翻译组数量计算，不按重复 XML 条目数量计算。
7. `python dialogue_mod_translation/translate.py stats <xml>`
   `python dialogue_mod_translation/translate.py --self-check`
   默认 GRUP 待译必须为 0；自检失败或出现格式警告时停止。
## 禁区

- 不改 `ORIGINAL`、`ID`、`EDID`、`CHAMP`、`GRUP`。
- 不跑 ElementTree 整文件重写（会毁掉空标签和缩进）。XML 写回只用 `translate.py`。
- 不把 SCPT 脚本字符串当对话译。
- 不用 `sd` 正则批量改 XML 结构、标签、占位符或记录标识。
- 词典多行 BOOK 正文经常不在 bdd 索引里（tsv 破行）— 当普通文本译，仍遵守名词表。
- 不忽略 `�`、占位符 / 标签校验错误；先修源文本或停下报告。
