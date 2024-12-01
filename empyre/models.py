from datetime import datetime
from enum import StrEnum
from typing import Any, Callable, Literal

from jsonpath_ng.ext import parse
from pydantic import BaseModel, Field


class Operator(StrEnum):
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
        return self in {self.and_, self.or_}

    @property
    def comparison(self) -> bool:
        return self in {self.eq, self.gt, self.lt, self.ge, self.le, }

    @property
    def belonging(self) -> bool:
        return self in {self.in_, self.lk}

    def fun(self, inst: Any = None) -> Callable:
        if self.logical:
            return all if self == self.and_ else any
        if self.belonging:
            return getattr(inst, "__contains__")
        return getattr(inst, f"__{self}__")

    def eval(self, v1: Any, v2: Any):
        if self.logical:
            return self.fun()((v1, v2))
        elif self.comparison:
            return self.fun(v1)(type(v1)(v2))
        elif self.belonging:
            return self.fun(v2)(v1)


class EmpyreEntity(BaseModel):
    id: int | None = None
    name: str | None = None

    def __str__(self):
        return f"{self.__class__.__name__}({self.id})<{self.name}>"


class Expectation(EmpyreEntity):
    path: str
    truthfulness: bool = True
    operator: Operator
    ignore_case: bool = False
    value: list["Expectation"] | Any

    @property
    def recursive(self):
        try:
            return isinstance(self.value[0], self.__class__)
        except (TypeError, IndexError):
            return False


class OutcomeTypes(StrEnum):
    LOGIC = "LOGIC"
    VALUE = "VALUE"
    EVENT = "EVENT"


class RuleOutcome(EmpyreEntity):
    typ: Literal[OutcomeTypes.LOGIC]
    logic_id: int


class ValueOutcome(EmpyreEntity):
    typ: Literal[OutcomeTypes.VALUE]
    value: Any


class EventOutcome(EmpyreEntity):
    typ: Literal[OutcomeTypes.EVENT]
    event_id: str
    data: list[str]

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        ctx, *args = args
        ret = super().model_dump(*args, **kwargs)
        ret["data"] = [v.value for jpath in self.data for v in parse(jpath).find(ctx)]
        return ret


Outcomes = RuleOutcome | ValueOutcome | EventOutcome


class Rule(EmpyreEntity):
    description: str | None = None
    since: datetime | None = None
    until: datetime | None = None
    active: bool = True
    root: bool = True
    expectations: list[Expectation] = Field(default_factory=list)
    outcomes: list[Outcomes] = Field(default_factory=list)

    @property
    def applicable(self):
        now = datetime.now()
        return self.active and ((self.since or now) <= now <= (self.until or now))
