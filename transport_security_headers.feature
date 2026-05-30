Feature: Transport security headers
  The Java service should set baseline transport-security headers.

  Scenario: HSTS header is present
    Given the platform service is reachable
    Then the response includes the security header "Strict-Transport-Security"
