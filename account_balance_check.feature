Feature: Credit card portfolio retrieval (Java banking service)
  The service returns the cardholder's portfolio with balances and masked
  card numbers.

  Scenario: The portfolio lists at least one card
    Given the banking service is reachable
    When I list the credit cards
    Then at least one credit card is returned
    And every card number is masked

  Scenario: Card details include balance fields
    Given an existing credit card
    When I fetch the card's full details
    Then the request succeeds
    And the balance fields are present
