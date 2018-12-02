from faaspact_maker.definitions import Interaction, Pact, ProviderState, Request, Response
from faaspact_maker.matchers import Regex
from faaspact_maker.pact_file_gateway.pact_file_gateway import build_pact_json


class TestBuildPactJson():

    def test_builds_pact_for_post(self) -> None:
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
                        json={'message': 'Hey gabe'},
                        headers={'Authorization': 'Bearer ABCDE'}
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
                        'body': {'message': 'Hey gabe'},
                        'headers': {'Authorization': 'Bearer ABCDE'}
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

    def test_builds_pact_for_get(self) -> None:
        # Given
        pact = Pact(
            consumer_name='Zach',
            provider_name='Gabe',
            interactions=[
                Interaction(
                    provider_states=(ProviderState('Zach has one friend online'),),
                    description='Zach checks friends online',
                    request=Request(
                        method='GET',
                        path='/friends',
                        query={'status': ['online']}
                    ),
                    response=Response(
                        json={'number': 1},
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
                    'description': 'Zach checks friends online',
                    'providerStates': [{'name': 'Zach has one friend online'}],
                    'request': {
                        'method': 'GET',
                        'path': '/friends',
                        'query': {'status': ['online']}
                    },
                    'response': {
                        'body': {'number': 1},
                        'status': 200
                    }
                }
            ],
            'metadata': {
                'pactSpecification': {'version': '3.0.0'}
            }
        }
        assert pact_json == expected

    def test_builds_pact_with_path_regex_matcher(self) -> None:
        # Given
        pact = Pact(
            consumer_name='Zach',
            provider_name='Gabe',
            interactions=[
                Interaction(
                    description='Zach messages gabe',
                    request=Request(
                        method='POST',
                        path=Regex('/gabe', r'\/\w+')
                    ),
                    response=Response(
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
                    'request': {
                        'method': 'POST',
                        'path': '/gabe',
                        'matchingRules': {
                            'path': {
                                'matchers': [
                                    {
                                        'match': 'regex',
                                        'regex': r'\/\w+'
                                    }
                                ]
                            }
                        }
                    },
                    'response': {
                        'status': 200
                    }
                }
            ],
            'metadata': {
                'pactSpecification': {'version': '3.0.0'}
            }
        }
        assert pact_json == expected
