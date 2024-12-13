from datetime import datetime, timedelta

import pytest

from empyre import Empyre


def test_empty_engine():
    # Test no outcomes with no rules
    results = Empyre().outcomes()
    assert not list(results)

    # Test no outcomes with no ctx
    results = Empyre(
        [
            {
                "matchers": [{"path": "$.foo", "op": "eq", "value": "bar"}],
                "outcomes": [{"typ": "VALUE", "value": "42"}],
            }
        ]
    ).outcomes()
    assert not list(results)


def test_comparison():
    # Test simple eq
    result = Empyre(
        [
            {
                "matchers": [{"path": "$.foo", "op": "eq", "value": "bar"}],
                "outcomes": [{"typ": "VALUE", "value": "42"}],
            }
        ],
        {"foo": "bar"},
    ).outcomes()
    # Should produce the defined outcome
    outcome = next(result)
    assert outcome["typ"] == "VALUE"
    assert outcome["value"] == "42"
    # Should not produce any other outcomes
    with pytest.raises(StopIteration):
        next(result)

    # Test no outcome with failing matcher
    result = Empyre(
        [
            {
                "matchers": [{"path": "$.foo", "op": "eq", "value": "baz"}],
                "outcomes": [{"typ": "VALUE", "value": "42"}],
            }
        ],
        {"foo": "bar"},
    ).outcomes()
    # Should not produce outcomes
    with pytest.raises(StopIteration):
        next(result)


def test_none_comparison():
    # Test comparison with None
    result = Empyre(
        [
            {
                "matchers": [{"path": "$.foo", "op": "eq", "value": None}],
                "outcomes": [{"typ": "VALUE", "value": "42"}],
            },
            {
                "matchers": [{"path": "$.foo", "op": "gt", "value": "test"}],
                "outcomes": [{"typ": "VALUE", "value": "43"}],
            },
            {
                "matchers": [{"path": "$.foo", "op": "lt", "value": "test"}],
                "outcomes": [{"typ": "VALUE", "value": "44"}],
            },
            {
                "matchers": [{"path": "$.foo", "op": "le", "value": "test"}],
                "outcomes": [{"typ": "VALUE", "value": "45"}],
            },
            {
                "matchers": [{"path": "$.foo", "op": "ge", "value": "test"}],
                "outcomes": [{"typ": "VALUE", "value": "46"}],
            },
        ],
        {"foo": None},
    ).outcomes()
    # Should produce the outcome of the first rule
    outcome = next(result)
    assert outcome["typ"] == "VALUE"
    assert outcome["value"] == "42"
    # All other rules should not produce outcomes
    with pytest.raises(StopIteration):
        next(result)


def test_nested():
    # Test nested rules
    result = Empyre(
        [
            {
                "matchers": [{"path": "$.foo", "op": "eq", "value": "bar"}],
                "outcomes": [
                    {"typ": "VALUE", "value": "42"},
                    {"typ": "RULE", "rule_id": 2},
                ],
            },
            {
                "id": 2,
                "matchers": [{"path": "$.baz", "op": "ge", "value": 42}],
                "outcomes": [{"typ": "VALUE", "value": True}],
                "root": False,
            },
        ],
        {"foo": "bar", "baz": 42},
    ).outcomes()
    # Should produce both rule's outcomes
    outcome = next(result)
    assert outcome["typ"] == "VALUE"
    assert outcome["value"] == "42"
    outcome = next(result)
    assert outcome["typ"] == "VALUE"
    assert outcome["value"]

    # Test nested matchers
    result = Empyre(
        [
            {
                "matchers": [
                    {
                        "op": "and",
                        "matchers": [
                            {"path": "$.baz", "op": "ge", "value": 42},
                            {"path": "$.foo", "op": "eq", "value": "bar"},
                        ],
                    },
                ],
                "outcomes": [
                    {"typ": "VALUE", "value": "42"},
                ],
            },
            {
                "matchers": [
                    {
                        "op": "or",
                        "matchers": [
                            {"path": "$.baz", "op": "ge", "value": 42},
                            {"path": "$.foo", "op": "eq", "value": "bam"},
                        ],
                    },
                ],
                "outcomes": [
                    {"typ": "VALUE", "value": "43"},
                ],
            },
            {
                "matchers": [
                    {
                        "op": "and",
                        "matchers": [
                            {"path": "$.baz", "op": "ge", "value": 42},
                            {"path": "$.foo", "op": "eq", "value": "bam"},
                        ],
                    },
                ],
                "outcomes": [
                    {"typ": "VALUE", "value": "44"},
                ],
            },
            {
                "matchers": [
                    {
                        "op": "or",
                        "matchers": [
                            {"path": "$.baz", "op": "lt", "value": 42},
                            {"path": "$.foo", "op": "eq", "value": "bam"},
                        ],
                    },
                ],
                "outcomes": [
                    {"typ": "VALUE", "value": "45"},
                ],
            },
        ],
        {"foo": "bar", "baz": 42},
    ).outcomes()
    # Should produce the first rule's output
    outcome = next(result)
    assert outcome["typ"] == "VALUE"
    assert outcome["value"] == "42"
    # Should produce the second rule's output
    outcome = next(result)
    assert outcome["typ"] == "VALUE"
    assert outcome["value"] == "43"
    # Should not produce any more output
    with pytest.raises(StopIteration):
        next(result)


