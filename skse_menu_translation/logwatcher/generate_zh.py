import json
from pathlib import Path

ROOT = Path(__file__).parent


def load_jsonc(path):
    text = Path(path).read_text(encoding="utf-8")
    output = []
    index = 0
    in_string = False
    escaped = False
    while index < len(text):
        char = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
        elif char == '"':
            in_string = True
            output.append(char)
            index += 1
        elif char == "/" and following == "/":
            index += 2
            while index < len(text) and text[index] not in "\r\n":
                index += 1
        elif char == "/" and following == "*":
            end = text.find("*/", index + 2)
            if end < 0:
                raise ValueError("Unclosed JSON block comment")
            output.extend("\n" for value in text[index:end + 2] if value == "\n")
            index = end + 2
        else:
            output.append(char)
            index += 1
    if in_string:
        raise ValueError("Unclosed JSON string")
    return json.loads("".join(output))


def flatten(value, prefix=""):
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            result.update(flatten(child, f"{prefix}.{key}" if prefix else key))
        return result
    return {prefix: value}


def apply(source, translations, prefix=""):
    if isinstance(source, dict):
        return {
            key: apply(value, translations, f"{prefix}.{key}" if prefix else key)
            for key, value in source.items()
        }
    if prefix not in translations:
        raise ValueError(f"Missing translation: {prefix}")
    return translations[prefix]


def main():
    source = load_jsonc(ROOT / "LogWatcherTranslation.json")
    translations = json.loads((ROOT / "translations.json").read_text(encoding="utf-8"))
    source_keys = set(flatten(source))
    if source_keys != set(translations):
        raise ValueError("Translation keys do not match the source")
    translated = apply(source, translations)
    print(f"总计: {len(translations)}")
    (ROOT / "LogWatcherTranslation_zh.json").write_text(
        json.dumps(translated, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
