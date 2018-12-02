from typing import Callable, Dict, Tuple

import requests

from typing_extensions import Protocol


RequestsCallback = Callable[[requests.models.PreparedRequest], Tuple[int, Dict, str]]


class RequestsMockProtocol(Protocol):

    def add_callback(self, method: str, path: str, callback: RequestsCallback) -> None:
        ...