def test_event_rendering():
    # Test event outcome:
    result = Empyre(
        [
            {
                "matchers": [{"path": "$.baz", "op": "ge", "value": 42}],
                "outcomes": [
                    {"typ": "EVENT", "event_id": "test", "data": ["$.foo", "test"]},
                ],
            }
        ],
        {"foo": "bar", "baz": 42},
    ).outcomes()
    # Should produce an outcome with populated data
    outcome = next(result)
    assert outcome["typ"] == "EVENT"
    assert outcome["data"] == {"foo": "bar", "values": ["test"]}
    assert outcome["event_id"] == "test"


def test_complex_rules():
    # Test complex rules/all operators
    result = Empyre(
        [
            {
                "id": 1,
                "name": "passing",
                "matchers": [
                    {
                        "op": "and",
                        "matchers": [
                            {"path": "$.string", "op": "eq", "value": "bar"},
                            {"path": "$.int", "op": "ge", "value": 42},
                        ],
                    },
                    {
                        "op": "or",
                        "matchers": [
                            {
                                "path": "$.past_datetime",
                                "op": "eq",
                                "value": datetime.now(),
                            },
                            {
                                "path": "$.past_datetime",
                                "op": "lt",
                                "value": datetime.now(),
                            },
                        ],
                    },
                    {"path": "$.zero", "op": "lt", "value": 1},
                    {"path": "$.float", "op": "gt", "value": -0.1},
                    {"path": "$.none", "op": "eq", "value": None},
                    {"path": "$.none", "op": "eq", "value": None},
                    {"path": "$.float", "comp": "not", "op": "eq", "value": None},
                    {"path": "$.int", "comp": "not", "op": "in", "value": [1, 2]},
                    {"path": "$.int_list[-1]", "op": "in", "value": {3, 2}},
                    {"path": "$.str_list.`len`", "op": "gt", "value": 0},
                    {
                        "path": "$.dict_list[?id = 1].field",
                        "op": "eq",
                        "value": "test",
                    },
                    {
                        "path": "$.dict_list[?id > 1].field",
                        "op": "eq",
                        "value": "test2",
                    },
                    {"path": "$.int_tuple[0] + $.int", "op": "eq", "value": 43},
                    {"path": "$.nested.key", "op": "re", "value": ".*v.*"},
                ],
                "outcomes": [
                    {"typ": "EVENT", "event_id": "test", "data": ["$.string"]},
                ],
            },
            {
                "id": 2,
                "name": "failing",
                "matchers": [
                    {"path": "$.nested.key", "op": "re", "value": "failure"},
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
    ).outcomes()
    # Should only produce the first rule outcome
    outcome = next(result)
    assert outcome["typ"] == "EVENT"
    assert outcome["data"] == {"string": "bar"}
    assert outcome["event_id"] == "test"
    with pytest.raises(StopIteration):
        next(result)
