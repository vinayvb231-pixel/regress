"""Model providers. openai/anthropic are lazy-imported so the CLI works
without their SDKs installed (e.g. when only using the mock provider)."""
from __future__ import annotations


def complete(test: dict, defaults: dict, prompt_text: str) -> str:
    provider = test["provider"]

    if provider == "mock":
        if test.get("mock_response") is None:
            raise RuntimeError(
                f"test '{test['name']}': the mock provider needs 'mock_response' "
                "set on the test"
            )
        return test["mock_response"]

    if provider == "openai":
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError(
                "the openai package is not installed — run: pip install 'regress-ai[openai]'"
            )
        client = OpenAI()  # reads OPENAI_API_KEY from the environment
        resp = client.chat.completions.create(
            model=test["model"],
            messages=[{"role": "user", "content": prompt_text}],
            temperature=test["temperature"],
            max_tokens=defaults.get("max_tokens", 512),
        )
        return resp.choices[0].message.content or ""

    if provider == "anthropic":
        try:
            import anthropic
        except ImportError:
            raise RuntimeError(
                "the anthropic package is not installed — run: pip install 'regress-ai[anthropic]'"
            )
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
        resp = client.messages.create(
            model=test["model"],
            max_tokens=defaults.get("max_tokens", 512),
            temperature=test["temperature"],
            messages=[{"role": "user", "content": prompt_text}],
        )
        return "".join(block.text for block in resp.content if block.type == "text")

    raise RuntimeError(f"unknown provider '{provider}' (use openai, anthropic, or mock)")


def make_judge(defaults: dict):
    """Return a callable (criteria, output) -> (passed: bool, reason: str)."""
    provider = defaults["provider"]
    if provider == "mock":
        def _mock_judge(criteria, output):
            raise RuntimeError(
                "llm_judge needs a real model provider — set defaults.provider "
                "to openai or anthropic"
            )

        return _mock_judge

    model = defaults.get("judge_model") or defaults["model"]

    def judge(criteria: str, output: str):
        prompt = (
            "You are evaluating an AI response against a criterion.\n"
            f"Criterion: {criteria}\n\nResponse:\n{output}\n\n"
            "Does the response satisfy the criterion? "
            "Reply with YES or NO on the first line, then a one-sentence reason."
        )
        verdict_text = complete(
            {"provider": provider, "model": model, "temperature": 0.0, "name": "__judge__"},
            defaults,
            prompt,
        )
        lines = verdict_text.strip().splitlines()
        first = lines[0].strip().upper() if lines else ""
        passed = first.startswith("YES")
        reason = lines[1].strip() if len(lines) > 1 else verdict_text.strip()
        return passed, reason

    return judge
