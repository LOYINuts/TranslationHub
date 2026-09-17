---
name: game-translation
description: Translate English game text into natural Simplified Chinese. Use for dialogue, UI, quests, descriptions, and proofreading.
---

# 英译中

先按项目路由加载对应文件流程，再翻译。改仓库文件时写回文件，不要只在聊天中输出全文。

## 原则

- 先判断用途、对象、语气和上下文，再重组为自然中文；不逐词替换
- 准确保留意思、逻辑、范围、条件、时态、情态、语气；不漏译、不误译、不补写
- 对话像人说话；UI 和说明简洁清楚；文学文本保留意象和文风
- 优先使用上下文、已有译文、词表和通行译法。术语、专名、称谓保持一致
- 中文可调整词性、语序、主被动、句型和标点，删除冗余冠词和英式虚词
## 格式（必须保留）

键、顺序、标签、代码、链接、路径、数字、单位、占位符、转义符、换行结构。

不改动：`{name}` `{0}` `%s` `$PLAYER$` `<color>` `</color>` `[br]` `\n`

## 示例

### ❌ 逐词翻译
> You have gained a new power.  
> 你已经获得了一个新的力量。

### ✅ 自然中文
> 你获得了新的能力。

---

### ❌ 漏占位符
> Equipped: %s (Damage: %d)  
> 已装备：（伤害：50）

### ✅ 保留占位符
> 已装备：%s（伤害：%d）

---

### ❌ 转义改真实换行
> Press\\nto continue  
> Press  
> to continue

### ✅ 保留转义
> 按下\\n继续
## 交付检查

1. 译文自然、准确、无翻译腔
2. 术语、数字、格式、标签、占位符完整一致
3. 无法判断的歧义才报告；能判断时直接用最稳妥译法
