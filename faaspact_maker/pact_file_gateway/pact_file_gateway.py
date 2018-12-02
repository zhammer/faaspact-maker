import json
import os
from datetime import datetime
from typing import Dict, Optional

from faaspact_maker.definitions import Interaction, Pact, ProviderState, Request, Response
from faaspact_maker import matchers


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
        'body': request.json,
        'headers': request.headers,
        'matchingRules': _build_request_matching_rules(request)
    })


def _build_path(request: Request) -> str:
    return request.path if isinstance(request.path, str) else request.path.value


def _build_request_matching_rules(request: Request) -> Optional[Dict]:
    matching_rules: Dict = {}
    if isinstance(request.path, matchers.Regex):
        matching_rules['path'] = {
            'matchers': [_build_regex_matcher(request.path)]
        }

    return matching_rules or None


def _build_regex_matcher(regex_matcher: matchers.Regex) -> Dict:
    return {
        'match': 'regex',
        'regex': regex_matcher.pattern
    }


def _build_response(response: Response) -> Dict:
    return _drop_none_values({
        'status': response.status_code,
        'headers': response.headers,
        'body': response.json
    })


def _drop_none_values(dictionary: Dict) -> Dict:
    """Drops fields from a dictionary where value is None.

    >>> _drop_none_values({'greeting': 'hello', 'name': None})
    {'greeting': 'hello'}
    """
    return {key: value for key, value in dictionary.items() if value is not None}
