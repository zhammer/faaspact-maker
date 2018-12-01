from typing import Dict, List, NamedTuple, Optional, Tuple


class ProviderState(NamedTuple):
    name: str
    params: Optional[Dict] = None


class Request(NamedTuple):
    method: str
    path: str
    query: Optional[Dict] = None
    headers: Optional[Dict] = None
    json: Optional[Dict] = None


class Response(NamedTuple):
    status_code: int
    headers: Optional[Dict] = None
    json: Optional[Dict] = None


class Interaction(NamedTuple):
    description: str
    request: Request
    response: Response
    provider_states: Optional[Tuple[ProviderState]] = None


class Pact(NamedTuple):
    consumer_name: str
    provider_name: str
    interactions: List[Interaction]

    @property
    def pact_specification(self) -> str:
        return '3.0.0'
