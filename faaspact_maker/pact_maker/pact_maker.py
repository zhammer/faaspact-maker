"""
This whole module is incredibly messy right now.
"""


import json
from contextlib import contextmanager, nullcontext  # type: ignore
from typing import Callable, Dict, Generator, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests

import responses

from faaspact_maker.definitions import Interaction, Pact
from faaspact_maker.pact_file_gateway import PactFileGateway
from faaspact_maker.pact_maker.definitions import Call, Request
from faaspact_maker.pact_maker.types import RequestsCallback, RequestsMockProtocol


class PactMaker:
    """Make a pact"""
    def __init__(self,
                 consumer_name: str,
                 provider_name: str,
                 provider_url: str,
                 *,
                 pact_directory: str = '') -> None:
        self.pact = Pact(
            consumer_name=consumer_name,
            provider_name=provider_name,
            interactions=[]
        )
        self.pact_directory = pact_directory
        self.provider_url = provider_url
        self.calls: List[Call] = []

    def add_interaction(self, interaction: Interaction) -> None:
        self.pact.interactions.append(interaction)

    def add_call(self, call: Call) -> None:
        self.calls.append(call)

    @contextmanager
    def start_mocking(self, *, outer: Optional[RequestsMockProtocol] = None) -> Generator:
        """Start mocking requests!"""
        context_manager = responses.RequestsMock() if not outer else nullcontext(outer)

        with context_manager as responses_mock:
            _register_mock_interactions(
                self.pact.interactions, self.provider_url, self.add_call, responses_mock
            )

            yield responses_mock

        for call in self.calls:
            _validate_call(call)

        PactFileGateway.write_pact_file(self.pact, pact_directory=self.pact_directory)


def _register_mock_interactions(
        interactions: List[Interaction],
        provider_url: str,
        register_call: Callable[[Call], None],
        responses_mock: responses.RequestsMock) -> None:
    for interaction in interactions:
        callback: RequestsCallback = _make_callback(interaction, register_call)
        path = (interaction.request.path if isinstance(interaction.request.path, str)
                else interaction.request.path.value)
        responses_mock.add_callback(
            interaction.request.method,
            f'{provider_url}{path}',
            callback=callback
        )


def _make_callback(interaction: Interaction,
                   register_call: Callable[[Call], None]) -> RequestsCallback:
    def callback(request: requests.models.PreparedRequest) -> Tuple[int, Dict, str]:
        register_call(Call(_pluck_request_from_requests(request), interaction))
        response_without_matchers = interaction.response.without_matchers()
        return (
            response_without_matchers.status,
            response_without_matchers.headers or {},
            json.dumps(response_without_matchers.body)
        )

    return callback


def _pluck_request_from_requests(request: requests.models.PreparedRequest) -> Request:
    return Request(  # type: ignore
        method=request.method,
        path=urlparse(request.url).path if request.url else '',
        query=_pluck_query_params(request.url) if request.url else {},
        headers=request.headers or {},
        body=json.loads(request.body) if request.body else None
    )


def _validate_call(call: Call) -> None:
    expected_request = call.interaction.request.without_matchers()
    actual_request = call.request

    if expected_request.headers is not None:
        assert actual_request.headers
        assert set(expected_request.headers.items()).issubset(set(actual_request.headers.items()))

    if expected_request.query is not None:
        assert expected_request.query == actual_request.query

    if expected_request.body is not None:
        assert actual_request.body
        assert expected_request.body == actual_request.body


def _pluck_query_params(url: str) -> Dict:
    qs = urlparse(url).query
    return parse_qs(qs)
