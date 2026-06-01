Feature: Injection / JNDI payload guard (CVE-2021-44228 Log4Shell)
  A crafted JNDI / deserialization payload must never be evaluated, reflected
  back, or crash the Java banking service.

  Scenario: A JNDI lookup payload is neither reflected nor fatal
    Given the banking service is reachable
    When I submit a limit change carrying an injection payload
    Then the request succeeds
    And the service does not return a server error
    And the payload is not reflected in the response
