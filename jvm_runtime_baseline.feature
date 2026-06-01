Feature: Payment-engine JVM runtime baseline
  Sanity checks that the platform team's JVM runtime options are present — these
  pass on the patched build (the heap and truststore are configured) and prove
  the suite validates real settings rather than failing everything.

  Scenario: The JVM heap is configured
    Given the payment-engine middleware inventory is available
    Then the JVM heap is configured

  Scenario: A TLS truststore is configured
    Given the payment-engine middleware inventory is available
    Then a TLS truststore is configured
