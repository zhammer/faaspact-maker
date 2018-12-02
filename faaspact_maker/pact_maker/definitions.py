from typing import NamedTuple

import requests

from faaspact_maker import Interaction


class Call(NamedTuple):
    """A call made within the mocked environment for a given interaction."""
    request: requests.models.PreparedRequest
    interaction: Interaction
