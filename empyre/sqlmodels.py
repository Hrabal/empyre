try:
    from sqlmodel import Field, Relationship, SQLModel, create_engine
except ImportError as e:
    raise ImportError(
        "sqlmodel is not installed, run `pip install empyre[sqlmodel]`"
    ) from e

from .models import Matcher, Outcomes, OutcomeTypes, Rule


class MatcherMatchers(SQLModel, table=True):
    __tablename__ = "em_matcher_matchers"
    rule_id: int | None = Field(
        default=None, foreign_key="em_matchers.id", primary_key=True
    )
    matcher_id: int | None = Field(
        default=None, foreign_key="em_matchers.id", primary_key=True
    )


class DbMatcher(SQLModel, Matcher, table=True):
    __tablename__ = "em_matchers"

    id: int | None = Field(default=None, primary_key=True)
    matchers: list["DbMatcher"] = Relationship(link_model=MatcherMatchers)


class DbOutcome(SQLModel, table=True):
    __tablename__ = "em_outcomes"

    id: int | None = Field(default=None, primary_key=True)
    typ: OutcomeTypes
    name: str = None
    description: str = None
    value: bytes = None
    outputs: bytes = None
    event_id: str = None
    rule_id: int = None


class RuleMatchers(SQLModel, table=True):
    __tablename__ = "em_rule_matchers"
    rule_id: int | None = Field(
        default=None, foreign_key="em_rules.id", primary_key=True
    )
    matcher_id: int | None = Field(
        default=None, foreign_key="em_matchers.id", primary_key=True
    )


class RuleOutcomes(SQLModel, table=True):
    rule_id: int | None = Field(
        default=None, foreign_key="em_rules.id", primary_key=True
    )
    outcome_id: int | None = Field(
        default=None, foreign_key="em_outcomes.id", primary_key=True
    )


class DbRule(SQLModel, Rule, table=True):
    __tablename__ = "em_rules"

    id: int | None = Field(default=None, primary_key=True)
    matchers: list[DbMatcher] = Relationship(link_model=RuleMatchers)
    outcomes: list[DbOutcome] = Relationship(link_model=RuleOutcomes)
