"""Contract tests for parsing usage exports.

Verifies that parse_usage correctly converts CSV export text into
MonthSnapshot dataclasses grouped by account and sorted chronologically.
"""

from __future__ import annotations

from main import load_export
from usage import MonthSnapshot, parse_usage


def test_parse_usage_fixture():
    export_text = load_export()
    result = parse_usage(export_text)

    assert result == {
        "hooli": [
            MonthSnapshot(account_id="hooli", month="2026-01", seats_active=12, logins=40, tickets_open=0),
            MonthSnapshot(account_id="hooli", month="2026-02", seats_active=12, logins=45, tickets_open=1),
        ],
        "acme": [
            MonthSnapshot(account_id="acme", month="2026-01", seats_active=10, logins=5, tickets_open=0),
            MonthSnapshot(account_id="acme", month="2026-02", seats_active=8, logins=5, tickets_open=0),
            MonthSnapshot(account_id="acme", month="2026-03", seats_active=0, logins=5, tickets_open=0),  # D02
        ],
        "globex": [
            MonthSnapshot(account_id="globex", month="2026-01", seats_active=4, logins=5, tickets_open=0),
            MonthSnapshot(account_id="globex", month="2026-02", seats_active=10, logins=5, tickets_open=0),
            MonthSnapshot(account_id="globex", month="2026-03", seats_active=6, logins=5, tickets_open=0),
        ],
        "vandelay": [
            MonthSnapshot(account_id="vandelay", month="2026-01", seats_active=10, logins=5, tickets_open=0),
            MonthSnapshot(account_id="vandelay", month="2026-02", seats_active=6, logins=5, tickets_open=0),
            MonthSnapshot(account_id="vandelay", month="2026-03", seats_active=5, logins=5, tickets_open=0),
        ],
        "initech": [
            MonthSnapshot(account_id="initech", month="2026-01", seats_active=6, logins=4, tickets_open=0),
            MonthSnapshot(account_id="initech", month="2026-02", seats_active=6, logins=2, tickets_open=3),
        ],
        "umbrella": [
            MonthSnapshot(account_id="umbrella", month="2026-02", seats_active=3, logins=10, tickets_open=0),
        ],
    }


def test_parse_usage_blank_seats_parsed_as_zero():
    csv_text = (
        "account_id,month,seats_active,logins,tickets_open\n"
        "acme,2026-03,,5,0\n"
    )
    result = parse_usage(csv_text)
    assert result == {
        "acme": [
            MonthSnapshot(account_id="acme", month="2026-03", seats_active=0, logins=5, tickets_open=0)  # D02
        ]
    }


def test_parse_usage_sorts_months_in_ascending_order():
    csv_text = (
        "account_id,month,seats_active,logins,tickets_open\n"
        "globex,2026-03,6,5,0\n"
        "globex,2026-01,4,5,0\n"
        "globex,2026-02,10,5,0\n"
    )
    result = parse_usage(csv_text)
    assert result == {
        "globex": [
            MonthSnapshot(account_id="globex", month="2026-01", seats_active=4, logins=5, tickets_open=0),
            MonthSnapshot(account_id="globex", month="2026-02", seats_active=10, logins=5, tickets_open=0),
            MonthSnapshot(account_id="globex", month="2026-03", seats_active=6, logins=5, tickets_open=0),
        ]
    }


def test_parse_usage_empty_export_returns_empty_dict():
    csv_text = "account_id,month,seats_active,logins,tickets_open\n"
    result = parse_usage(csv_text)
    assert result == {}
