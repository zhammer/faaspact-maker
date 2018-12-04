from typing import Dict, List, NamedTuple, Optional, Tuple, Union

from faaspact_maker import matchers


class ProviderState(NamedTuple):
    name: str
    params: Optional[Dict] = None


class Request(NamedTuple):
    method: str
    path: str
    query: Optional[Dict] = None
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict] = None


class Response(NamedTuple):
    status: int
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict] = None


class RequestWithMatchers(NamedTuple):
    method: str
    path: Union[str, matchers.Regex]
    query: Optional[Dict] = None
    headers: Optional[Dict[str, Union[str, matchers.Regex]]] = None
    body: Optional[Dict] = None

    def without_matchers(self) -> Request:
        return _pluck_request(self)


class ResponseWithMatchers(NamedTuple):
    status: int
    headers: Optional[Dict[str, Union[str, matchers.Regex]]] = None
    body: Optional[Dict] = None

    def without_matchers(self) -> Response:
        return _pluck_response(self)


class Interaction(NamedTuple):
    description: str
    request: RequestWithMatchers
    response: ResponseWithMatchers
    provider_states: Optional[Tuple[ProviderState]] = None


class Pact(NamedTuple):
    consumer_name: str
    provider_name: str
    interactions: List[Interaction]

    @property
    def pact_specification(self) -> str:
        return '3.0.0'


def _pluck_request(request_with_matchers: RequestWithMatchers) -> Request:
    return Request(
        method=request_with_matchers.method,
        path=_pluck_path(request_with_matchers.path),
        query=request_with_matchers.query and _pluck_dict(request_with_matchers.query),
        headers=(None if request_with_matchers.headers is None
                 else _pluck_headers(request_with_matchers.headers)),
        body=request_with_matchers.body and _pluck_dict(request_with_matchers.body)
    )


def _pluck_response(response_with_matchers: ResponseWithMatchers) -> Response:
    return Response(
        status=response_with_matchers.status,
        headers=(None if response_with_matchers.headers is None
                 else _pluck_headers(response_with_matchers.headers)),
        body=response_with_matchers.body and _pluck_dict(response_with_matchers.body)
    )


def _pluck_path(path: Union[str, matchers.Regex]) -> str:
    return path if isinstance(path, str) else path.value


def _pluck_headers(headers: Dict[str, Union[str, matchers.Regex]]) -> Dict[str, str]:
    return {field: value.value if isinstance(value, matchers.Regex) else value
            for field, value in headers.items()}


def _pluck_dict(dict_with_matchers: Dict) -> Dict:
    without_matchers = {field: value.value if isinstance(value, matchers.Matcher) else value
                        for field, value in dict_with_matchers.items()}
    without_dictionaries = {field: _pluck_dict(value) if isinstance(value, dict) else value
                            for field, value in without_matchers.items()}
    without_lists = {field: _pluck_list(value) if isinstance(value, list) else value
                     for field, value in without_dictionaries.items()}
    return without_lists


def _pluck_list(list_with_matchers: List) -> List:
    without_matchers = [value.value if isinstance(value, matchers.Matcher) else value
                        for value in list_with_matchers]
    without_dictionaries = [_pluck_dict(value) if isinstance(value, dict) else value
                            for value in without_matchers]
    without_lists = [_pluck_list(value) if isinstance(value, list) else value
                     for value in without_dictionaries]
    return without_lists
