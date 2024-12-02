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
