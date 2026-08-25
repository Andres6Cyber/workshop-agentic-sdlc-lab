"""Integration tests verifying parse_usage and score compose correctly.

Loads the usage fixture, parses it into snapshots, and scores each account.
"""

from __future__ import annotations

from main import load_export
from usage import Result, parse_usage, score


def test_end_to_end_scoring_on_fixture():
    export_text = load_export()
    accounts = parse_usage(export_text)

    results = {account: score(months) for account, months in accounts.items()}

    assert results["hooli"] == Result(score=10, tier="HEALTHY", reasons=[])
    assert results["acme"] == Result(score=6, tier="MEDIUM", reasons=["seats down sharply"])  # D02
    assert results["globex"] == Result(score=6, tier="MEDIUM", reasons=["seats down sharply"])  # D01
    assert results["vandelay"] == Result(score=10, tier="HEALTHY", reasons=[])
    assert results["initech"] == Result(score=5, tier="MEDIUM", reasons=["low engagement", "unresolved support load"])  # D03
    assert results["umbrella"] == Result(score=10, tier="HEALTHY", reasons=[])
