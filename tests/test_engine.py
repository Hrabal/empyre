from datetime import datetime, timedelta

import pytest

from empyre import Empyre


def test_engine():
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
                "expectations": [{"path": "$.foo", "operator": "eq", "value": "bar"}],
                "outcomes": [
                    {"typ": "VALUE", "value": "42"},
                    {"typ": "LOGIC", "logic_id": 2},
                ],
            },
            {
                "id": 2,
                "expectations": [{"path": "$.baz", "operator": "ge", "value": 42}],
                "outcomes": [{"typ": "VALUE", "value": True}],
                "root": False,
            },
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
                    {
                        "operator": "and",
                        "expectations": [
                            {"path": "$.baz", "operator": "ge", "value": 42},
                            {"path": "$.foo", "operator": "eq", "value": "bar"},
                        ],
                    }
                ],
                "outcomes": [
                    {"typ": "EVENT", "event_id": "test", "data": ["$.foo"]},
                ],
            }
        ],
        {"foo": "bar", "baz": 42},
    ).evaluate()
    outcome = next(result)
    assert outcome["typ"] == "EVENT"
    assert outcome["data"] == {"foo": "bar"}
    assert outcome["event_id"] == "test"

    result = Empyre(
        [
            {
                "id": 1,
                "name": "passing",
                "expectations": [
                    {
                        "operator": "and",
                        "expectations": [
                            {"path": "$.string", "operator": "eq", "value": "bar"},
                            {"path": "$.int", "operator": "ge", "value": 42},
                        ],
                    },
                    {
                        "operator": "or",
                        "expectations": [
                            {
                                "path": "$.past_datetime",
                                "operator": "eq",
                                "value": datetime.now(),
                            },
                            {
                                "path": "$.past_datetime",
                                "operator": "lt",
                                "value": datetime.now(),
                            },
                        ],
                    },
                    {"path": "$.zero", "operator": "lt", "value": 1},
                    {"path": "$.float", "operator": "gt", "value": -0.1},
                    {"path": "$.none", "operator": "eq", "value": None},
                    {"path": "$.none", "operator": "eq", "value": None},
                    {"path": "$.float", "comp": "not", "operator": "eq", "value": None},
                    {"path": "$.int", "comp": "not", "operator": "in", "value": [1, 2]},
                    {"path": "$.int_list[-1]", "operator": "in", "value": {3, 2}},
                    {"path": "$.str_list.`len`", "operator": "gt", "value": 0},
                    {
                        "path": "$.dict_list[?id = 1].field",
                        "operator": "eq",
                        "value": "test",
                    },
                    {
                        "path": "$.dict_list[?id > 1].field",
                        "operator": "eq",
                        "value": "test2",
                    },
                    {"path": "$.int_tuple[0] + $.int", "operator": "eq", "value": 43},
                    {"path": "$.nested.key", "operator": "like", "value": "a"},
                ],
                "outcomes": [
                    {"typ": "EVENT", "event_id": "test", "data": ["$.string"]},
                ],
            },
            {
                "id": 2,
                "name": "failing",
                "expectations": [
                    {"path": "$.nested.key", "operator": "like", "value": "failure"},
                ],
                "outcomes": [
                    {
                        "typ": "VALUE",
                        "value": "test",
                    },
                ],
            },
        ],
        {
            "string": "bar",
            "int": 42,
            "zero": 0,
            "float": 0.1,
            "none": None,
            "past_datetime": datetime.now() - timedelta(days=1),
            "int_list": [1, 2, 3],
            "str_list": ["a", "b", "baz"],
            "dict_list": [{"id": 1, "field": "test"}, {"id": 2, "field": "test2"}],
            "int_tuple": (1, 2, 3),
            "nested": {"key": "val"},
        },
    ).evaluate()
    outcome = next(result)
    assert outcome["typ"] == "EVENT"
    assert outcome["data"] == {"string": "bar"}
    assert outcome["event_id"] == "test"

    with pytest.raises(StopIteration):
        next(result)
