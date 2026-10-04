"""模组配置加载和数据类定义。"""

import os
import tomllib
from dataclasses import dataclass
from typing import Optional



def setup_cli_logging(verbose: bool = False) -> None:
    """Logging spec: one UTF-8 stdout handler, INFO default, DEBUG on --verbose.

    Use `log = logging.getLogger(__name__)` in each CLI.
    `print` is for tables, summaries, and prompts only.
    Never log translation values. Exit code is the gate signal."""
    import logging
    import sys

    from locale_utils import force_utf8_stdout

    force_utf8_stdout()
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
@dataclass
class ModConfig:
    """行分隔文件模组配置（TXT/INI）。"""
    dir: str
    source: str
    output: str
    sep: Optional[str] = "\t"
    encoding: str = "utf16-le-bom"
    output_sep: Optional[str] = None
    value_field: int = 1
    trim_trailing_fields: bool = False

    def __post_init__(self):
        if self.output_sep is None:
            self.output_sep = self.sep if self.sep is not None else "\t"


@dataclass
class ModJson:
    """JSON 文件模组配置。"""
    dir: str
    source: str
    output: str = ""
    translation_section: Optional[str] = None

    def __post_init__(self):
        if not self.output:
            base, ext = os.path.splitext(self.source)
            self.output = f"{base}_zh{ext}"


@dataclass
class ModQt:
    """Qt Linguist TS translation configuration."""
    dir: str
    source: str
    output: str

def matches_filter(mod_dir: str, filters) -> bool:
    """No filter = all. Accept full path or basename."""
    if not filters:
        return True
    norm = mod_dir.replace("\\", "/").lower()
    base = os.path.basename(norm)
    for value in filters:
        want = value.replace("\\", "/").rstrip("/").lower()
        if norm == want or base == want:
            return True
    return False


def repo_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def load_repo_configs(root: str | None = None):
    root = root or repo_root()
    return load_configs_from_toml(os.path.join(root, "mods.toml"))
def load_configs_from_toml(toml_path: str) -> tuple[list[ModConfig], list[ModJson], list[ModQt]]:
    """从 TOML 文件加载模组配置。"""
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)

    line_configs = []
    for idx, item in enumerate(data.get("line", [])):
        # Validate required fields
        if "dir" not in item:
            raise ValueError(f"line[{idx}]: missing required field 'dir'")
        if "source" not in item:
            raise ValueError(f"line[{idx}]: missing required field 'source'")
        if "output" not in item:
            raise ValueError(f"line[{idx}]: missing required field 'output'")
        
        sep = item.get("sep", "\t")
        if sep == "":  # 空字符串表示 None（任意空白）
            sep = None
        cfg = ModConfig(
            dir=item["dir"],
            source=item["source"],
            output=item["output"],
            sep=sep,
            encoding=item.get("encoding", "utf16-le-bom"),
            output_sep=item.get("output_sep"),
            value_field=item.get("value_field", 1),
            trim_trailing_fields=item.get("trim_trailing_fields", False),
        )
        line_configs.append(cfg)
    json_configs = []
    for idx, item in enumerate(data.get("json", [])):
        # Validate required fields
        if "dir" not in item:
            raise ValueError(f"json[{idx}]: missing required field 'dir'")
        if "source" not in item:
            raise ValueError(f"json[{idx}]: missing required field 'source'")
        
        cfg = ModJson(
            dir=item["dir"],
            source=item["source"],
            output=item.get("output", ""),
            translation_section=item.get("translation_section"),
        )
        json_configs.append(cfg)
    qt_configs = []
    for idx, item in enumerate(data.get("qt", [])):
        for field in ("dir", "source", "output"):
            if field not in item:
                raise ValueError(f"qt[{idx}]: missing required field '{field}'")
        qt_configs.append(
            ModQt(dir=item["dir"], source=item["source"], output=item["output"])
        )
    return line_configs, json_configs, qt_configs
