import pytest

from empyre import Empyre


def test_enging():
    result = Empyre(
        [
            {
                "expectations": [{"path": "$.foo", "operator": "eq", "value": "bar"}],
                "outcomes": [{"typ": "VALUE", "value": "42"}],
            }
        ],
        {"foo": "bar"},
    ).evaluate()
    outcome = next(result)
    assert outcome["typ"] == "VALUE"
    assert outcome["value"] == "42"

    result = Empyre(
        [
            {
                "expectations": [{"path": "$.foo", "operator": "eq", "value": "baz"}],
                "outcomes": [{"typ": "VALUE", "value": "42"}],
            }
        ],
        {"foo": "bar"},
    ).evaluate()
    with pytest.raises(StopIteration):
        next(result)

    result = Empyre(
        [
            {
                "expectations": [
                    {"path": "$.foo", "operator": "eq", "value": "bar"}
                ],
                "outcomes": [
                    {"typ": "VALUE", "value": "42"},
                    {"typ": "LOGIC", "logic_id": 2},
                ],
            },
            {
                "id": 2,
                "expectations": [
                    {"path": "$.baz", "operator": "ge", "value": 42}
                ],
                "outcomes": [{"typ": "VALUE", "value": True}],
                "root": False
            }
        ],
        {"foo": "bar", "baz": 42},
    ).evaluate()
    outcome = next(result)
    assert outcome["typ"] == "VALUE"
    assert outcome["value"] == "42"
    outcome = next(result)
    assert outcome["typ"] == "VALUE"
    assert outcome["value"]

    result = Empyre(
        [
            {
                "expectations": [
                    {"operator": "and", "value": [
                        {"path": "$.baz", "operator": "ge", "value": 42},
                        {"path": "$.foo", "operator": "eq", "value": "bar"}
                    ]}
                ],
                "outcomes": [
                    {"typ": "VALUE", "value": "42"},
                ],
            }
        ],
        {"foo": "bar", "baz": 42},
    ).evaluate()
    outcome = next(result)
    assert outcome["typ"] == "VALUE"
    assert outcome["value"] == "42"
