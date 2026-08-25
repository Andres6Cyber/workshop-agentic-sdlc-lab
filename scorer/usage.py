from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MonthSnapshot:
    account_id: str
    month: str  # "YYYY-MM"
    seats_active: int
    logins: int
    tickets_open: int


@dataclass(frozen=True)
class Result:
    score: int
    tier: str  # "HEALTHY" | "MEDIUM" | "AT RISK"
    reasons: list[str]


def parse_usage(csv_text: str) -> dict[str, list[MonthSnapshot]]:
    """Group the export text by account, each list in ascending month order.

    An account with no months to score is omitted, so score() is never
    called with an empty list.
    """
    import csv
    import io

    reader = csv.DictReader(io.StringIO(csv_text))
    accounts: dict[str, list[MonthSnapshot]] = {}

    for row in reader:
        account_id = row["account_id"].strip()
        month = row["month"].strip()
        seats_str = row.get("seats_active", "").strip() if row.get("seats_active") is not None else ""
        seats_active = int(seats_str) if seats_str else 0
        logins = int(row["logins"].strip())
        tickets_open = int(row["tickets_open"].strip())

        snapshot = MonthSnapshot(
            account_id=account_id,
            month=month,
            seats_active=seats_active,
            logins=logins,
            tickets_open=tickets_open,
        )

        if account_id not in accounts:
            accounts[account_id] = []
        accounts[account_id].append(snapshot)

    for account_id in accounts:
        accounts[account_id].sort(key=lambda s: s.month)

    return accounts


def score(months: list[MonthSnapshot]) -> Result:
    """Score one account's months. Never reads the CSV."""
    if not months:
        raise ValueError("score() called with empty months list")

    latest = months[-1]
    reasons: list[str] = []
    points = 10

    # Rule 1: The latest month's seat count has fallen by 40% or more
    if len(months) >= 2:
        prev = months[-2]
        if prev.seats_active > 0 and (prev.seats_active - latest.seats_active) * 100 >= 40 * prev.seats_active:
            points -= 4
            reasons.append("seats down sharply")

    # Rule 2: Fewer than 3 logins in the latest month
    if latest.logins < 3:
        points -= 3
        reasons.append("low engagement")

    # Rule 3: 2 or more tickets open in the latest month
    if latest.tickets_open >= 2:
        points -= 2
        reasons.append("unresolved support load")

    final_score = max(0, points)

    if final_score >= 8:
        tier = "HEALTHY"
    elif final_score >= 5:
        tier = "MEDIUM"
    else:
        tier = "AT RISK"

    return Result(score=final_score, tier=tier, reasons=reasons)
