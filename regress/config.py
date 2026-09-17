"""Load and validate regress.yaml."""
from __future__ import annotations

import yaml


class ConfigError(Exception):
    pass


DEFAULTS = {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "temperature": 0.0,
    "judge_model": None,  # defaults to `model` when unset
    "max_tokens": 512,
}


def load_config(path: str) -> dict:
    with open(path) as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ConfigError("top level of the config must be a mapping")

    defaults = {**DEFAULTS, **(raw.get("defaults") or {})}

    tests = raw.get("tests")
    if not isinstance(tests, list) or not tests:
        raise ConfigError("'tests' must be a non-empty list")

    normed = []
    for i, t in enumerate(tests):
        if not isinstance(t, dict) or "name" not in t or "prompt" not in t:
            raise ConfigError(f"test #{i} needs 'name' and 'prompt'")
        asserts = t.get("assert") or t.get("asserts") or []
        if isinstance(asserts, dict):
            asserts = [asserts]
        normed.append(
            {
                "name": t["name"],
                "prompt": t["prompt"],
                "inputs": t.get("inputs") or {},
                "assert": asserts,
                "mock_response": t.get("mock_response"),
                "provider": t.get("provider", defaults["provider"]),
                "model": t.get("model", defaults["model"]),
                "temperature": t.get("temperature", defaults["temperature"]),
            }
        )

    return {"defaults": defaults, "tests": normed}
