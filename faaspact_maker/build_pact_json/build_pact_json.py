from typing import Any, Dict, List, Optional, Union

from faaspact_maker import matchers
from faaspact_maker.definitions import (
    Interaction,
    Pact,
    ProviderState,
    RequestWithMatchers,
    ResponseWithMatchers
)


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


def _build_request(request_with_matchers: RequestWithMatchers) -> Dict:
    request = request_with_matchers.without_matchers()
    return _drop_none_values({
        **request._asdict(),
        'matchingRules': _build_request_matching_rules(request_with_matchers)
    })


def _build_response(response_with_matchers: ResponseWithMatchers) -> Dict:
    response = response_with_matchers.without_matchers()
    return _drop_none_values({
        **response._asdict(),
        'matchingRules': _build_response_matching_rules(response_with_matchers)
    })


def _build_request_matching_rules(request: RequestWithMatchers) -> Optional[Dict]:
    matching_rules: Dict = {}

    if isinstance(request.path, matchers.Regex):
        matching_rules['path'] = {
            'matchers': [_build_regex_matcher(request.path)]
        }

    if request.headers:
        matching_rules['header'] = _build_headers_matching_rules(request.headers)

    if request.body:
        matching_rules['body'] = _build_body_matching_rules(request.body)

    return _drop_none_values(matching_rules) or None


def _build_response_matching_rules(response: ResponseWithMatchers) -> Optional[Dict]:
    matching_rules: Dict = {}

    if response.headers:
        matching_rules['header'] = _build_headers_matching_rules(response.headers)

    if response.body:
        matching_rules['body'] = _build_body_matching_rules(response.body)

    return _drop_none_values(matching_rules) or None


def _build_body_matching_rules(body: Dict, parent: str = '$') -> Optional[Dict]:
    body_matching_rules: Dict = {}

    for field, value in body.items():
        child_matching_rule = _build_body_matching_rule(value, f'{parent}.{field}') or {}
        body_matching_rules = {**body_matching_rules, **child_matching_rule}

    return body_matching_rules or None


def _build_body_matching_rule(value: Any, key: str) -> Optional[Dict]:
    if isinstance(value, matchers.Regex):
            return {key: {'matchers': [_build_regex_matcher(value)]}}
    elif isinstance(value, dict):
        return _build_body_matching_rules(value, key) or None
    elif isinstance(value, list):
        return _build_body_matching_rules_for_list(value, key)
    else:
        return None


def _build_body_matching_rules_for_list(body_list: List, parent: str) -> Optional[Dict]:
    body_matching_rules: Dict = {}

    for index, value in enumerate(body_list):
        child_matching_rule = _build_body_matching_rule(value, f'{parent}[{index}]') or {}
        body_matching_rules = {**body_matching_rules, **child_matching_rule}

    return body_matching_rules or None


def _build_headers_matching_rules(headers: Dict[str, Union[str, matchers.Regex]]) -> Optional[Dict]:
    headers_matching_rules: Dict = {}

    for field, value in headers.items():
        if isinstance(value, matchers.Regex):
            headers_matching_rules[field] = {
                'matchers': [_build_regex_matcher(value)]
            }

    return headers_matching_rules or None


def _build_regex_matcher(regex_matcher: matchers.Regex) -> Dict:
    return {
        'match': 'regex',
        'regex': regex_matcher.pattern
    }


def _drop_none_values(dictionary: Dict) -> Dict:
    """Drops fields from a dictionary where value is None.

    >>> _drop_none_values({'greeting': 'hello', 'name': None})
    {'greeting': 'hello'}
    """
    return {key: value for key, value in dictionary.items() if value is not None}
