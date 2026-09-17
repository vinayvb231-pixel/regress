"""Terminal and Markdown reporters."""
from __future__ import annotations

from .runner import SuiteResult


def render_terminal(suite: SuiteResult) -> None:
    for r in suite.results:
        mark = "✓" if r.passed else "✗"
        print(f"{mark} {r.name}")
        if r.error:
            print(f"    error: {r.error}")
        for a in r.assertions:
            if not a.passed:
                print(f"    ✗ [{a.kind}] {a.detail}")
    print(f"\n{suite.passed_count}/{len(suite.results)} passed")


def render_markdown(suite: SuiteResult) -> str:
    lines = [
        "## regress report",
        "",
        f"**{suite.passed_count}/{len(suite.results)} tests passed**",
        "",
        "| test | result | failing checks |",
        "| ---- | ------ | -------------- |",
    ]
    for r in suite.results:
        result = "✅ pass" if r.passed else "❌ fail"
        failing = ", ".join(
            f"`{a.kind}`" for a in r.assertions if not a.passed
        ) or ("error" if r.error else "—")
        lines.append(f"| {r.name} | {result} | {failing} |")

    failures = [r for r in suite.results if not r.passed]
    if failures:
        lines += ["", "### failures", ""]
        for r in failures:
            lines.append(f"<details><summary><b>{r.name}</b></summary>")
            lines.append("")
            if r.error:
                lines.append(f"Error: `{r.error}`")
            else:
                for a in r.assertions:
                    if not a.passed:
                        lines.append(f"- ❌ `{a.kind}` — {a.detail}")
                lines.append("")
                lines.append("**Actual output:**")
                lines.append("")
                lines.append("```")
                lines.append(r.output.strip() or "(empty)")
                lines.append("```")
            lines.append("")
            lines.append("</details>")
            lines.append("")
    return "\n".join(lines)
