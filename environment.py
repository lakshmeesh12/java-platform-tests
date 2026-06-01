"""behave hooks for the Java middleware platform suite. Minimal — each step
reads the live posture endpoint from the environment (AQE_JAVA_MOCK_URL)."""


def before_all(context):
    context.config.setup_logging()
