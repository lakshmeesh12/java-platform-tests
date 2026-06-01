Feature: Credit limit movement validation (Java banking service)
  The banking middleware applies credit-limit changes correctly and keeps the
  arithmetic consistent on every movement.

  Scenario: The banking service is healthy
    Given the banking service is reachable
    Then the service reports it is healthy

  Scenario: A cardholder increases their credit limit
    Given an active credit card
    When I increase the credit limit by 1000
    Then the request succeeds
    And the new credit limit reflects the change

  Scenario: A cardholder decreases their credit limit
    Given an active credit card
    When I decrease the credit limit by 500
    Then the request succeeds
    And the new credit limit reflects the change
