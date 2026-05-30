Feature: JWT authentication handling (CVE-2023-21930)
  The Java service must reject forged or expired bearer tokens on protected endpoints.

  Scenario: Forged bearer token is rejected on a protected endpoint
    Given the platform service is reachable
    When I call a protected endpoint with a forged bearer token
    Then the response is unauthorized
