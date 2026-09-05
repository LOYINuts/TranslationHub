import json
en=json.load(open('D:/codes/Python/MyTranslation/Dodgeall/Language.json','r',encoding='utf-8'))
zh=json.load(open('D:/codes/Python/MyTranslation/Dodgeall/Language_zh.json','r',encoding='utf-8'))
def count_keys(d):
    n = 0
    for k,v in d.items():
        if isinstance(v, dict):
            n += count_keys(v)
        else:
            n += 1
    return n
def flat_keys(d, prefix=''):
    keys = []
    for k,v in d.items():
        key = f'{prefix}.{k}' if prefix else k
        if isinstance(v, dict):
            keys.extend(flat_keys(v, key))
        else:
            keys.append(key)
    return keys
en_keys = set(flat_keys(en))
zh_keys = set(flat_keys(zh))
missing = sorted(en_keys - zh_keys)
extra = sorted(zh_keys - en_keys)
print(f'EN keys: {len(en_keys)}')
print(f'ZH keys: {len(zh_keys)}')
if missing:
    print(f'Missing in ZH ({len(missing)}):')
    for m in missing:
        print(f'  {m}')
if extra:
    print(f'Extra in ZH ({len(extra)}):')
    for e in extra:
        print(f'  {e}')
if not missing and not extra:
    print('Perfect match!')
