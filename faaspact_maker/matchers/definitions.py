import re
from dataclasses import dataclass
from typing import Union

from typing_extensions import Protocol, runtime

from faaspact_maker.types import Primitive


@runtime
class Matcher(Protocol):
    """Matcher base class"""
    # Note: ideally here I'd want an ABC with an abstract property
    # for getting a matcher's value, but that is throwing some runtime
    # errors that i don't know how to debug.
    def value(self) -> Union[Primitive, 'Matcher']:
        ...


@dataclass
class Regex:
    value: str
    pattern: str

    def __post_init__(self) -> None:
        assert re.match(self.pattern, self.value)


@dataclass
class Like:
    value: Union[Primitive, Matcher]


@dataclass
class EachLike:
    value: Union[Primitive, Matcher]
    min: int = 1
