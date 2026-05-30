Feature: Funds movement input validation (Java banking service)
  Verify the Java middleware rejects invalid money movements and accepts valid ones.

  Scenario: Negative credit-limit delta is rejected
    Given the platform service is reachable
    When I request a credit limit increase with delta -500
    Then the response is a client error

  Scenario: Valid credit-limit delta is accepted
    Given the platform service is reachable
    When I request a credit limit increase with delta 1000
    Then the response is successful
