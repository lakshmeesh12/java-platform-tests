Feature: Payment-engine TLS hardening (connector config)
  The middleware connector must terminate TLS and refuse legacy protocols.

  Scenario: HTTPS is enabled on the connector
    Given the payment-engine middleware inventory is available
    Then HTTPS is enabled on the connector

  Scenario: Only TLS 1.2 or higher is negotiated
    Given the payment-engine middleware inventory is available
    Then TLS is restricted to version 1.2 or higher
