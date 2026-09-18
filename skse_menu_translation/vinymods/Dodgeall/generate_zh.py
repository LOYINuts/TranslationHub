"""
Dodgeall 翻译脚本：Language.json → Language_zh.json（嵌套 JSON）
"""
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# 读取英文源文件
with open(os.path.join(script_dir, "Language.json"), "r", encoding="utf-8") as f:
    en = json.load(f)

# 加载已有的中文翻译
zh_path = os.path.join(script_dir, "Language_zh.json")
if os.path.exists(zh_path):
    with open(zh_path, "r", encoding="utf-8") as f:
        zh_existing = json.load(f)
else:
    zh_existing = {}

# 加载新翻译（点号键名）
with open(os.path.join(script_dir, "translations.json"), "r", encoding="utf-8") as f:
    new_trans = json.load(f)

# 构建完整翻译映射：已有中文 + 新翻译（新翻译优先级更高）
def walk(d, prefix=""):
    """将嵌套 JSON 展开为 flat key -> value"""
    result = {}
    for k, v in d.items():
        pk = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            result.update(walk(v, pk))
        else:
            result[pk] = v
    return result

existing_flat = walk(zh_existing)
# 合并，新翻译覆盖已有
all_trans = {**existing_flat, **new_trans}


def rebuild(d, prefix=""):
    """用翻译映射重建嵌套 JSON"""
    out = {}
    for k, v in d.items():
        pk = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out[k] = rebuild(v, pk)
        else:
            out[k] = all_trans.get(pk, v)
    return out


zh = rebuild(en)

with open(zh_path, "w", encoding="utf-8") as f:
    json.dump(zh, f, ensure_ascii=False, indent=2)
    f.write("\n")

total = len([k for k in all_trans if not any(c in k for c in ["{", "}"])])  # rough count
print(f"总计: {len(all_trans)}")
