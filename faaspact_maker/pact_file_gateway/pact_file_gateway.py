import json
import os
from functools import reduce
from typing import Dict, List

from faaspact_maker.build_pact_json import build_pact_json
from faaspact_maker.definitions import Pact


class PactFileGateway:

    @staticmethod
    def write_pact_file(pact: Pact, *,
                        pact_directory: str = '') -> None:
        """Writes a pact to a file. If there is already a pact file, this will add the interactions
        of `pact` to that file.
        """
        os.makedirs(pact_directory, exist_ok=True)

        pact_json = build_pact_json(pact)
        pact_file_path = _build_pact_file_path(pact_directory, pact)

        if os.path.isfile(pact_file_path):
            with open(pact_file_path) as existing_pact_file:
                existing_pact_json = json.load(existing_pact_file)
                pact_json = _merge_pacts(existing_pact_json, pact_json)

        with open(pact_file_path, 'w') as pact_file:
            json.dump(pact_json, pact_file, indent=4)


def _merge_pacts(left: Dict, right: Dict) -> Dict:
    if not (left['provider'] == right['provider'] and
            left['consumer'] == right['consumer'] and
            left['metadata']['pactSpecification'] == right['metadata']['pactSpecification']):
        raise RuntimeError('Trying to merge to an existing pact file that doesnt match. left: '
                           f'({left}, right: {right})')

    return {
        'provider': left['provider'],
        'consumer': left['consumer'],
        'interactions': _unique_dicts(left['interactions'] + right['interactions']),
        'metadata': left['metadata']
    }


def _unique_dicts(dicts: List[Dict]) -> List[Dict]:
    """Get a unique list of dicts from a list of dicts.

    >>> _unique_dicts([{'a': 'b'}, {'a': 'c'}, {'a': 'b'}])
    [{'a': 'b'}, {'a': 'c'}]
    """
    return reduce(lambda unique, new: (unique + [new]) if new not in unique else unique, dicts, [])


def _build_pact_file_path(pact_directory: str, pact: Pact) -> str:
    return os.path.join(pact_directory, f'{pact.consumer_name}-{pact.provider_name}.pact.json')
