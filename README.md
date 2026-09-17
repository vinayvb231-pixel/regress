# regress

Dead-simple regression testing for LLM prompts, built for CI. One YAML file in your repo; prompt breakages fail the build like broken unit tests.

```bash
pip install regress-ai
regress init        # writes a starter regress.yaml
regress run         # runs your prompt tests
```

## Why

You changed a prompt. Or swapped models. Did anything break? Right now you find out from customers. `regress` catches it on the PR instead.

Unlike heavyweight eval platforms, there's nothing to adopt: no dashboard to learn, no SDK to integrate. Just a YAML file and a GitHub Action.

## 5-minute quickstart

1. Install: `pip install 'regress-ai[openai]'` (or `[anthropic]`, or `[all]`)
2. Set your key: `export OPENAI_API_KEY=...`
3. `regress init` and edit the generated `regress.yaml`
4. `regress run`

No key handy? Use `provider: mock` with `mock_response` on a test to try the harness with zero setup (see the repo's own `regress.yaml`).

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
    assert:
      - contains: "30 days"      # substring must appear
      - not_contains: "cannot"   # substring must NOT appear
      - regex: "\\$\\d+"         # regex must match
      - equals: "exact text"     # exact match after stripping
      - max_words: 50            # output word count cap
      - llm_judge:               # ask a model whether the output meets a criterion
          criteria: "The answer approves the refund and cites the policy"
```

Any test can override `provider`, `model`, or `temperature` individually. `{placeholders}` in `prompt` are filled from `inputs` (escape literal braces as `{{` / `}}`).

## CLI

```
regress run [--config regress.yaml] [--format terminal|markdown|json]
            [--output report.md] [--fail-fast]
regress init [--force]
```

Exit codes: `0` all passed, `1` failures, `2` config error — so CI fails the check on regressions automatically.

## GitHub Action

This repo dogfoods itself: [`.github/workflows/regress.yml`](.github/workflows/regress.yml) runs the suite on every PR and comments a Markdown report. To use it in your repo:

```yaml
- run: pip install regress-ai
- run: regress run --format markdown --output regress-report.md
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## Roadmap

- [ ] Baseline diffs: compare against the last green run, not just assertions
- [ ] Flaky detection: re-run failures N times before calling them real
- [ ] RAG-aware assertions: faithfulness / citation checks against retrieved context
- [ ] Hosted: history, trends, and alerts across runs (the paid tier)

## Contributing

PRs welcome. Run the mock suite before pushing: `python -m regress run`.
