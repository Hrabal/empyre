from datetime import datetime
from enum import StrEnum
from typing import Any, Callable, Literal

from jsonpath_ng.exceptions import JSONPathError
from jsonpath_ng.ext import parse
from pydantic import BaseModel, Field


class CompNone:
    """Utility class to handle comparisons with None."""

    def __eq__(self, other):
        """Only None returns True"""
        return other is None

    def __ge__(self, other):
        """Only None returns True"""
        return self.__eq__(other)

    def __le__(self, other):
        """Only None returns True"""
        return self.__eq__(other)

    def __gt__(self, other):
        """Everything is not greater"""
        return False

    def __lt__(self, other):
        """Everything is not lesser"""
        raise False


class Comparator(StrEnum):
    """The expected result of a Match."""

    is_ = "is"
    not_ = "not"

    @property
    def truth(self) -> bool:
        """Returns the expected truth value of a Match."""
        return self == self.is_


class Operator(StrEnum):
    """Comparison operators to use when matching."""

    and_ = "and"
    or_ = "or"
    eq = "eq"
    gt = "gt"
    lt = "lt"
    ge = "ge"
    le = "le"
    in_ = "in"
    lk = "like"

    @property
    def logical(self) -> bool:
        """Returns true for logical operators (and/or)"""
        return self in {self.and_, self.or_}

    @property
    def comparison(self) -> bool:
        """Returns true for comparison operators (==/</<=/>/>=)"""
        return self in {
            self.eq,
            self.gt,
            self.lt,
            self.ge,
            self.le,
        }

    def fun(self, value: Any = None) -> Callable:
        """
        Returns the python function of the operator.
        Non-logical operators returns a method of the given value.
        """
        if self.logical:
            return all if self == self.and_ else any
        if value is None:
            # For comparisons with None, we use CompNone
            # to avoid NotImplemented exceptions
            value = CompNone()
        return getattr(value, f"__{self}__")


class EmpyreModel(BaseModel):
    """Base class for Empyre models"""

    id: int = Field(None, description="Unique id")
    name: str = Field(None, description="Human-readable name")
    description: str = Field(
        None, description="Complete description of the defined Empyre entity"
    )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id or self.name or ''})"

    def __str__(self):
        return self.__repr__()


class Matcher(EmpyreModel):
    """A Matcher is a condition to evaluate."""

    path: str = Field(
        None, description="A jsonpath for extracting values from the context."
    )
    comp: Comparator = Field(
        Comparator.is_, description="The expected truthness of the match."
    )
    op: Operator = Field(..., description="The comparison operator to use.")
    value: Any = Field(None, description="The value to compare against/with.")
    transform: Callable = Field(
        None, description="Optional values transformation before comparisons."
    )
    matchers: list["Matcher"] = Field(
        None, description="Optional list of other Matchers to use with the given op."
    )

    def __repr__(self):
        cond_repr = f"{self.path} {self.comp} {self.op} {self.value}"
        if self.op.logical:
            cond_repr = self.op
        return f"{super().__repr__()}<{cond_repr}>"


class OutcomeTypes(StrEnum):
    LOGIC = "LOGIC"
    VALUE = "VALUE"
    DATA = "DATA"
    EVENT = "EVENT"


class Outcome(EmpyreModel):
    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        ret = super().model_dump(*args, **kwargs)
        ret.pop("name")
        ret.pop("description")
        return ret


class RuleOutcome(Outcome):
    """
    Outcome that will evaluate and apply the specified rule,
    allowing for creating evaluation directed graphs.
    """

    typ: Literal[OutcomeTypes.LOGIC] = OutcomeTypes.LOGIC
    rule_id: int = Field(..., description="The rule id to evaluate next.")


class ValueOutcome(Outcome):
    """Simple value outcome"""

    typ: Literal[OutcomeTypes.VALUE] = OutcomeTypes.VALUE
    value: Any = Field(..., description="The value to return.")


class DataOutcome(Outcome):
    """
    Outcome that when dumped will contain multiple values.
    The `data` attribute will be used build a data key in the returned dict,
    for each element:
        - if a jsonpath is provided, the corresponding stuff is
          extracted from context and added to the result
        - any non jsonapth item will be added to the `values` list
    """

    typ: Literal[OutcomeTypes.DATA] = OutcomeTypes.DATA
    data: list[Any] = Field(
        default_factory=list, description="A list of values or jsonpaths."
    )

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        ctx, *args = args
        ret = super().model_dump(*args, **kwargs)
        ret["data"] = {}
        for el in self.data:
            print(el)
            try:
                matches = parse(el).find(ctx)
                if not matches:
                    raise JSONPathError()
                for match in matches:
                    ret["data"][str(match.path)] = match.value
            except JSONPathError:
                ret.setdefault("data", {}).setdefault("values", []).append(el)
        return ret


class EventOutcome(DataOutcome):
    """
    Extension of the DataOutcome.
    Intended to specify an event to trigger with the extracted data.
    """

    typ: Literal[OutcomeTypes.EVENT] = OutcomeTypes.EVENT
    event_id: str = Field(..., description="The event unique identifier.")


Outcomes = RuleOutcome | ValueOutcome | EventOutcome


class Rule(EmpyreModel):
    """A Rule will evaluate matchers and produce outcomes with an expected match."""

    since: datetime | None = Field(None, description="Rule validity start.")
    until: datetime | None = Field(None, description="Rule validity end.")
    active: bool = Field(True, description="Flag used to deactivate a rule.")
    root: bool = Field(True, description="Set this to false for child-only rules.")
    comp: Comparator = Field(
        Comparator.is_, description="The expected truthness of the match."
    )
    op: Literal[Operator.and_, Operator.or_] = Field(
        Operator.and_, description="AND/OR condition for the matchers."
    )
    matchers: list[Matcher] = Field(
        default_factory=list, description="The matchers to evaluate."
    )
    outcomes: list[Outcomes] = Field(
        default_factory=list, description="The outcomes in case of positive match."
    )

    @property
    def applicable(self):
        """Checks the rule's activeness and time boundaries."""
        now = datetime.now()
        return self.active and ((self.since or now) <= now <= (self.until or now))

    def __repr__(self):
        return f"{super().__repr__()}<{self.comp} {self.op}>"
