"""Speakable identifiers and automatic names.

Object ids are m1, m2, ... and group ids are g1, g2, ... — short,
unambiguous, easy to say and to hear. Auto-names are "box 3",
"line 7": the kind plus a per-kind ordinal.
"""

from __future__ import annotations

ID_PREFIX = "m"
GROUP_PREFIX = "g"


def next_object_id(counters: dict) -> str:
    counters["object"] = counters.get("object", 0) + 1
    return ID_PREFIX + str(counters["object"])


def next_group_id(counters: dict) -> str:
    counters["group"] = counters.get("group", 0) + 1
    return GROUP_PREFIX + str(counters["group"])


def auto_name(counters: dict, kind: str) -> str:
    key = "kind:" + kind
    counters[key] = counters.get(key, 0) + 1
    return "{0} {1}".format(kind, counters[key])


def looks_like_id(token: str) -> bool:
    return (len(token) > 1 and token[0] in (ID_PREFIX, GROUP_PREFIX)
            and token[1:].isdigit())
