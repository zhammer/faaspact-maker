import json
from contextlib import contextmanager
from typing import Any, Callable, Dict, Generator, List, NamedTuple, Optional, Set, Tuple
from urllib.parse import urlparse, parse_qs

import requests
import responses


class ProviderState(NamedTuple):
    name: str
    params: Optional[Dict] = None


class Request(NamedTuple):
    method: str
    path: str
    json: Dict
    query: Dict
    headers: Dict


class Response(NamedTuple):
    status_code: int
    headers: Dict
    json: Dict


class Interaction(NamedTuple):
    description: str
    request: Request
    response: Response
    provider_states: Optional[Tuple[ProviderState]] = None


# class Pact(NamedTuple):
#     consumer_name: str
#     provider_name: str
#     interactions: List[Interaction]

#     @property
#     def pact_specification() -> str:
#         return '3.0.0'

#     def add_interaction(interaction: Interaction) -> None:
#         interactions.append(interaction)


class Pact:

    def __init__(self, consumer_name: str, provider_name: str, provider_url: str) -> None:
        self.consumer_name = consumer_name
        self.provider_name = provider_name
        self.provider_url = provider_url
        self.interactions: List[Interaction] = []
        self.calls: List[Tuple[Interaction, Any]] = []
        self.pact_specification = '3.0.0'

    def add_interaction(self, interaction: Interaction) -> None:
        self.interactions.append(interaction)

    @contextmanager
    def mocker(self, outer: Optional[responses.RequestsMock] = None) -> Generator:
        with responses.RequestsMock() as responses_mock:
            for interaction in self.interactions:
                responses_mock.add_callback(
                    interaction.request.method,
                    self.provider_url + interaction.request.path,
                    callback=self._make_callback(interaction, register_call=lambda call: self.calls.append(call))
                )

            yield

            for interaction, request in self.calls:
                assert set(interaction.request.headers.items()) <= set(request.headers.items())
                assert self._query_param_set(interaction.request.query) <= self._query_param_set(self._pluck_query_params(request.url))
                self._pluck_query_params(request.url)

                if interaction.request.json:
                    assert interaction.request.json == json.loads(request.body)

            built = self._build_pact()
            print(json.dumps(built, indent=4))

    @staticmethod
    def _make_callback(interaction: Interaction, register_call: Callable[[Tuple[Interaction, requests.models.PreparedRequest]], None]) -> Callable[[requests.models.PreparedRequest], None]:
        def callback(request: requests.models.PreparedRequest):
            register_call((interaction, request))
            return (
                interaction.response.status_code,
                interaction.response.headers,
                json.dumps(interaction.response.json)
            )

        return callback

    @staticmethod
    def _pluck_query_params(url: str) -> Dict:
        qs = urlparse(url).query
        return parse_qs(qs)

    @staticmethod
    def _query_param_set(params: Dict) -> Set:
        return {(k, tuple(v) if isinstance(v, list) else v) for k, v in params.items()}

    def _build_pact(self) -> Dict:
        return {
            'provider': {'name': self.provider_name},
            'consumer': {'name': self.provider_name},
            'interactions': [self._build_interaction(interaction) for interaction in self.interactions],
            'metadata': {'pactSpecification': {'version': '3.0.0'}}
        }

    @staticmethod
    def _build_interaction(interaction: Interaction) -> Dict:
        built = {
            'description': interaction.description,
            'request': Pact._build_request(interaction.request),
            'response': Pact._build_response(interaction.response)
        }
        if interaction.provider_states is not None:
            built['providerStates'] = [Pact._build_provider_state(provider_state) for provider_state in interaction.provider_states]

        return built

    @staticmethod
    def _build_provider_state(provider_state: ProviderState) -> Dict:
        built = {'name': provider_state.name}
        if provider_state.params is not None:
            built['params'] = provider_state.params

        return built

    @staticmethod
    def _build_request(request: Request) -> Dict:
        return {
            'method': request.method,
            'path': request.path,
            'query': request.query,
            'body': request.json,
            'headers': request.headers
        }

    @staticmethod
    def _build_response(response: Response) -> Dict:
        return {
            'status': response.status_code,
            'headers': response.headers,
            'body': response.json
        }


pact = Pact('Zach', 'Gabe', 'https://zachgabechat.com')

pact.add_interaction(Interaction(
    description='Zach messages gabe',
    provider_states=(ProviderState('Gabe is online'),),
    request=Request(
        method='POST',
        path='/gabe',
        json={'message': 'Hey gabe'},
        query={},
        headers={}
    ),
    response=Response(
        json={'message': 'Ayee whatsup'},
        headers={},
        status_code=200
    )
))

pact.add_interaction(Interaction(
    description='Zach checks friends online',
    provider_states=(ProviderState('I have one friend online'),),
    request=Request(
        method='GET',
        path='/friends',
        query={'status': ['online']},
        json={},
        headers={}
    ),
    response=Response(
        json={'number': 1},
        headers={},
        status_code=200
    )
))

with pact.mocker():
    requests.post('https://zachgabechat.com/gabe', json={'message': 'Hey gabe'})
    requests.get('https://zachgabechat.com/friends', params={'status': 'online'})
