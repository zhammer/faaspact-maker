import re
from dataclasses import dataclass
from typing import Dict, List, Union


Primitive = Union[str, int, float, bool, Dict, List]


class Matcher:
    """Matcher base class"""


@dataclass
class Regex(Matcher):
    value: str
    pattern: str

    def __post__init__(self) -> None:
        re.compile(self.pattern)


@dataclass
class Like(Matcher):
    value: Union[Primitive, Matcher]


@dataclass
class EachLike(Matcher):
    value: Union[Primitive, Matcher]
    min: int = 1
