# regress

[![PyPI](https://img.shields.io/pypi/v/regress-llm.svg)](https://pypi.org/project/regress-llm/)
[![Python](https://img.shields.io/pypi/pyversions/regress-llm.svg)](https://pypi.org/project/regress-llm/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Regression testing for LLM prompts, built for CI.** One YAML file in your repo; prompt breakages fail the build like broken unit tests.

You changed a prompt. Or swapped models. Or your provider shipped a new snapshot. Did anything break? Right now you find out from customers. `regress` catches it on the PR instead.

Unlike heavyweight eval platforms, there's nothing to adopt: no dashboard to learn, no SDK to integrate, no service to run. Just a YAML file and a CI step.

```bash
pip install regress-llm          # Python 3.10+
regress init                     # writes a starter regress.yaml
regress run                      # runs your prompt tests
```

---

## 60-second quickstart (no API key needed)

```bash
<<<<<<< Updated upstream
pip install regress-ai
regress init        # writes a starter regress.yaml
regress run         # runs your prompt tests
=======
pip install regress-llm
mkdir demo && cd demo
regress init
regress run
>>>>>>> Stashed changes
```

```
✓ answers_from_policy

1/1 passed
```

The starter suite uses the `mock` provider, so it passes with zero setup. Edit `regress.yaml`, break a `mock_response`, run again — the test fails and the process exits with code `1`. That's the whole idea: **prompts as tests, failures as red builds.**

## Going live

<<<<<<< Updated upstream
1. Install: `pip install 'regress-ai[openai]'` (or `[anthropic]`, or `[all]`)
2. Set your key: `export OPENAI_API_KEY=...`
3. `regress init` and edit the generated `regress.yaml`
4. `regress run`
=======
Install with your provider's extra and set your key:
>>>>>>> Stashed changes

```bash
pip install 'regress-llm[openai]'      # or [anthropic], or [all]
export OPENAI_API_KEY=...
# export ANTHROPIC_API_KEY=...
```

Then point a test at the live model:

```yaml
tests:
  - name: refund_answer_uses_policy
    provider: openai
    model: gpt-4o-mini
    temperature: 0
    prompt: |
      You are a support bot. Answer using ONLY this policy:
      {policy}
      Customer: {question}
    inputs:
      policy: "Refunds are available within 30 days of purchase."
      question: "Can I get a refund for something I bought last week?"
    assert:
      - contains: "30 days"
      - not_contains: "cannot"
      - llm_judge:
          criteria: "The answer approves the refund and cites the 30-day policy"
```

See [`examples/support-bot/regress.yaml`](https://github.com/vinayvb231-pixel/regress/tree/main/examples/support-bot) for a complete live example.

---

## The YAML schema

```yaml
version: 1

defaults:
  provider: openai        # openai | anthropic | mock
  model: gpt-4o-mini
  temperature: 0
  judge_model: gpt-4o     # model used for llm_judge (defaults to `model`)
  max_tokens: 512

tests:
  - name: refund_answer_uses_policy
    prompt: |
      You are a support bot. Answer using ONLY this policy:
      {policy}
      Customer: {question}
    inputs:
      policy: "Refunds within 30 days."
      question: "Can I get a refund?"
    # provider / model / temperature can be overridden per test
    mock_response: "..."  # only for provider: mock — canned output, no API call
    assert:
      - contains: "30 days"
```

- `{placeholders}` in `prompt` are filled from `inputs` (escape literal braces as `{{` / `}}`).
- `mock_response` is required for `mock` tests and ignored otherwise. Mock tests run with zero keys — great for trying the harness and for the repo's own CI.

## Assertions

| Assertion | Example | Passes when |
|---|---|---|
| `contains` | `- contains: "30 days"` | output includes the substring |
| `not_contains` | `- not_contains: "cannot"` | output excludes the substring |
| `equals` | `- equals: "exact text"` | output matches exactly (after stripping) |
| `regex` | `- regex: "\\$\\d+"` | the pattern matches |
| `max_words` | `- max_words: 50` | output is at most N words |
| `llm_judge` | `- llm_judge: {criteria: "..."}` | a judge model says the output meets the criteria |

Shorthand: a bare string in the assert list means `contains`, so `- "30 days"` works too.

`llm_judge` uses `judge_model` (or the test's `model` when unset) to evaluate free-form criteria — useful for assertions you can't express as substrings, like tone, completeness, or policy compliance. It costs one extra model call per test.

## Providers

| Provider | Extra | Key env var |
|---|---|---|
| `mock` | — (built in) | — |
| `openai` | `regress-llm[openai]` | `OPENAI_API_KEY` |
| `anthropic` | `regress-llm[anthropic]` | `ANTHROPIC_API_KEY` |

## CLI

```
regress init [--force]                 # write a starter regress.yaml
regress run [--config regress.yaml]    # run the suite
            [--format terminal|markdown|json]
            [--output report.md]
            [--fail-fast]
regress --version
```

**Formats:** `terminal` (default, human-readable), `markdown` (for PR comments), `json` (for piping into other tools).

**Exit codes:** `0` all passed · `1` failures · `2` config error. CI fails the check on regressions automatically.

---

## CI: GitHub Action

This repo dogfoods itself — [`.github/workflows/regress.yml`](https://github.com/vinayvb231-pixel/regress/blob/main/.github/workflows/regress.yml) runs the suite on every PR and comments a Markdown report on the PR. To use it in your repo:

```yaml
<<<<<<< Updated upstream
- run: pip install regress-ai
- run: regress run --format markdown --output regress-report.md
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
=======
name: regress

"on":
  pull_request:

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  prompt-regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install regress-llm
      - run: regress run --format markdown --output regress-report.md
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      - name: Comment report on PR
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const body = fs.readFileSync('regress-report.md', 'utf8');
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: body,
            });
>>>>>>> Stashed changes
```

The `if: always()` on the comment step means the report lands on the PR even when tests fail — which is exactly when you want to read it.

### The report

`--format markdown` produces a summary table like:

```markdown
## regress report — 2/3 passed

| test | result | detail |
|---|---|---|
| refund_policy_mentions_window | ✓ | |
| refuses_disallowed_request | ✗ | expected output to contain "can't help" |
| stays_concise | ✓ | |
```

## Examples

- [`regress.yaml`](https://github.com/vinayvb231-pixel/regress/blob/main/regress.yaml) — the repo's own suite (mock; this is what our CI runs)
- [`examples/support-bot/`](https://github.com/vinayvb231-pixel/regress/tree/main/examples/support-bot) — live OpenAI support-bot suite
- [`examples/failing-demo/`](https://github.com/vinayvb231-pixel/regress/tree/main/examples/failing-demo) — intentionally failing suite, for trying the failure output

## How this differs

Tools like Promptfoo, Braintrust, and LangSmith are full eval platforms — powerful, but they're a thing to adopt. `regress` is the opposite bet: prompt tests should live next to your unit tests, run in the CI you already have, and fail the build the same way. If you outgrow a YAML file, those platforms will be waiting.

## Roadmap

- [ ] **Baseline diffs** — compare against the last green run, not just assertions
- [ ] **Flaky detection** — re-run failures N times before calling them real (LLM outputs are non-deterministic; the harness should know that)
- [ ] **Model-migration diffing** — run the suite against two models, get a behavior-change report
- [ ] **Hosted** — history, trends, and alerts across runs

## Contributing

PRs welcome. Please run the mock suite before pushing:

```bash
python -m pip install -e .
regress run
```

## License

MIT — see [LICENSE](https://github.com/vinayvb231-pixel/regress/blob/main/LICENSE).
