"""Run a suite of prompt tests and collect results."""
from __future__ import annotations

from dataclasses import dataclass, field

from .assertions import evaluate
from .config import load_config
from .providers import complete, make_judge


@dataclass
class TestResult:
    name: str
    passed: bool
    output: str
    assertions: list = field(default_factory=list)
    error: str | None = None


@dataclass
class SuiteResult:
    results: list[TestResult]

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    def to_dict(self) -> dict:
        return {
            "passed": self.all_passed,
            "summary": f"{self.passed_count}/{len(self.results)} passed",
            "tests": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "error": r.error,
                    "output": r.output,
                    "assertions": [
                        {"kind": a.kind, "passed": a.passed, "detail": a.detail}
                        for a in r.assertions
                    ],
                }
                for r in self.results
            ],
        }


def render_prompt(test: dict) -> str:
    try:
        return test["prompt"].format(**test["inputs"])
    except KeyError as e:
        raise RuntimeError(f"test '{test['name']}': missing input {e}")
    except IndexError as e:
        raise RuntimeError(
            f"test '{test['name']}': bad placeholder in prompt ({e}). "
            "Escape literal braces as {{ and }}."
        )


def run_suite(config_path: str, fail_fast: bool = False) -> SuiteResult:
    cfg = load_config(config_path)
    defaults = cfg["defaults"]
    judge = make_judge(defaults)

    results: list[TestResult] = []
    for t in cfg["tests"]:
        try:
            prompt_text = render_prompt(t)
            output = complete(t, defaults, prompt_text)
            assertion_results = evaluate(t["assert"], output, judge)
            passed = all(a.passed for a in assertion_results)
            results.append(TestResult(t["name"], passed, output, assertion_results))
        except Exception as e:  # noqa: BLE001 — a broken test is a failed test
            results.append(TestResult(t["name"], False, "", [], error=str(e)))
        if fail_fast and not results[-1].passed:
            break
    return SuiteResult(results)
