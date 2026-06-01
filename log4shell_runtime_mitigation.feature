Feature: Log4Shell runtime mitigations (JVM options)
  Even with libraries pending upgrade, the JVM runtime must carry the Log4Shell
  mitigations the platform team is responsible for setting.

  Scenario: The formatMsgNoLookups mitigation is enabled
    Given the payment-engine middleware inventory is available
    Then the Log4Shell JVM mitigation flag is enabled

  Scenario: JNDI remote-codebase loading is disabled
    Given the payment-engine middleware inventory is available
    Then JNDI remote-codebase loading is disabled
