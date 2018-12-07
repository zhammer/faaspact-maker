import json
import os
from datetime import datetime

from faaspact_maker.build_pact_json import build_pact_json
from faaspact_maker.definitions import Pact


class PactFileGateway:

    @staticmethod
    def write_pact_file(pact: Pact, *,
                        pact_directory: str = '',
                        overwrite_existing: bool = True) -> None:
        os.makedirs(pact_directory, exist_ok=True)

        pact_json = build_pact_json(pact)
        pact_file_path = _build_pact_file_path(pact_directory, pact)

        if os.path.isfile(pact_file_path) and not overwrite_existing:
            timestamp = datetime.now().isoformat(timespec='seconds')
            os.rename(pact_file_path, f'{pact_file_path}.{timestamp}')

        with open(pact_file_path, 'w') as pact_file:
            json.dump(pact_json, pact_file, indent=4)


def _build_pact_file_path(pact_directory: str, pact: Pact) -> str:
    return os.path.join(pact_directory, f'{pact.consumer_name}-{pact.provider_name}.pact.json')
