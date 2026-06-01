Feature: Transport observability headers (Java banking service)
  Every response carries a request-trace header so calls can be traced
  end-to-end for audit and incident response.

  Scenario: The health response carries a request trace header
    Given the banking service is reachable
    When I read the health endpoint
    Then the response carries a request trace header
