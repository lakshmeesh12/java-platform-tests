Feature: Payment-engine dependency CVE scan (shared library BOM)
  The platform team owns the shared library versions in the payment-engine.
  None of them may carry a known-exploited (KEV) vulnerability.

  Scenario: log4j-core is free of Log4Shell
    Given the payment-engine middleware inventory is available
    Then no Log4Shell-vulnerable log4j-core is present

  Scenario: spring-webmvc is free of Spring4Shell
    Given the payment-engine middleware inventory is available
    Then no Spring4Shell-vulnerable spring-webmvc is present

  Scenario: commons-collections has no deserialization gadget chain
    Given the payment-engine middleware inventory is available
    Then no insecure commons-collections gadget chain is present
