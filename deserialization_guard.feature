Feature: Injection / JNDI lookup guard (CVE-2021-44228 Log4Shell)
  A crafted JNDI lookup string must never be evaluated or reflected by the Java service.

  Scenario: JNDI lookup payload is neither evaluated nor reflected
    Given the platform service is reachable
    When I submit a JNDI lookup payload in a request field
    Then the payload is not reflected and no server error occurs
