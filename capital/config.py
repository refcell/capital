"""Settings that differ per operator. Read from the environment, never hard-coded."""

from __future__ import annotations

import os
import sys

# SEC EDGAR rejects requests (HTTP 403) whose User-Agent lacks a contact email.
# TODO(andreas): set CAPITAL_SEC_CONTACT to a personal or project address.
SEC_CONTACT_PLACEHOLDER = "REPLACE-ME@set-CAPITAL_SEC_CONTACT.invalid"


def sec_user_agent() -> str:
    contact = os.environ.get("CAPITAL_SEC_CONTACT", "").strip()
    if not contact:
        print(
            "warning: CAPITAL_SEC_CONTACT is not set; using the placeholder SEC contact",
            file=sys.stderr,
        )
        contact = SEC_CONTACT_PLACEHOLDER
    return f"refcell-capital research {contact}"


# Rating rule. Default proposed by the track-records research and adopted while
# Andreas is away; change the numbers here and every page regenerates.
# A rating is derived from the call's fair value (probability-weighted when the
# report gives weights) versus its reference price, annualized over HORIZON_YEARS.
# The benchmark is total return on BENCHMARK over the same horizon.
RATING_HORIZON_YEARS = 3
RATING_BENCHMARK = "SPY"
RATING_OWN_MIN_ANNUAL = 0.15  # Own: expected return >= 15% a year
RATING_AVOID_MAX_ANNUAL = 0.00  # Avoid: expected return < 0% a year; Watch in between

RATING_DEFINITIONS = {
    "own": f"Expected annualized return of at least {RATING_OWN_MIN_ANNUAL:.0%} over {RATING_HORIZON_YEARS} years; maps to Buy.",
    "watch": f"Expected annualized return from {RATING_AVOID_MAX_ANNUAL:.0%} to {RATING_OWN_MIN_ANNUAL:.0%} over {RATING_HORIZON_YEARS} years; maps to Hold.",
    "avoid": f"Expected annualized return below {RATING_AVOID_MAX_ANNUAL:.0%} over {RATING_HORIZON_YEARS} years; maps to Sell.",
}

# Price-check tolerance: a call's stated price versus the committed close on its date.
PRICE_CHECK_TOLERANCE = 0.05
