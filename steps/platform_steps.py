"""Step definitions for the Java MIDDLEWARE platform suite (payment-engine).

These validate what the platform / middleware team actually owns — shared
library versions, JVM runtime flags, and app-server (Spring Boot) configuration
— against the live middleware posture endpoint at AQE_JAVA_MOCK_URL
(the platform posture service; defaults to http://127.0.0.1:8009). The endpoint
reflects the real pushed config files, so the suite is clean on the hardened
baseline and flags the regressions a patch introduces. Nothing is hardcoded.
"""
import os

import requests
from behave import given, then

BASE = os.environ.get("AQE_JAVA_MOCK_URL", "http://127.0.0.1:8009").rstrip("/")
TIMEOUT = float(os.environ.get("JAVA_HTTP_TIMEOUT", "15"))


def _posture(context):
    if getattr(context, "data", None) is None:
        r = requests.get(f"{BASE}/java/dependencies", timeout=TIMEOUT)
        assert r.status_code == 200, f"middleware inventory not available at {BASE} (status {r.status_code})"
        context.data = r.json()
        context.vulnerable = [str(v).lower() for v in context.data.get("vulnerable", [])]
        context.mw = context.data.get("middleware", {})
    return context.data


def _no_vuln(context, *needles):
    hits = [v for v in context.vulnerable if any(n in v for n in needles)]
    assert not hits, "vulnerable component(s) detected: " + "; ".join(hits)


@given("the payment-engine middleware inventory is available")
def step_inventory(context):
    _posture(context)


# ── Shared dependency BOM ─────────────────────────────────────────────────────
@then("no Log4Shell-vulnerable log4j-core is present")
def step_log4j(context):
    _posture(context); _no_vuln(context, "log4j")


@then("no Spring4Shell-vulnerable spring-webmvc is present")
def step_spring(context):
    _posture(context); _no_vuln(context, "spring")


@then("no insecure commons-collections gadget chain is present")
def step_commons(context):
    _posture(context); _no_vuln(context, "commons-collections")


# ── JVM runtime hardening ─────────────────────────────────────────────────────
@then("the Log4Shell JVM mitigation flag is enabled")
def step_mitigation(context):
    _posture(context)
    assert context.mw.get("log4shell_mitigation") is True, "formatMsgNoLookups mitigation is not set in jvm.options"


@then("JNDI remote-codebase loading is disabled")
def step_jndi(context):
    _posture(context)
    assert context.mw.get("jndi_trust_url_codebase") is False, "trustURLCodebase is enabled — Log4Shell remote class load is open"


@then("the JVM heap is configured")
def step_heap(context):
    _posture(context)
    assert context.mw.get("heap_configured") is True, "no -Xmx heap setting found in jvm.options"


@then("a TLS truststore is configured")
def step_truststore(context):
    _posture(context)
    assert context.mw.get("truststore_configured") is True, "no truststore configured in jvm.options"


# ── App-server / TLS config ───────────────────────────────────────────────────
@then("TLS is restricted to version 1.2 or higher")
def step_tls(context):
    _posture(context)
    assert context.mw.get("tls_hardened") is True, "weak TLS protocols (TLSv1 / TLSv1.1) are enabled on the connector"


@then("HTTPS is enabled on the connector")
def step_https(context):
    _posture(context)
    assert context.mw.get("https_enabled") is True, "server.ssl.enabled is not true"


@then("no hardcoded datasource credentials are configured")
def step_secrets(context):
    _posture(context)
    assert context.mw.get("hardcoded_datasource_password") is False, "a hardcoded datasource password is present in application.properties"


@then("management endpoints are not publicly exposed")
def step_actuator(context):
    _posture(context)
    assert context.mw.get("actuator_exposed") is False, "actuator/management endpoints are exposed (exposure.include=*)"
