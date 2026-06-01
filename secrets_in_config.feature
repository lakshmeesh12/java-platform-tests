Feature: No secrets in payment-engine configuration
  Datasource credentials must come from a vault / environment, never inlined in
  the application configuration the platform team ships.

  Scenario: The datasource password is not hardcoded
    Given the payment-engine middleware inventory is available
    Then no hardcoded datasource credentials are configured
