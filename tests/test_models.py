from empyre.models import Operator


def test_fun():
    fun = Operator.and_.fun()
    assert callable(fun)
    assert fun is all

    fun = Operator.or_.fun()
    assert callable(fun)
    assert fun is any

    for case_val, ko in (
        (1, 2),
        ("a", "b"),
    ):
        fun = Operator.eq.fun(case_val)
        assert callable(fun)
        assert type(case_val).__eq__(case_val, case_val) == fun(case_val)
        assert type(case_val).__eq__(case_val, ko) == fun(ko)

    for case_val, ko in (
        (1, 2),
        ("a", "b"),
    ):
        fun = Operator.ne.fun(case_val)
        assert callable(fun)
        assert type(case_val).__ne__(case_val, case_val) == fun(case_val)
        assert type(case_val).__ne__(case_val, ko) == fun(ko)

    for case_val, ko, ko2 in (
        (1, 2, -1),
        ("b", "a", "c"),
    ):
        fun = Operator.gt.fun(case_val)
        assert callable(fun)
        assert type(case_val).__gt__(case_val, case_val) == fun(case_val)
        assert type(case_val).__gt__(case_val, ko) == fun(ko)
        assert type(case_val).__gt__(case_val, ko2) == fun(ko2)

    for case_val, ko, ko2 in (
        (1, 2, -1),
        ("b", "a", "c"),
    ):
        fun = Operator.lt.fun(case_val)
        assert callable(fun)
        assert type(case_val).__lt__(case_val, case_val) == fun(case_val)
        assert type(case_val).__lt__(case_val, ko) == fun(ko)
        assert type(case_val).__lt__(case_val, ko2) == fun(ko2)

    for case_val, ko, ko2 in (
        (1, 2, -1),
        ("b", "a", "c"),
    ):
        fun = Operator.ge.fun(case_val)
        assert callable(fun)
        assert type(case_val).__ge__(case_val, case_val) == fun(case_val)
        assert type(case_val).__ge__(case_val, ko) == fun(ko)
        assert type(case_val).__ge__(case_val, ko2) == fun(ko2)

    for case_val, ko, ko2 in (
        (1, 2, -1),
        ("b", "a", "c"),
    ):
        fun = Operator.le.fun(case_val)
        assert callable(fun)
        assert type(case_val).__le__(case_val, case_val) == fun(case_val)
        assert type(case_val).__le__(case_val, ko) == fun(ko)
        assert type(case_val).__le__(case_val, ko2) == fun(ko2)

    for case_val, ok, ko in (("123", "2", "4"), ([1, 2, 3], 2, 4), ((1, 2, 3), 2, 4)):
        fun = Operator.in_.fun(case_val)
        assert callable(fun)
        assert fun(ok)
        assert not fun(ko)
        assert case_val.__contains__(ok) == fun(ok)
        assert case_val.__contains__(ko) == fun(ko)

    fun = Operator.like.fun("122")
    assert callable(fun)
    assert fun("1")
    assert "122".__contains__("1")
    assert "122".__contains__("1") == fun("1")
    assert "122".__contains__("3") == fun("3")
