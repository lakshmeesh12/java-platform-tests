Feature: Management endpoint exposure (Spring Boot actuator)
  Actuator/management endpoints must not be exposed wide open — they leak
  configuration, environment, and operational internals.

  Scenario: Management endpoints are not publicly exposed
    Given the payment-engine middleware inventory is available
    Then management endpoints are not publicly exposed
