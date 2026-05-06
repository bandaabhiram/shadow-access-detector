"""
Shadow Risk Score Calculator — 0-100 scale per identity.

Factors:
- Account disabled but tokens valid: +40
- Guest with RBAC, no sign-in 90d: +30
- Service Principal no auth 180d: +25
- Orphaned Managed Identity: +35
"""
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List


def calculate_shadow_score(identity: dict) -> int:
    score = 0
    reasons = []

    # Disabled but active tokens
    if identity.get("accountEnabled") is False:
        refresh_valid = identity.get("refreshTokensValidFromDateTime")
        if refresh_valid:
            token_date = datetime.fromisoformat(refresh_valid.replace("Z", "+00:00"))
            if datetime.now(timezone.utc) - token_date < timedelta(days=90):
                score += 40
                reasons.append("Disabled account with valid refresh token")

    # Guest with stale RBAC
    if identity.get("userType") == "Guest":
        last_signin = identity.get("signInActivity", {}).get("lastSignInDateTime")
        if last_signin:
            signin_date = datetime.fromisoformat(last_signin.replace("Z", "+00:00"))
            if datetime.now(timezone.utc) - signin_date > timedelta(days=90):
                if identity.get("hasRbacAssignments"):
                    score += 30
                    reasons.append("Guest with RBAC, no sign-in 90+ days")

    # Service Principal stale auth
    if identity.get("type") == "servicePrincipal":
        last_auth = identity.get("signInActivity", {}).get("lastSignInDateTime")
        if last_auth:
            auth_date = datetime.fromisoformat(last_auth.replace("Z", "+00:00"))
            if datetime.now(timezone.utc) - auth_date > timedelta(days=180):
                score += 25
                reasons.append("Service Principal no authentication 180+ days")

    # Orphaned Managed Identity
    if identity.get("type") == "managedIdentity":
        if identity.get("attachedResourceDeleted") is True:
            score += 35
            reasons.append("Managed Identity attached to deleted resource")

    return min(score, 100), reasons


def process_batch(identities: List[dict]) -> List[dict]:
    results = []
    for identity in identities:
        score, reasons = calculate_shadow_score(identity)
        identity["shadowRiskScore"] = score
        identity["shadowRiskReasons"] = reasons
        results.append(identity)
    return sorted(results, key=lambda x: x["shadowRiskScore"], reverse=True)


if __name__ == "__main__":
    # Example test
    test_identities = [
        {"accountEnabled": False, "refreshTokensValidFromDateTime": "2024-04-01T00:00:00Z"},
        {"userType": "Guest", "signInActivity": {"lastSignInDateTime": "2024-01-01T00:00:00Z"}, "hasRbacAssignments": True},
    ]
    scored = process_batch(test_identities)
    print(json.dumps(scored, indent=2))
