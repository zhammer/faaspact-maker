from typing import Callable, Dict, Tuple
from typing_extensions import Protocol

import requests


RequestsCallback = Callable[[requests.models.PreparedRequest], Tuple[int, Dict, str]]


class RequestsMockProtocol(Protocol):

    def add_callback(method: str, path: str, callback: RequestsCallback) -> None:
        ...
