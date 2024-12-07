import logging
from uuid import uuid4
from typing import Any

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
        self._log(f"Eval {self.ctx} against rules {' '.join(map(str, active_rules))}")
        for rule in active_rules:
            yield from self._eval_rule(rule)

    def _eval_rule(self, rule: Rule):
        out = self._match_expectations(Operator.and_, rule.expectations)
        self._log(f"{rule} outcome: {out}")
        if out:
            for outcome in rule.outcomes:
                yield from self.apply(outcome)

    @staticmethod
    def _prepare_val(val: Any, exp: Expectation) -> Any:
        if exp.ignore_case and isinstance(val, str):
            val = val.lower()
        return val

    def _match(self, exp: Expectation) -> bool:
        self._log(f"Matching {exp}")
        if exp.expectations:
            match = self._match_expectations(exp.operator, exp.expectations)
            self._log(f"{exp} matches to {match}")
            return match
        matches = []
        vals = []
        for el in parse(exp.path).find(self.ctx):
            val = self._prepare_val(el.value, exp)
            vals.append(val)
            if exp.operator == Operator.in_:
                matches.append(val in exp.value)
            elif exp.operator == Operator.lk:
                matches.append(exp.value in val)
            elif (exp.value is None or val is None) and exp.operator == Operator.eq:
                matches.append(val is exp.value)
            elif exp.operator.comparison:
                fun = exp.operator.fun(val)
                matches.append(fun(exp.value))
        if not any(matches) == exp.comp.truth:
            self._log(f"{exp.comp.truth=}: {matches=} {vals=}")
        return any(matches) == exp.comp.truth

    def _match_expectations(self, op: Operator, expectations: list[Expectation]) -> bool:
        res = list(map(self._match, expectations))
        return op.fun()(res)

    def _log(self, msg: str):
        print(f"Evaluation[{self.id}] {msg}")
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
