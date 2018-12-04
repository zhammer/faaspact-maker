from typing import NamedTuple

from faaspact_maker.definitions import Interaction, Request


class Call(NamedTuple):
    """A call made within the mocked environment for a given interaction."""
    request: Request
    interaction: Interaction
