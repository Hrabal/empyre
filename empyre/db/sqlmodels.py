from datetime import datetime
from typing import Literal

from sqlmodel import Field, Relationship, SQLModel, String

from empyre.models import Comparator, EmpyreModel, Operator, OutcomeTypes


class MatcherMatchers(SQLModel, table=True):
    __tablename__ = "em_matcher_matchers"

    rule_id: int | None = Field(
        default=None, foreign_key="em_matchers.id", primary_key=True
    )
    matcher_id: int | None = Field(
        default=None, foreign_key="em_matchers.id", primary_key=True
    )


class DbMatcher(SQLModel, EmpyreModel, table=True):
    __tablename__ = "em_matchers"

    id: int | None = Field(default=None, primary_key=True)
    path: str
    comp: Comparator
    op: Operator
    value: str | None = None
    value_type: str | None = None
    transform: str | None = None
    matchers: list["DbMatcher"] = Relationship(link_model=MatcherMatchers)


class DbOutcome(SQLModel, EmpyreModel, table=True):
    __tablename__ = "em_outcomes"

    id: int | None = Field(default=None, primary_key=True)
    typ: OutcomeTypes
    name: str | None = None
    description: str | None = None
    value: str | None = None
    outputs: str | None = None
    event_id: str | None = None
    rule_id: int | None = None


class RuleMatchers(SQLModel, table=True):
    __tablename__ = "em_rule_matchers"
    rule_id: int | None = Field(
        default=None, foreign_key="em_rules.id", primary_key=True
    )
    matcher_id: int | None = Field(
        default=None, foreign_key="em_matchers.id", primary_key=True
    )


class RuleOutcomes(SQLModel, table=True):
    __tablename__ = "em_rule_outcomes"
    rule_id: int | None = Field(
        default=None, foreign_key="em_rules.id", primary_key=True
    )
    outcome_id: int | None = Field(
        default=None, foreign_key="em_outcomes.id", primary_key=True
    )


class DbRule(SQLModel, EmpyreModel, table=True):
    __tablename__ = "em_rules"

    id: int | None = Field(default=None, primary_key=True)
    since: datetime | None = None
    until: datetime | None = None
    active: bool = True
    root: bool = True
    comp: Comparator = Comparator.is_
    op: Literal[Operator.and_, Operator.or_] = Field(Operator.and_, sa_type=String)

    matchers: list[DbMatcher] = Relationship(link_model=RuleMatchers)
    outcomes: list[DbOutcome] = Relationship(link_model=RuleOutcomes)
