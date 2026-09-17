# Launch posts for regress

Copy-paste ready. Post Show HN on a Tuesday–Thursday morning US time for best visibility.

---

## 1. Hacker News — Show HN

**Title:** Show HN: Regress – regression testing for LLM prompts in CI

**Body:**

I kept breaking prompts and finding out from users instead of CI. Changed a system prompt, swapped a model, and something subtle regressed — no test caught it because there were no tests.

regress is the thinnest possible fix: a `regress.yaml` in your repo that runs your prompts against assertions on every PR. If a prompt change breaks behavior, the build goes red like a broken unit test.

```yaml
tests:
  - name: refund_answer_uses_policy
    prompt: |
      You are a support bot. Answer using ONLY this policy:
      {policy}
      Customer: {question}
    inputs:
      policy: "Refunds are available within 30 days of purchase."
      question: "Can I get a refund?"
    assert:
      - contains: "30 days"
      - llm_judge:
          criteria: "The answer approves the refund and cites the policy"
```

Assertions: contains, regex, exact match, word cap, and llm_judge (a model checks the output against your criterion). OpenAI + Anthropic supported, plus a mock provider so the harness runs with zero API keys. GitHub Action included — it comments a Markdown report on the PR.

Why not LangSmith/Braintrust? Those are powerful platforms you have to adopt. This is one YAML file and 5 minutes. It's deliberately small.

It's early (v0.1.0) and MIT licensed. I'd love feedback on what's missing — baseline diffs vs. the last green run and RAG faithfulness checks are next on my list unless you convince me otherwise.

Repo: <YOUR GITHUB URL>

---

## 2. Reddit — r/SideProject

**Title:** I built open-source regression testing for LLM prompts — broken prompts fail your CI like broken unit tests

**Body:**

Side project I've been hacking on: **regress**.

The problem: I was shipping AI features and every prompt tweak was a leap of faith. Change the system prompt, swap models, and something subtle breaks — you find out from users, not tests.

What it does: you add a `regress.yaml` to your repo with your prompts and assertions (`contains`, `regex`, `llm_judge`, etc.). A GitHub Action runs them on every PR and comments the report. Red build = broken prompt behavior.

The whole pitch vs. existing eval platforms: 5-minute setup, one YAML file, nothing to adopt. And there's a mock provider so you can try the whole thing without any API keys.

It's v0.1.0, MIT licensed, and very much early. Roast it — what's the first thing you'd need before trusting it in your repo?

Repo: <YOUR GITHUB URL>

---

## 3. X / Twitter thread

1/ I kept breaking LLM prompts and finding out from users instead of CI. So I built the thinnest possible fix: regress — prompt regression tests that run on every PR. Open source, MIT.

2/ The whole thing is one YAML file in your repo:

tests:
  - name: refund_answer
    prompt: "Answer using ONLY: {policy} ..."
    assert:
      - contains: "30 days"
      - llm_judge: { criteria: "cites the policy" }

3/ Change a prompt, break a behavior → the build goes red, with the actual output in the PR comment. Like unit tests, but for prompts.

4/ Deliberately tiny vs. LangSmith/Braintrust: no platform to adopt, no dashboard to learn. 5-minute setup. There's even a mock provider so it runs with zero API keys.

5/ v0.1.0, early, and I'd love your harshest feedback. What's the first thing missing before you'd trust it?

<YOUR GITHUB URL>
