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
