from faaspact_maker.build_pact_json import build_pact_json
from faaspact_maker.definitions import Interaction, Pact, ProviderState, Request, Response
from faaspact_maker.matchers import Regex


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
                        headers={'Content-Type': 'application/json'},
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
                        'headers': {'Content-Type': 'application/json'},
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

    def test_builds_pact_with_headers_regex_matcher(self) -> None:
        # Given
        pact = Pact(
            consumer_name='Zach',
            provider_name='Gabe',
            interactions=[
                Interaction(
                    description='Zach messages gabe',
                    request=Request(
                        method='POST',
                        path='/gabe',
                        headers={'Authorization': Regex('Bearer ABCDE', r'Bearer \S\+')}
                    ),
                    response=Response(
                        status_code=200,
                        headers={'Age': Regex('12', r'\d\+')}
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
                        'headers': {'Authorization': 'Bearer ABCDE'},
                        'matchingRules': {
                            'header': {
                                'Authorization': {
                                    'matchers': [{
                                        'match': 'regex',
                                        'regex': r'Bearer \S\+'
                                    }]
                                }
                            }
                        }
                    },
                    'response': {
                        'status': 200,
                        'headers': {'Age': '12'},
                        'matchingRules': {
                            'header': {
                                'Age': {
                                    'matchers': [{
                                        'match': 'regex',
                                        'regex': r'\d\+'
                                    }]
                                }
                            }
                        }
                    }
                }
            ],
            'metadata': {
                'pactSpecification': {'version': '3.0.0'}
            }
        }
        assert pact_json == expected

    def test_builds_pact_with_body_regex_matcher_top_level(self) -> None:
        # Given
        pact = Pact(
            consumer_name='Zach',
            provider_name='Gabe',
            interactions=[
                Interaction(
                    description='Zach messages gabe',
                    request=Request(
                        method='POST',
                        path='/gabe',
                        json={'message': Regex('yooo', r'yo\+')}
                    ),
                    response=Response(
                        status_code=200,
                        json={'message': Regex('ayee whatsup', r'aye\+ whatsup')}
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
                        'body': {'message': 'yooo'},
                        'matchingRules': {
                            'body': {
                                '$.message': {
                                    'matchers': [{
                                        'match': 'regex',
                                        'regex': r'yo\+',
                                    }]
                                }
                            }
                        }
                    },
                    'response': {
                        'status': 200,
                        'body': {'message': 'ayee whatsup'},
                        'matchingRules': {
                            'body': {
                                '$.message': {
                                    'matchers': [{
                                        'match': 'regex',
                                        'regex': r'aye\+ whatsup',
                                    }]
                                }
                            }
                        }
                    }
                }
            ],
            'metadata': {
                'pactSpecification': {'version': '3.0.0'}
            }
        }
        assert pact_json == expected

    def test_builds_pact_with_body_regex_matcher_nested(self) -> None:
        # Given
        pact = Pact(
            consumer_name='Zach',
            provider_name='Gabe',
            interactions=[
                Interaction(
                    description='Zach messages gabe',
                    request=Request(
                        method='POST',
                        path='/gabe',
                        json={'message': {'contents': Regex('yooo', r'yo\+')}}
                    ),
                    response=Response(
                        status_code=200,
                        json={'message': {'contents': Regex('ayee whatsup', r'aye\+ whatsup')}}
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
                        'body': {'message': {'contents': 'yooo'}},
                        'matchingRules': {
                            'body': {
                                '$.message.contents': {
                                    'matchers': [{
                                        'match': 'regex',
                                        'regex': r'yo\+',
                                    }]
                                }
                            }
                        }
                    },
                    'response': {
                        'status': 200,
                        'body': {'message': {'contents': 'ayee whatsup'}},
                        'matchingRules': {
                            'body': {
                                '$.message.contents': {
                                    'matchers': [{
                                        'match': 'regex',
                                        'regex': r'aye\+ whatsup',
                                    }]
                                }
                            }
                        }
                    }
                }
            ],
            'metadata': {
                'pactSpecification': {'version': '3.0.0'}
            }
        }
        assert pact_json == expected

    def test_builds_pact_with_body_regex_matcher_list(self) -> None:
        # Given
        pact = Pact(
            consumer_name='Zach',
            provider_name='Gabe',
            interactions=[
                Interaction(
                    description='Zach messages gabe',
                    request=Request(
                        method='POST',
                        path='/gabe',
                        json={'messages': [Regex('yooo', r'yo\+')]}
                    ),
                    response=Response(
                        status_code=200,
                        json={'messages': [Regex('ayee whatsup', r'aye\+ whatsup')]}
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
                        'body': {'messages': ['yooo']},
                        'matchingRules': {
                            'body': {
                                '$.messages[0]': {
                                    'matchers': [{
                                        'match': 'regex',
                                        'regex': r'yo\+',
                                    }]
                                }
                            }
                        }
                    },
                    'response': {
                        'status': 200,
                        'body': {'messages': ['ayee whatsup']},
                        'matchingRules': {
                            'body': {
                                '$.messages[0]': {
                                    'matchers': [{
                                        'match': 'regex',
                                        'regex': r'aye\+ whatsup',
                                    }]
                                }
                            }
                        }
                    }
                }
            ],
            'metadata': {
                'pactSpecification': {'version': '3.0.0'}
            }
        }
        assert pact_json == expected
