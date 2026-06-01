# java-platform-tests

Platform / middleware validation for the shared **payment-engine** (Spring Boot).
Cucumber/`.feature` suites run with `behave` against the middleware posture
service. They validate what the **platform team** owns — the shared dependency
BOM, JVM runtime flags, TLS config, secrets handling, and actuator exposure —
not application business logic.

Imported and run by UTP; edit & push back from the platform UI.
