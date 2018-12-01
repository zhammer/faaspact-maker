import json
from contextlib import contextmanager
from typing import Callable, Dict, Generator, List, NamedTuple, Tuple
from urllib.parse import parse_qsl, urlparse

import requests

import responses

from faaspact_maker.definitions import Interaction, Pact
from faaspact_maker.pact_file_gateway import PactFileGateway


class Call(NamedTuple):
    """A call made within the mocked environment for a given interaction."""
    request: requests.models.PreparedRequest
    interaction: Interaction


class PactMaker:

    def __init__(self, consumer_name: str, provider_name: str, provider_url: str) -> None:
        self.pact = Pact(
            consumer_name=consumer_name,
            provider_name=provider_name,
            interactions=[]
        )
        self.provider_url = provider_url
        self.calls: List[Call] = []

    def add_interaction(self, interaction: Interaction) -> None:
        self.pact.interactions.append(interaction)

    def add_call(self, call: Call) -> None:
        self.calls.append(call)

    @contextmanager
    def start_mocking(self) -> Generator:
        """Start mocking requests!"""
        with responses.RequestsMock() as responses_mock:
            _register_mock_interactions(
                self.pact.interactions,
                self.provider_url,
                self.add_call,
                responses_mock
            )

            yield

        for call in self.calls:
            _validate_call(call)

        pact_file_gateway = PactFileGateway()
        pact_file_gateway.write_pact_file(self.pact)


_RequestsCallback = Callable[[requests.models.PreparedRequest], Tuple[int, Dict, str]]


def _register_mock_interactions(
        interactions: List[Interaction],
        provider_url: str,
        register_call: Callable[[Call], None],
        responses_mock: responses.RequestsMock) -> None:
    """Messy!"""
    for interaction in interactions:
        callback: _RequestsCallback = _make_callback(interaction, register_call)
        responses_mock.add_callback(
            interaction.request.method,
            f'{provider_url}{interaction.request.path}',
            callback=callback
        )


def _make_callback(interaction: Interaction,
                   register_call: Callable[[Call], None]) -> _RequestsCallback:
    def callback(request: requests.models.PreparedRequest) -> Tuple[int, Dict, str]:
        register_call(Call(request, interaction))
        return (
            interaction.response.status_code,
            interaction.response.headers or {},
            json.dumps(interaction.response.json)
        )

    return callback


def _validate_call(call: Call) -> None:
    expected_request = call.interaction.request

    if expected_request.headers is not None:
        assert set(expected_request.headers.items()).issubset(set(call.request.headers.items()))

    if expected_request.query is not None:
        assert call.request.url
        assert expected_request.query == _pluck_query_params(call.request.url)

    if expected_request.json is not None:
        assert call.request.body
        assert call.interaction.request.json == json.loads(call.request.body)


def _pluck_query_params(url: str) -> Dict:
    qs = urlparse(url).query
    return dict(parse_qsl(qs))
