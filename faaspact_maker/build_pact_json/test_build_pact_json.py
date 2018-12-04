from faaspact_maker.build_pact_json import build_pact_json
from faaspact_maker.definitions import (
    Interaction,
    Pact,
    ProviderState,
    RequestWithMatchers,
    ResponseWithMatchers
)
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
                    request=RequestWithMatchers(
                        method='POST',
                        path='/gabe',
                        body={'message': 'Hey gabe'},
                        headers={'Authorization': 'Bearer ABCDE'}
                    ),
                    response=ResponseWithMatchers(
                        body={'message': 'Ayee whatsup'},
                        headers={'Content-Type': 'application/json'},
                        status=200
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
                    request=RequestWithMatchers(
                        method='GET',
                        path='/friends',
                        query={'status': ['online']}
                    ),
                    response=ResponseWithMatchers(
                        body={'number': 1},
                        status=200
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
                    request=RequestWithMatchers(
                        method='POST',
                        path=Regex('/gabe', r'\/\w+')
                    ),
                    response=ResponseWithMatchers(
                        status=200
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
                    request=RequestWithMatchers(
                        method='POST',
                        path='/gabe',
                        headers={'Authorization': Regex('Bearer ABCDE', r'Bearer \S+')}
                    ),
                    response=ResponseWithMatchers(
                        status=200,
                        headers={'Age': Regex('12', r'\d+')}
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
                                        'regex': r'Bearer \S+'
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
                                        'regex': r'\d+'
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
                    request=RequestWithMatchers(
                        method='POST',
                        path='/gabe',
                        body={'message': Regex('yooo', r'yo+')}
                    ),
                    response=ResponseWithMatchers(
                        status=200,
                        body={'message': Regex('ayee whatsup', r'aye+ whatsup')}
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
                                        'regex': r'yo+',
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
                                        'regex': r'aye+ whatsup',
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
                    request=RequestWithMatchers(
                        method='POST',
                        path='/gabe',
                        body={'message': {'contents': Regex('yooo', r'yo+')}}
                    ),
                    response=ResponseWithMatchers(
                        status=200,
                        body={'message': {'contents': Regex('ayee whatsup', r'aye+ whatsup')}}
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
                                        'regex': r'yo+',
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
                                        'regex': r'aye+ whatsup',
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
                    request=RequestWithMatchers(
                        method='POST',
                        path='/gabe',
                        body={'messages': [Regex('yooo', r'yo+')]}
                    ),
                    response=ResponseWithMatchers(
                        status=200,
                        body={'messages': [Regex('ayee whatsup', r'aye+ whatsup')]}
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
                                        'regex': r'yo+',
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
                                        'regex': r'aye+ whatsup',
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


# will be feeling good once build_pact_json can build this
goal = {
    "provider": {"name": "test_provider_array"},
    "consumer": {"name": "test_consumer_array"},
    "interactions": [
        {
            "description": "java test interaction with a DSL array body",
            "request": {"method": "GET", "path": "/"},
            "response": {
                "status": 200,
                "headers": {
                    "Content-Type": "application/json; charset=UTF-8"
                },
                "body": [
                    {
                        "dob": "07/19/2016",
                        "id": 8958464620,
                        "name": "Rogger the Dogger",
                        "timestamp": "2016-07-19T12:14:39",
                    },
                    {
                        "dob": "07/19/2016",
                        "id": 4143398442,
                        "name": "Cat in the Hat",
                        "timestamp": "2016-07-19T12:14:39",
                    },
                ],
                "matchingRules": {
                    "body": {
                        "$[0].id": {
                            "matchers": [{"match": "type"}]
                        },
                        "$[1].id": {
                            "matchers": [{"match": "type"}]
                        },
                    }
                },
            },
        },
        {
            "description": "test interaction with a array body with templates",
            "request": {"method": "GET", "path": "/"},
            "response": {
                "status": 200,
                "headers": {
                    "Content-Type": "application/json; charset=UTF-8"
                },
                "body": [
                    {
                        "dob": "2016-07-19",
                        "id": 1943791933,
                        "name": "ZSAICmTmiwgFFInuEuiK",
                    },
                    {
                        "dob": "2016-07-19",
                        "id": 1943791933,
                        "name": "ZSAICmTmiwgFFInuEuiK",
                    },
                    {
                        "dob": "2016-07-19",
                        "id": 1943791933,
                        "name": "ZSAICmTmiwgFFInuEuiK",
                    },
                ],
                "matchingRules": {
                    "body": {
                        "$[2].name": {
                            "matchers": [{"match": "type"}]
                        },
                        "$[0].id": {
                            "matchers": [{"match": "type"}]
                        },
                        "$[1].id": {
                            "matchers": [{"match": "type"}]
                        },
                        "$[2].id": {
                            "matchers": [{"match": "type"}]
                        },
                        "$[1].name": {
                            "matchers": [{"match": "type"}]
                        },
                        "$[0].name": {
                            "matchers": [{"match": "type"}]
                        },
                        "$[0].dob": {
                            "matchers": [
                                {"date": "yyyy-MM-dd"}
                            ]
                        },
                    }
                },
            },
        },
        {
            "description": "test interaction with an array like matcher",
            "request": {"method": "GET", "path": "/"},
            "response": {
                "status": 200,
                "headers": {
                    "Content-Type": "application/json; charset=UTF-8"
                },
                "body": {
                    "data": {
                        "array1": [
                            {
                                "dob": "2016-07-19",
                                "id": 1600309982,
                                "name": "FVsWAGZTFGPLhWjLuBOd",
                            }
                        ],
                        "array2": [
                            {
                                "address": "127.0.0.1",
                                "name": "jvxrzduZnwwxpFYrQnpd",
                            }
                        ],
                        "array3": [
                            [{"itemCount": 652571349}]
                        ],
                    },
                    "id": 7183997828,
                },
                "matchingRules": {
                    "body": {
                        "$.data.array3[0]": {
                            "matchers": [
                                {"max": 5, "match": "type"}
                            ]
                        },
                        "$.data.array1": {
                            "matchers": [
                                {"min": 0, "match": "type"}
                            ]
                        },
                        "$.data.array2": {
                            "matchers": [
                                {"min": 1, "match": "type"}
                            ]
                        },
                        "$.id": {
                            "matchers": [{"match": "type"}]
                        },
                        "$.data.array3[0][*].itemCount": {
                            "matchers": [
                                {"match": "integer"}
                            ]
                        },
                        "$.data.array2[*].name": {
                            "matchers": [{"match": "type"}]
                        },
                        "$.data.array2[*].address": {
                            "matchers": [
                                {
                                    "regex": "(\\d{1,3}\\.)+\\d{1,3}"
                                }
                            ]
                        },
                        "$.data.array1[*].name": {
                            "matchers": [{"match": "type"}]
                        },
                        "$.data.array1[*].id": {
                            "matchers": [{"match": "type"}]
                        },
                    }
                },
            },
        },
    ],
    "metadata": {"pactSpecification": {"version": "3.0.0"}},
}
