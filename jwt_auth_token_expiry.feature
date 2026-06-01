Feature: Sensitive data protection (Java banking service)
  Card numbers must be masked everywhere the service returns card data, so a
  leaked response never exposes a full PAN.

  Scenario: Listed cards never expose a full PAN
    Given the banking service is reachable
    When I list the credit cards
    Then at least one credit card is returned
    And every card number is masked

  Scenario: Card detail responses mask the PAN
    Given an existing credit card
    When I fetch the card's full details
    Then the request succeeds
    And the card number is masked in the response
