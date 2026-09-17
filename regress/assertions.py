"""Assertion types evaluated against a model output."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class AssertionResult:
    kind: str
    passed: bool
    detail: str


def _contains(spec, output, judge):
    ok = str(spec) in (output or "")
    return AssertionResult("contains", ok, f"expected output to contain {str(spec)!r}")


def _not_contains(spec, output, judge):
    ok = str(spec) not in (output or "")
    return AssertionResult("not_contains", ok, f"expected output NOT to contain {str(spec)!r}")


def _equals(spec, output, judge):
    ok = (output or "").strip() == str(spec).strip()
    return AssertionResult("equals", ok, "expected exact match")


def _regex(spec, output, judge):
    ok = re.search(str(spec), output or "", re.DOTALL) is not None
    return AssertionResult("regex", ok, f"expected output to match /{spec}/")


def _max_words(spec, output, judge):
    n = len((output or "").split())
    ok = n <= int(spec)
    return AssertionResult("max_words", ok, f"output is {n} words, max is {spec}")


def _llm_judge(spec, output, judge):
    criteria = spec.get("criteria") if isinstance(spec, dict) else spec
    passed, reason = judge(str(criteria), output or "")
    return AssertionResult("llm_judge", passed, f"judge: {reason}")


_HANDLERS = {
    "contains": _contains,
    "not_contains": _not_contains,
    "equals": _equals,
    "regex": _regex,
    "max_words": _max_words,
    "llm_judge": _llm_judge,
}


def evaluate(assertions: list, output: str, judge) -> list[AssertionResult]:
    results = []
    for a in assertions:
        if isinstance(a, str):
            kind, spec = "contains", a  # shorthand: "- hello" means contains "hello"
        else:
            kind, spec = next(iter(a.items()))
        handler = _HANDLERS.get(kind)
        if handler is None:
            results.append(
                AssertionResult(kind, False, f"unknown assertion '{kind}'")
            )
            continue
        try:
            results.append(handler(spec, output, judge))
        except Exception as e:  # noqa: BLE001 — surface assertion errors as failures
            results.append(AssertionResult(kind, False, f"assertion error: {e}"))
    return results
