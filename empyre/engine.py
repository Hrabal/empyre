import logging
import re
from typing import Any
from uuid import uuid4

from jsonpath_ng.ext import parse

from .models import DataOutcome, Matcher, Operator, Outcomes, OutcomeTypes, Rule


class Empyre:
    """A class to evaluate rules against a context."""

    _logger = logging.getLogger("Empyre")

    def __init__(self, rules: list[dict | Rule] = None, ctx: dict = None):
        self.id = uuid4().hex
        self.rules = {}
        for i, rule in enumerate(rules or []):
            rule = Rule.model_validate(rule)
            rule.id = rule.id or i + 1
            self.rules[rule.id] = rule
        self.ctx = ctx or {}

    def _log(self, msg: str):
        self._logger.debug(f"Evaluation[{self.id}] {msg}")

    def outcomes(self):
        """
        Returns a generator of outcomes produced by
        the matching, applicable rules against the current context.
        """
        self._log(
            f"Evaluating rules {'-'.join(map(str, self.rules.values()))} rules against {self.ctx}"
        )
        for rule in self.rules.values():
            if not rule.applicable or not rule.root:
                continue
            yield from self._eval_rule(rule)

    def _eval_rule(self, rule: Rule):
        """
        Checks if matchers produce the desired outcome. Yields outcomes for matching rules.
        """
        matchers_result = self._match_matchers(rule.op, rule.matchers)
        self._log(
            f"{rule} with {len(rule.matchers)} matchers expects {rule.comp.truth} and matches {matchers_result}"
        )
        if matchers_result == rule.comp.truth:
            for outcome in rule.outcomes:
                yield from self._produce(outcome)

    @staticmethod
    def _prepare_val(val: Any, matcher: Matcher) -> Any:
        try:
            return matcher.transform(val)
        except (TypeError, ValueError):
            return val

    def _match_value(self, matcher: Matcher) -> bool:
        """
        Performs the matcher evaluation on the value.
        returns true if any of the values extracted using the
        jsonpath matches to the value using the operator.
        """
        matches = []
        # Extract values from the context using the jsonpath
        for el in parse(matcher.path).find(self.ctx):
            # Eventually apply a transformation on the found value
            val = self._prepare_val(el.value, matcher)
            if matcher.op == Operator.in_:
                # IN: the value is in the matcher iterable
                matches.append(val in matcher.value)
            elif matcher.op == Operator.re:
                # REGEX: use regex against the value
                matches.append(re.compile(matcher.value).match(val))
            elif (matcher.value is None or val is None) and matcher.op == Operator.eq:
                # EQ with Nones use `is`
                matches.append(val is matcher.value)
            elif matcher.op.comparison:
                # Comparisons + EQ with no Nones:
                # use the value's magic method for the
                # operator against the matcher value.
                fun = matcher.op.fun(val)
                matches.append(fun(matcher.value))
        return any(matches)

    def _match(self, matcher: Matcher) -> bool:
        """
        Executes the matcher on the context.
        Returns true is the match produces the expected truthness.
        """
        self._log(f"Matching {matcher}")
        if matcher.matchers:
            # Match sub-matchers with and/or logic
            match = self._match_matchers(matcher.op, matcher.matchers)
        else:
            # Match on the value
            match = self._match_value(matcher)
        self._log(f"{matcher} produces {match} and expects {matcher.comp.truth}")
        return match == matcher.comp.truth

    def _match_matchers(self, op: Operator, matchers: list[Matcher]) -> bool:
        """
        Accumulates results from matchers and applies the
        and/or logic, defaulting to False for no matchers.
        """
        matches = []
        for matcher in matchers:
            matches.append(self._match(matcher))
        return op.fun()(matches or (False,))

    def _produce(self, outcome: Outcomes):
        """Applies the outcome if needed , or yields the dumped outcome."""
        if outcome.typ == OutcomeTypes.RULE:
            child_rule = self.rules[outcome.rule_id]
            if child_rule.applicable:
                yield from self._eval_rule(child_rule)
        else:
            if isinstance(outcome, DataOutcome):
                ret = outcome.model_dump(self.ctx, mode="json")
            else:
                ret = outcome.model_dump(mode="json")
            ret["decision_id"] = self.id
            yield ret
