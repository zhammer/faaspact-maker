import json
import os
from datetime import datetime
from typing import Dict

from faaspact_maker.definitions import Interaction, Pact, ProviderState, Request, Response


class PactFileGateway:

    @staticmethod
    def write_pact_file(pact: Pact, *,
                        pact_directory: str = '',
                        overwrite_existing: bool = True) -> None:
        pact_json = _build_pact_json(pact)
        pact_file_path = _build_pact_file_path(pact_directory, pact)

        if os.path.isfile(pact_file_path) and not overwrite_existing:
            timestamp = datetime.now().isoformat(timespec='seconds')
            os.rename(pact_file_path, f'{pact_file_path}.{timestamp}')

        with open(pact_file_path, 'w') as pact_file:
            json.dump(pact_json, pact_file, indent=4)


def _build_pact_file_path(pact_directory: str, pact: Pact) -> str:
    return os.path.join(pact_directory, f'{pact.consumer_name}-{pact.provider_name}.pact.json')


def _build_pact_json(pact: Pact) -> Dict:
    return {
        'provider': {'name': pact.provider_name},
        'consumer': {'name': pact.consumer_name},
        'interactions': [_build_interaction(interaction) for interaction in pact.interactions],
        'metadata': {'pactSpecification': {'version': '3.0.0'}}
    }


def _build_interaction(interaction: Interaction) -> Dict:
    built = {
        'description': interaction.description,
        'request': _build_request(interaction.request),
        'response': _build_response(interaction.response)
    }
    if interaction.provider_states is not None:
        built['providerStates'] = [_build_provider_state(provider_state)
                                   for provider_state in interaction.provider_states]

    return built


def _build_provider_state(provider_state: ProviderState) -> Dict:
    return _drop_none_values({
        'name': provider_state.name,
        'params': provider_state.params
    })


def _build_request(request: Request) -> Dict:
    return _drop_none_values({
        'method': request.method,
        'path': request.path,
        'query': request.query,
        'body': request.json,
        'headers': request.headers
    })


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
