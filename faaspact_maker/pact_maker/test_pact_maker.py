import json
import tempfile
from typing import Dict, List

import requests

from faaspact_maker import (
    Interaction,
    PactMaker,
    ProviderState,
    RequestWithMatchers,
    ResponseWithMatchers
)
from faaspact_maker.matchers import Regex


class TestPactMaker():

    def test_works_for_pact_without_matchers(self) -> None:
        with tempfile.TemporaryDirectory() as mock_pact_dir:
            pact_maker = PactMaker(
                consumer_name='Zach',
                provider_name='Gabe',
                provider_url='https://zachgabechat.com',
                pact_directory=mock_pact_dir
            )

            pact_maker.add_interaction(Interaction(
                description='Zach messages gabe',
                provider_states=(ProviderState('Gabe is online'),),
                request=RequestWithMatchers(
                    method='POST',
                    path='/gabe',
                    body={'message': 'Hey gabe'}
                ),
                response=ResponseWithMatchers(
                    body={'message': 'Ayee whatsup'},
                    status=200
                )
            ))

            pact_maker.add_interaction(Interaction(
                description='Zach checks friends online',
                provider_states=(ProviderState('I have one friend online'),),
                request=RequestWithMatchers(
                    method='GET',
                    path='/friends',
                    query={'status': ['online']}
                ),
                response=ResponseWithMatchers(
                    body={'number': 1},
                    status=200
                )
            ))

            json_responses: List[Dict] = []

            with pact_maker.start_mocking():
                r = requests.post('https://zachgabechat.com/gabe', json={'message': 'Hey gabe'})
                json_responses.append(r.json())

                r = requests.get('https://zachgabechat.com/friends', params={'status': 'online'})
                json_responses.append(r.json())

                assert json_responses[0] == {'message': 'Ayee whatsup'}
                assert json_responses[1] == {'number': 1}

            with open(f'{mock_pact_dir}/Zach-Gabe.pact.json') as pact_file:
                pact_json = json.load(pact_file)

            expected_pact_json = {
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
                    },
                    {
                        'description': 'Zach checks friends online',
                        'providerStates': [{'name': 'I have one friend online'}],
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
        assert pact_json == expected_pact_json

    def test_mocks_for_pact_with_matchers(self) -> None:
        with tempfile.TemporaryDirectory() as mock_pact_dir:
            pact_maker = PactMaker(
                consumer_name='Zach',
                provider_name='Gabe',
                provider_url='https://zachgabechat.com',
                pact_directory=mock_pact_dir
            )

            pact_maker.add_interaction(Interaction(
                description='Zach messages gabe',
                provider_states=(ProviderState('Gabe is online'),),
                request=RequestWithMatchers(
                    method='POST',
                    path=Regex('/gabe', r'\/(gabe|gabriel)'),
                    body={'message': Regex('Hey gabe', r'(Hey|Yo) gabe')}
                ),
                response=ResponseWithMatchers(
                    body={'message': Regex('Ayee whatsup', r'Aye+ whatsup')},
                    status=200
                )
            ))

            pact_maker.add_interaction(Interaction(
                description='Zach checks friends online',
                provider_states=(ProviderState('I have one friend online'),),
                request=RequestWithMatchers(
                    method='GET',
                    path='/friends',
                    query={'status': ['online']}
                ),
                response=ResponseWithMatchers(
                    body={'number': 1},
                    status=200
                )
            ))

            json_responses: List[Dict] = []

            with pact_maker.start_mocking():
                r = requests.post('https://zachgabechat.com/gabe', json={'message': 'Hey gabe'})
                json_responses.append(r.json())

                r = requests.get('https://zachgabechat.com/friends', params={'status': 'online'})
                json_responses.append(r.json())

                assert json_responses[0] == {'message': 'Ayee whatsup'}
                assert json_responses[1] == {'number': 1}

            with open(f'{mock_pact_dir}/Zach-Gabe.pact.json') as pact_file:
                pact_json = json.load(pact_file)

            expected_pact_json = {
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
                            'matchingRules': {
                                'path': {
                                    'matchers': [
                                        {
                                            'match': 'regex',
                                            'regex': r'\/(gabe|gabriel)'
                                        }
                                    ]
                                },
                                'body': {
                                    '$.message': {'matchers': [
                                        {
                                            'match': 'regex',
                                            'regex': r'(Hey|Yo) gabe'
                                        }
                                    ]}
                                }
                            }
                        },
                        'response': {
                            'body': {'message': 'Ayee whatsup'},
                            'status': 200,
                            'matchingRules': {
                                'body': {
                                    '$.message': {
                                        'matchers': [{
                                            'match': 'regex',
                                            'regex': r'Aye+ whatsup'
                                        }]
                                    }
                                }
                            }
                        }
                    },
                    {
                        'description': 'Zach checks friends online',
                        'providerStates': [{'name': 'I have one friend online'}],
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
        assert pact_json == expected_pact_json


class TestNestedMocker:

    def test_works_for_one_nested_mocker(self) -> None:
        with tempfile.TemporaryDirectory() as mock_pact_dir:
            pact_maker_outer = PactMaker(
                consumer_name='Zach',
                provider_name='Gabe',
                provider_url='https://zachgabechat.com',
                pact_directory=mock_pact_dir
            )

            pact_maker_outer.add_interaction(Interaction(
                description='Zach messages gabe',
                provider_states=(ProviderState('Gabe is online'),),
                request=RequestWithMatchers(
                    method='POST',
                    path='/gabe',
                    body={'message': 'Hey gabe'}
                ),
                response=ResponseWithMatchers(
                    body={'message': 'Ayee whatsup'},
                    status=200
                )
            ))

            json_responses: List[Dict] = []

            with pact_maker_outer.start_mocking() as outer_mocker:
                pact_maker_inner = PactMaker(
                    consumer_name='Zach',
                    provider_name='Evan',
                    provider_url='https://zachevanchat.com',
                    pact_directory=mock_pact_dir
                )

                pact_maker_inner.add_interaction(Interaction(
                    description='Zach messages evan',
                    provider_states=(ProviderState('Evan is offline'),),
                    request=RequestWithMatchers(
                        method='POST',
                        path='/evan',
                        body={'message': 'Hey evan'}
                    ),
                    response=ResponseWithMatchers(
                        body={'message': 'Evan is not online'},
                        status=200
                    )
                ))

                with pact_maker_inner.start_mocking(outer=outer_mocker):
                    r = requests.post('https://zachgabechat.com/gabe', json={'message': 'Hey gabe'})
                    json_responses.append(r.json())

                    r = requests.post('https://zachevanchat.com/evan', json={'message': 'Hey evan'})
                    json_responses.append(r.json())

                assert json_responses[0] == {'message': 'Ayee whatsup'}
                assert json_responses[1] == {'message': 'Evan is not online'}

            with open(f'{mock_pact_dir}/Zach-Gabe.pact.json') as pact_file:
                gabe_pact_json = json.load(pact_file)

            with open(f'{mock_pact_dir}/Zach-Evan.pact.json') as pact_file:
                evan_pact_json = json.load(pact_file)

            expected_gabe_pact_json = {
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
        assert gabe_pact_json == expected_gabe_pact_json

        expected_evan_pact_json = {
                'consumer': {'name': 'Zach'},
                'provider': {'name': 'Evan'},
                'interactions': [
                    {
                        'description': 'Zach messages evan',
                        'providerStates': [{'name': 'Evan is offline'}],
                        'request': {
                            'method': 'POST',
                            'path': '/evan',
                            'body': {'message': 'Hey evan'}
                        },
                        'response': {
                            'body': {'message': 'Evan is not online'},
                            'status': 200
                        }
                    }
                ],
                'metadata': {
                    'pactSpecification': {'version': '3.0.0'}
                }
            }
        assert evan_pact_json == expected_evan_pact_json
