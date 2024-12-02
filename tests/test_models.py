from datetime import datetime, timedelta

import pytest

from empyre.models import Operator, Rule, Expectation, EventOutcome


def test_fun():
    fun = Operator.and_.fun()
    assert callable(fun)
    assert fun is all

    fun = Operator.or_.fun()
    assert callable(fun)
    assert fun is any

    for op, expected_fun in (
        (Operator.eq, "__eq__"),
        (Operator.gt, "__gt__"),
        (Operator.lt, "__lt__"),
        (Operator.ge, "__ge__"),
        (Operator.le, "__le__"),
    ):
        for v1, v2 in (
            (1, 2),
            (1, -1),
            ("a", "b"),
            (True, False),
            (1, False),
            (0, False),
        ):
            fun = op.fun(v1)
            assert callable(fun)
            assert getattr(type(v1), expected_fun)(v1, v1) == fun(v1)
            assert getattr(type(v1), expected_fun)(v1, v2) == fun(v2)

    for case_val, v in (
        ("123", "2"),
        ([1, 2, 3], 2),
        ((1, 2, 3), 4),
        ([1, 2, 3], 2),
        ([1, 2, 3], 4),
        ({1, 2, 3}, 2),
        ({1, 2, 3}, 4),
    ):
        fun = Operator.in_.fun(case_val)
        assert callable(fun)
        assert case_val.__contains__(v) == fun(v)

    for case_val, v in (
        ("foo", "o"),
        ("foo", "bar"),
        ("foo", "bar"),
    ):
        fun = Operator.lk.fun("foo")
        assert callable(fun)
        assert (v in case_val) == fun(v)


def test_eval():
    for v1, v2 in (
        (True, False),
        (True, True),
        (None, False),
        (None, True),
        (None, 1),
        (None, 0),
        ("a", 0),
        ("a", "b"),
    ):
        assert Operator.and_.eval(v1, v2) == all((v1, v2))

    for v1, v2 in (
        (True, False),
        (True, True),
        (None, False),
        (None, True),
        (None, 1),
        (None, 0),
        (-1, 1),
        (1, -1),
        ("a", 0),
        ("a", "b"),
    ):
        assert Operator.eq.eval(v1, v2) == (v1 == v2)

    for v1, v2 in (
        (True, False),
        (True, True),
        (None, False),
        (None, True),
        (None, 1),
        (None, 0),
        (-1, 1),
        (1, -1),
        ("a", 0),
        ("a", "b"),
    ):
        if v1 is None:
            assert Operator.gt.eval(v1, v2) == bool(v2)
        else:
            assert Operator.gt.eval(v1, v2) == (v1 > Operator._cast(v1, v2))

    for v1, v2 in (
        (True, False),
        (True, True),
        (None, False),
        (None, True),
        (None, 1),
        (None, 0),
        (-1, 1),
        (1, -1),
        ("a", 0),
        ("a", "b"),
    ):
        if v1 is None:
            with pytest.raises(TypeError):
                assert Operator.lt.eval(v1, v2)
        else:
            assert Operator.lt.eval(v1, v2) == (v1 < Operator._cast(v1, v2))

    for v1, v2 in (
        (True, False),
        (True, True),
        (None, False),
        (None, True),
        (None, 1),
        (None, 0),
        (-1, 1),
        (1, -1),
        ("a", 0),
        ("a", "b"),
    ):
        if v1 is None:
            assert Operator.ge.eval(v1, v2)
        else:
            assert Operator.ge.eval(v1, v2) == (v1 >= Operator._cast(v1, v2))

    for v1, v2 in (
        (True, False),
        (True, True),
        (None, False),
        (None, True),
        (None, 1),
        (None, 0),
        (-1, 1),
        (1, -1),
        ("a", 0),
        ("a", "b"),
    ):
        if v1 is None:
            assert Operator.le.eval(v1, v2) == (not bool(v2))
        else:
            assert Operator.le.eval(v1, v2) == (v1 <= Operator._cast(v1, v2))

    for v1, v2 in (
        ("123", "2"),
        ([1, 2, 3], 2),
        ((1, 2, 3), 4),
        ([1, 2, 3], 2),
        ([1, 2, 3], 4),
        ({1, 2, 3}, 2),
        ({1, 2, 3}, 4),
    ):
        fun = Operator.in_.fun(v1)
        assert callable(fun)
        assert Operator.in_.eval(v2, v1) == (v2 in v1)

    for v1, v2 in (
        ("foo", "o"),
        ("foo", "bar"),
        ("foo", "bar"),
    ):
        assert Operator.lk.eval(v2, v1) == (v2 in v1)


def test_models():
    assert not Rule(active=False).applicable
    assert not Rule(since=datetime.now() + timedelta(seconds=1)).applicable
    assert not Rule(until=datetime.now() - timedelta(seconds=1)).applicable
    assert not Rule(
        since=datetime.now() - timedelta(seconds=2),
        until=datetime.now() - timedelta(seconds=1)
    ).applicable
    assert not Rule(
        since=datetime.now() + timedelta(seconds=1),
        until=datetime.now() + timedelta(seconds=2)
    ).applicable
    assert not Rule(
        active=False,
        since=datetime.now() - timedelta(seconds=1),
        until=datetime.now() + timedelta(seconds=1)
    ).applicable

    assert Rule().applicable
    assert Rule(
        since=datetime.now() - timedelta(seconds=1),
        until=datetime.now() + timedelta(seconds=1)
    ).applicable

    assert EventOutcome(event_id="test", data=[
        "$.foo",
        "$.bar",
        "$.bazinga.bam"
    ]).model_dump(
        {"foo": "foz", "bar": "baz", "bazinga": {"bam": "bazingaz"}},
        mode="json"
    ) == {
        "id": None,
        "name": None,
        "typ": "EVENT",
        "event_id": "test",
        "data": {
            "foo": "foz",
            "bar": "baz",
            "bam": "bazingaz",
        }
    }

    assert str(EventOutcome(id=1, name="test", event_id="1")) == "EventOutcome(1)<test>"

    exp1 = Expectation(path="$.foo", operator=Operator.eq, value="bar")
    assert not exp1.recursive
    exp2 = Expectation(path="$.foo", operator=Operator.eq, value=1)
    assert not exp2.recursive
    exp3 = Expectation(path="$.baz", operator=Operator.eq, value=[exp1, exp2])
    assert exp3.recursive
