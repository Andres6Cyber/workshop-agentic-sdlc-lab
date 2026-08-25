"""Contract tests for scoring account health.

Verifies scoring rules, tier classifications, and reason strings
using longhand MonthSnapshot lists without reading CSV files.
"""

from __future__ import annotations

from usage import MonthSnapshot, Result, score


def test_score_healthy_account_no_deductions():
    snapshots = [
        MonthSnapshot(account_id="hooli", month="2026-01", seats_active=12, logins=40, tickets_open=0),
        MonthSnapshot(account_id="hooli", month="2026-02", seats_active=12, logins=45, tickets_open=1),
    ]
    assert score(snapshots) == Result(score=10, tier="HEALTHY", reasons=[])


def test_score_seats_drop_to_zero():
    snapshots = [
        MonthSnapshot(account_id="acme", month="2026-01", seats_active=10, logins=5, tickets_open=0),
        MonthSnapshot(account_id="acme", month="2026-02", seats_active=8, logins=5, tickets_open=0),
        MonthSnapshot(account_id="acme", month="2026-03", seats_active=0, logins=5, tickets_open=0),
    ]
    assert score(snapshots) == Result(score=6, tier="MEDIUM", reasons=["seats down sharply"])  # D02


def test_score_seats_drop_compares_to_immediately_preceding_month():
    snapshots = [
        MonthSnapshot(account_id="globex", month="2026-01", seats_active=4, logins=5, tickets_open=0),
        MonthSnapshot(account_id="globex", month="2026-02", seats_active=10, logins=5, tickets_open=0),
        MonthSnapshot(account_id="globex", month="2026-03", seats_active=6, logins=5, tickets_open=0),
    ]
    assert score(snapshots) == Result(score=6, tier="MEDIUM", reasons=["seats down sharply"])  # D01


def test_score_seats_drop_below_forty_percent_threshold():
    snapshots = [
        MonthSnapshot(account_id="vandelay", month="2026-01", seats_active=10, logins=5, tickets_open=0),
        MonthSnapshot(account_id="vandelay", month="2026-02", seats_active=6, logins=5, tickets_open=0),
        MonthSnapshot(account_id="vandelay", month="2026-03", seats_active=5, logins=5, tickets_open=0),
    ]
    assert score(snapshots) == Result(score=10, tier="HEALTHY", reasons=[])


def test_score_low_engagement_and_support_load_medium_tier():
    snapshots = [
        MonthSnapshot(account_id="initech", month="2026-01", seats_active=6, logins=4, tickets_open=0),
        MonthSnapshot(account_id="initech", month="2026-02", seats_active=6, logins=2, tickets_open=3),
    ]
    assert score(snapshots) == Result(score=5, tier="MEDIUM", reasons=["low engagement", "unresolved support load"])  # D03


def test_score_single_month_account_cannot_fire_seat_decline():
    snapshots = [
        MonthSnapshot(account_id="umbrella", month="2026-02", seats_active=3, logins=10, tickets_open=0),
    ]
    assert score(snapshots) == Result(score=10, tier="HEALTHY", reasons=[])
