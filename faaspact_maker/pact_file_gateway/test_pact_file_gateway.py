from faaspact_maker.definitions import Interaction, Pact, ProviderState, Request, Response
from faaspact_maker.pact_file_gateway.pact_file_gateway import build_pact_json


class TestBuildPactJson():

    def test_builds_pact(self) -> None:
        # Given
        pact = Pact(
            consumer_name='Zach',
            provider_name='Gabe',
            interactions=[
                Interaction(
                    provider_states=(ProviderState('Gabe is online'),),
                    description='Zach messages gabe',
                    request=Request(
                        method='POST',
                        path='/gabe',
                        json={'message': 'Hey gabe'}
                    ),
                    response=Response(
                        json={'message': 'Ayee whatsup'},
                        status_code=200
                    )
                )
            ]
        )

        # When
        pact_json = build_pact_json(pact)

        # Then
        expected = {
            'consumer': {'name': 'Zach'},
            'provider': {'name': 'Gabe'},
            'interactions': [
                {
                    'description': 'Zach messages gabe',
                    'providerStates': [{'name': 'Gabe is online'}],
                    'request': {
                        'method': 'POST',
                        'path': '/gabe',
                        'body': {'message': 'Hey gabe'}
                    },
                    'response': {
                        'body': {'message': 'Ayee whatsup'},
                        'status': 200
                    }
                }
            ],
            'metadata': {
                'pactSpecification': {'version': '3.0.0'}
            }
        }
        assert pact_json == expected
