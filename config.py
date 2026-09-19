"""模组配置加载和数据类定义。"""

import os
import tomllib
from dataclasses import dataclass
from typing import Optional

@dataclass
class ModConfig:
    """行分隔文件模组配置（TXT/INI）。"""
    dir: str
    source: str
    output: str
    sep: Optional[str] = "\t"
    encoding: str = "utf16-le-bom"
    output_sep: Optional[str] = None

    def __post_init__(self):
        if self.output_sep is None:
            self.output_sep = self.sep if self.sep is not None else "\t"


@dataclass
class ModJson:
    """JSON 文件模组配置。"""
    dir: str
    source: str
    output: str = ""

    def __post_init__(self):
        if not self.output:
            base, ext = os.path.splitext(self.source)
            self.output = f"{base}_zh{ext}"


@dataclass
class ModScript:
    """脚本型模组配置。"""
    dir: str
    script: str = "generate_zh.py"
    verify: str = ""

def load_configs_from_toml(toml_path: str) -> tuple[list[ModConfig], list[ModJson], list[ModScript]]:
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
        )
        json_configs.append(cfg)
    script_configs = []
    for idx, item in enumerate(data.get("script", [])):
        # Validate required fields
        if "dir" not in item:
            raise ValueError(f"script[{idx}]: missing required field 'dir'")
        
        cfg = ModScript(
            dir=item["dir"],
            script=item.get("script", "generate_zh.py"),
            verify=item.get("verify", ""),
        )
        script_configs.append(cfg)
    return line_configs, json_configs, script_configs
