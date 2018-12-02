import json
from contextlib import contextmanager, nullcontext
from typing import Callable, Dict, Generator, List, NamedTuple, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests

import responses

from faaspact_maker.definitions import Interaction, Pact
from faaspact_maker.pact_file_gateway import PactFileGateway
from faaspact_maker.pact_maker.definitions import Call
from faaspact_maker.pact_maker.types import RequestsCallback, RequestsMockProtocol


class PactMaker:
    """Make a pact"""
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
    def start_mocking(self, *, outer: Optional[RequestsMockProtocol] = None) -> Generator:
        """Start mocking requests!"""
        context_manager = responses.RequestsMock() if not outer else contextlib.nullcontext(outer)

        with context_manager as responses_mock:
            _register_mock_interactions(self.pact.interactions, self.provider_url, self.add_call, responses_mock)

            yield

        for call in self.calls:
            _validate_call(call)

        PactFileGateway.write_pact_file(self.pact)


def _register_mock_interactions(
        interactions: List[Interaction],
        provider_url: str,
        register_call: Callable[[Call], None],
        responses_mock: responses.RequestsMock) -> None:
    """Messy!"""
    for interaction in interactions:
        callback: RequestsCallback = _make_callback(interaction, register_call)
        responses_mock.add_callback(
            interaction.request.method,
            f'{provider_url}{interaction.request.path}',
            callback=callback
        )


def _make_callback(interaction: Interaction,
                   register_call: Callable[[Call], None]) -> RequestsCallback:
    def callback(request: requests.models.PreparedRequest) -> Tuple[int, Dict, str]:
        register_call(Call(request, interaction))  # todo: pluck out an understood request
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
    return parse_qs(qs)
