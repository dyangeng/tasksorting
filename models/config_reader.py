# models/config_reader.py
from pathlib import Path
from typing import Dict, List, Union
import ast   # safe literal_eval

# ------------------------------------------------------------------ #
# 1)  Locate project root and the config file correctly
# ------------------------------------------------------------------ #
BASE_DIR     = Path(__file__).resolve().parent.parent   # one level above /models
CONFIG_PATH  = BASE_DIR / "models\config.txt"                  # e.g. .../Tasksorting/config.txt

# ------------------------------------------------------------------ #
def _parse(val: str) -> Union[int, List[str], Dict[str, tuple]]:
    val = val.strip()
    if val.isdigit():
        return int(val)
    if val.startswith("{") and val.endswith("}"):
        out = ast.literal_eval(val)
        return {k: tuple(v) for k, v in out.items()}
    return [part.strip() for part in val.split(",") if part.strip()]

# ------------------------------------------------------------------ #
def load_config(path: Union[str, Path] = CONFIG_PATH):
    # ensure Path object
    path = Path(path) if isinstance(path, str) else path
    if not path.exists():
        raise FileNotFoundError(f"config.txt not found: {path}")

    cfg = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()   # remove comments
            if not line:
                continue
            key, val = map(str.strip, line.split("=", 1))
            cfg[key] = _parse(val)

    required = {"rows", "cols", "objects", "layout"}
    missing  = required - cfg.keys()
    if missing:
        raise ValueError(f"Missing keys in config.txt: {missing}")

    return cfg

# singleton for easy import
CONFIG = load_config()
