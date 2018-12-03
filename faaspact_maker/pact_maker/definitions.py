from typing import Dict, NamedTuple, Optional

from faaspact_maker import Interaction


class Request(NamedTuple):
    method: str
    path: str
    headers: Dict[str, str]
    query: Optional[Dict] = None
    body: Optional[Dict] = None


class Call(NamedTuple):
    """A call made within the mocked environment for a given interaction."""
    request: Request
    interaction: Interaction
