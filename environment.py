"""behave hooks for the Java platform suite. Minimal — the steps are
self-contained and read the target URL from the environment."""


def before_all(context):
    context.config.setup_logging()
