import json
from tempfile import TemporaryDirectory

from faaspact_maker.definitions import (
    Interaction,
    Pact,
    ProviderState,
    RequestWithMatchers,
    ResponseWithMatchers
)
from faaspact_maker.pact_file_gateway import PactFileGateway


PACT_A = Pact(
    consumer_name='zach',
    provider_name='zachsfriend',
    interactions=[
        Interaction(
            description='a text to hang out',
            provider_states=(ProviderState('friends phone is dead'),),
            request=RequestWithMatchers(
                method='GET',
                path='/status'
            ),
            response=ResponseWithMatchers(
                status=503
            )
        )
    ]
)


PACT_B = Pact(
    consumer_name='zach',
    provider_name='zachsfriend',
    interactions=[
        Interaction(
            description='an offer to go to a free show',
            request=RequestWithMatchers(
                method='POST',
                path='/messages',
                body={'message': 'i have free tickets lets go to a show'}
            ),
            response=ResponseWithMatchers(
                status=200,
                body={'message': 'sweet yeah'}
            )
        )
    ]
)


class TestWritePactFile:

    def test_creates_and_writes_to_new_file(self) -> None:
        with TemporaryDirectory() as dirname:
            PactFileGateway.write_pact_file(PACT_A, pact_directory=dirname)

            with open(dirname + '/zach-zachsfriend.pact.json') as written_pact_file:
                written_pact_json = json.load(written_pact_file)

        expected_pact_json = {
            'consumer': {'name': 'zach'},
            'provider': {'name': 'zachsfriend'},
            'interactions': [{
                'description': 'a text to hang out',
                'providerStates': [{'name': 'friends phone is dead'}],
                'request': {
                    'method': 'GET',
                    'path': '/status'
                },
                'response': {
                    'status': 503
                }
            }],
            'metadata': {'pactSpecification': {'version': '3.0.0'}}
        }
        assert written_pact_json == expected_pact_json

    def test_adds_new_interations_to_existing_pact_file(self) -> None:
        with TemporaryDirectory() as dirname:
            PactFileGateway.write_pact_file(PACT_A, pact_directory=dirname)
            PactFileGateway.write_pact_file(PACT_B, pact_directory=dirname)

            with open(dirname + '/zach-zachsfriend.pact.json') as written_pact_file:
                written_pact_json = json.load(written_pact_file)

        expected_pact_json = {
            'consumer': {'name': 'zach'},
            'provider': {'name': 'zachsfriend'},
            'interactions': [
                {
                    'description': 'a text to hang out',
                    'providerStates': [{'name': 'friends phone is dead'}],
                    'request': {
                        'method': 'GET',
                        'path': '/status'
                    },
                    'response': {
                        'status': 503
                    }
                },
                {
                    'description': 'an offer to go to a free show',
                    'request': {
                        'method': 'POST',
                        'path': '/messages',
                        'body': {'message': 'i have free tickets lets go to a show'}
                    },
                    'response': {
                        'status': 200,
                        'body': {'message': 'sweet yeah'}
                    }
                }

            ],
            'metadata': {'pactSpecification': {'version': '3.0.0'}}
        }
        assert written_pact_json == expected_pact_json

    def test_doesnt_add_identical_interactions_to_existing_pact_file(self) -> None:
        # Given/When we write our pacts too many times
        with TemporaryDirectory() as dirname:
            PactFileGateway.write_pact_file(PACT_A, pact_directory=dirname)
            PactFileGateway.write_pact_file(PACT_B, pact_directory=dirname)
            PactFileGateway.write_pact_file(PACT_A, pact_directory=dirname)
            PactFileGateway.write_pact_file(PACT_B, pact_directory=dirname)
            PactFileGateway.write_pact_file(PACT_A, pact_directory=dirname)
            PactFileGateway.write_pact_file(PACT_B, pact_directory=dirname)

            with open(dirname + '/zach-zachsfriend.pact.json') as written_pact_file:
                written_pact_json = json.load(written_pact_file)

        # Then we still only expect our two interactions to be logged
        expected_pact_json = {
            'consumer': {'name': 'zach'},
            'provider': {'name': 'zachsfriend'},
            'interactions': [
                {
                    'description': 'a text to hang out',
                    'providerStates': [{'name': 'friends phone is dead'}],
                    'request': {
                        'method': 'GET',
                        'path': '/status'
                    },
                    'response': {
                        'status': 503
                    }
                },
                {
                    'description': 'an offer to go to a free show',
                    'request': {
                        'method': 'POST',
                        'path': '/messages',
                        'body': {'message': 'i have free tickets lets go to a show'}
                    },
                    'response': {
                        'status': 200,
                        'body': {'message': 'sweet yeah'}
                    }
                }

            ],
            'metadata': {'pactSpecification': {'version': '3.0.0'}}
        }
        assert written_pact_json == expected_pact_json
