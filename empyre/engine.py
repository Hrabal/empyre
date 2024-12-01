import logging
import traceback
from uuid import uuid4

from jsonpath_ng.ext import parse
from pydantic import TypeAdapter

from .models import Expectation, Operator, Outcomes, OutcomeTypes, Rule


class Empyre:
    _rules_adapter = TypeAdapter(list[Rule])
    _logger = logging.getLogger("Empyre")

    def __init__(self, rules: list[dict | Rule] = None, ctx: dict = None):
        self.rules = list(map(Rule.model_validate, rules or []))
        self.ctx = ctx or {}
        self.id = None

    def evaluate(self):
        self.id = uuid4().hex
        active_rules = list(filter(lambda r: r.root and r.applicable, self.rules))
        self._log(f"{self.ctx} against rules {' '.join(map(str, active_rules))}")
        for rule in active_rules:
            yield from self._eval_rule(rule)

    def _eval_rule(self, rule: Rule):
        if self._match_expectations(Operator.and_, rule.expectations):
            for outcome in rule.outcomes:
                yield from self.apply(outcome)

    def _match(self, exp: Expectation) -> bool:
        self._log(f"Matching {exp}")
        if exp.recursive:
            return self._match_expectations(exp.operator, exp.value)
        ctx_vals = parse(exp.path).find(self.ctx)
        v_transformation = str.lower if exp.ignore_case else lambda i: i
        match = any(exp.op.eval(*map(v_transformation, (el.value, exp.value))) for el in ctx_vals)
        self._log(f"{exp} matches to {match}")
        return match == exp.truthfulness

    def _match_expectations(self, op: Operator, expectations: list[Expectation]):
        return op.fun()(map(self._match, expectations))

    def _log(self, msg: str):
        self._logger.debug(f"Evaluation[{self.id}] {msg}")

    def apply(self, outcome: Outcomes):
        self._log(f"Applying {outcome}")
        if outcome.typ == OutcomeTypes.LOGIC:
            child_rule = next(filter(lambda r: r.id == outcome.logic_id, self.rules))
            yield from self._eval_rule(child_rule)

        if outcome.typ == OutcomeTypes.EVENT:
            ret = outcome.model_dump(self.ctx, mode="json")
        else:
            ret = outcome.model_dump(mode="json")
        ret["decision_id"] = self.id
        yield ret
