"""The single markdown front-matter parser used for every content file."""

import re
from typing import Dict, List, Tuple

_FRONT_MATTER_RE = re.compile(r"\A\s*---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)(.*)\Z", re.DOTALL)
TRUE_VALUES = ("true", "yes", "1")


def parse(text: str) -> Tuple[Dict[str, str], str]:
    """
    Split markdown into (front-matter dict, body).

    The block must sit at the very top of the file. Keys are lowercased and
    surrounding quotes on values are stripped. A file with no front matter
    returns ({}, whole text). Horizontal rules (---) in the body are left alone.
    """
    text = text.replace("\r\n", "\n")
    match = _FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text.strip()

    meta: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        m = re.match(r"^\s*([A-Za-z_][\w-]*)\s*:\s*(.*?)\s*$", line)
        if not m:
            continue
        value = m.group(2)
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        meta[m.group(1).lower()] = value
    return meta, match.group(2).strip()


def as_bool(raw: str) -> bool:
    return (raw or "").strip().lower() in TRUE_VALUES


def as_list(raw: str) -> List[str]:
    raw = (raw or "").strip().strip("[]")
    return [k.strip().strip("\"'") for k in raw.split(",") if k.strip().strip("\"'")]
