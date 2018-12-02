import json
import os
from datetime import datetime
from typing import Dict, Optional, Union

from faaspact_maker import matchers
from faaspact_maker.definitions import Interaction, Pact, ProviderState, Request, Response


class PactFileGateway:

    @staticmethod
    def write_pact_file(pact: Pact, *,
                        pact_directory: str = '',
                        overwrite_existing: bool = True) -> None:
        pact_json = build_pact_json(pact)
        pact_file_path = _build_pact_file_path(pact_directory, pact)

        if os.path.isfile(pact_file_path) and not overwrite_existing:
            timestamp = datetime.now().isoformat(timespec='seconds')
            os.rename(pact_file_path, f'{pact_file_path}.{timestamp}')

        with open(pact_file_path, 'w') as pact_file:
            json.dump(pact_json, pact_file, indent=4)


def _build_pact_file_path(pact_directory: str, pact: Pact) -> str:
    return os.path.join(pact_directory, f'{pact.consumer_name}-{pact.provider_name}.pact.json')


def build_pact_json(pact: Pact) -> Dict:
    return {
        'provider': {'name': pact.provider_name},
        'consumer': {'name': pact.consumer_name},
        'interactions': [_build_interaction(interaction) for interaction in pact.interactions],
        'metadata': {'pactSpecification': {'version': '3.0.0'}}
    }


def _build_interaction(interaction: Interaction) -> Dict:
    return _drop_none_values({
        'description': interaction.description,
        'request': _build_request(interaction.request),
        'response': _build_response(interaction.response),
        'providerStates': (interaction.provider_states and
                           [_build_provider_state(provider_state)
                            for provider_state in interaction.provider_states])
    })


def _build_provider_state(provider_state: ProviderState) -> Dict:
    return _drop_none_values({
        'name': provider_state.name,
        'params': provider_state.params
    })


def _build_request(request: Request) -> Dict:
    return _drop_none_values({
        'method': request.method,
        'path': _build_path(request),
        'query': request.query,
        'body': request.json and _build_body(request.json),
        'headers': request.headers and _build_headers(request.headers),
        'matchingRules': _build_request_matching_rules(request)
    })


def _build_response(response: Response) -> Dict:
    return _drop_none_values({
        'status': response.status_code,
        'headers': response.headers and _build_headers(response.headers),
        'body': response.json and _build_body(response.json),
        'matchingRules': _build_response_matching_rules(response)
    })


def _build_body(body: Dict) -> Dict:
    without_matchers = {field: value.value if isinstance(value, matchers.Matcher) else value
                        for field, value in body.items()}

    return without_matchers


def _build_request_matching_rules(request: Request) -> Optional[Dict]:
    matching_rules: Dict = {}

    if isinstance(request.path, matchers.Regex):
        matching_rules['path'] = {
            'matchers': [_build_regex_matcher(request.path)]
        }

    if request.headers:
        header_matching_rules = _build_headers_matching_rules(request.headers)
        if header_matching_rules:
            matching_rules['header'] = header_matching_rules

    if request.json:
        body_matching_rules = _build_body_matching_rules(request.json)
        if body_matching_rules:
            matching_rules['body'] = body_matching_rules

    return matching_rules or None


def _build_response_matching_rules(response: Response) -> Optional[Dict]:
    matching_rules: Dict = {}

    if response.headers:
        header_matching_rules = _build_headers_matching_rules(response.headers)
        if header_matching_rules:
            matching_rules['header'] = header_matching_rules

    if response.json:
        body_matching_rules = _build_body_matching_rules(response.json)
        if body_matching_rules:
            matching_rules['body'] = body_matching_rules

    return matching_rules or None


def _build_body_matching_rules(body: Dict) -> Optional[Dict]:
    parent = '$'

    body_matching_rules: Dict = {}

    for field, value in body.items():
        if isinstance(value, matchers.Regex):
            body_matching_rules[f'{parent}.{field}'] = {
                'matchers': [_build_regex_matcher(value)]
            }

    return body_matching_rules or None


def _build_headers_matching_rules(headers: Dict[str, Union[str, matchers.Regex]]) -> Optional[Dict]:
    headers_matching_rules: Dict = {}

    for field, value in headers.items():
        if isinstance(value, matchers.Regex):
            headers_matching_rules[field] = {
                'matchers': [_build_regex_matcher(value)]
            }

    return headers_matching_rules or None


def _build_headers(headers: Dict[str, Union[str, matchers.Regex]]) -> Dict:
    return {field: value.value if isinstance(value, matchers.Regex) else value
            for field, value in headers.items()}


def _build_path(request: Request) -> str:
    return request.path if isinstance(request.path, str) else request.path.value


def _build_regex_matcher(regex_matcher: matchers.Regex) -> Dict:
    return {
        'match': 'regex',
        'regex': regex_matcher.pattern
    }


def _drop_none_values(dictionary: Dict) -> Dict:
    """Drops fields from a dictionary where value is None.

    >>> _drop_none_values({'greeting': 'hello', 'name': None})
    {'greeting': 'hello'}
    """
    return {key: value for key, value in dictionary.items() if value is not None}
