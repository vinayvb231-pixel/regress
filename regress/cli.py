"""CLI: `regress init` and `regress run`."""
from __future__ import annotations

import argparse
import json
import os
import sys

from . import __version__
from .config import ConfigError
from .report import render_markdown, render_terminal
from .runner import run_suite

STARTER = """\
version: 1

defaults:
  provider: openai        # openai | anthropic | mock
  model: gpt-4o-mini
  temperature: 0

tests:
  - name: answers_from_policy
    prompt: |
      You are a support bot. Answer using only this policy:
      {policy}
      Customer: {question}
    inputs:
      policy: "Refunds are available within 30 days of purchase."
      question: "Can I get a refund?"
    assert:
      - contains: "30 days"
      - not_contains: "cannot"

  # No API key handy? Use provider: mock with a canned response to try the harness:
  # - name: mock_example
  #   provider: mock
  #   prompt: "Say hello."
  #   mock_response: "Hello!"
  #   assert:
  #     - contains: "Hello"
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="regress",
        description="Regression testing for LLM prompts. Drop a regress.yaml in your repo; catch prompt breakages in CI.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("run", help="Run the test suite")
    r.add_argument("--config", default="regress.yaml", help="Path to regress.yaml")
    r.add_argument(
        "--format",
        choices=["terminal", "markdown", "json"],
        default="terminal",
        help="Report format",
    )
    r.add_argument("--output", default=None, help="Write the report to a file")
    r.add_argument("--fail-fast", action="store_true", help="Stop after the first failure")

    i = sub.add_parser("init", help="Write a starter regress.yaml in the current directory")
    i.add_argument("--force", action="store_true", help="Overwrite an existing regress.yaml")
    return p


def cmd_init(args: argparse.Namespace) -> int:
    path = os.path.join(os.getcwd(), "regress.yaml")
    if os.path.exists(path) and not args.force:
        print("regress.yaml already exists (use --force to overwrite)")
        return 2
    with open(path, "w") as f:
        f.write(STARTER)
    print("Wrote regress.yaml — edit it, then run: regress run")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    try:
        suite = run_suite(args.config, fail_fast=args.fail_fast)
    except ConfigError as e:
        print(f"config error: {e}", file=sys.stderr)
        return 2
    except FileNotFoundError:
        print(f"config not found: {args.config} (run `regress init` first)", file=sys.stderr)
        return 2

    if args.format == "terminal":
        render_terminal(suite)
    else:
        text = (
            render_markdown(suite)
            if args.format == "markdown"
            else json.dumps(suite.to_dict(), indent=2)
        )
        if args.output:
            with open(args.output, "w") as f:
                f.write(text)
            print(f"wrote {args.output}")
        else:
            print(text)

    return 0 if suite.all_passed else 1


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        sys.exit(cmd_run(args))
    elif args.command == "init":
        sys.exit(cmd_init(args))
