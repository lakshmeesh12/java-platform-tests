Feature: Error handling on the Java banking service
  Requests for resources that do not exist must return a clean not-found
  error rather than leaking internals or a server error.

  Scenario: An unknown card id returns not found
    Given the banking service is reachable
    When I fetch details for a non-existent card
    Then the service returns a not-found error
