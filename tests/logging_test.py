"""Verify Energia respects application logging configuration."""

import subprocess
import sys
from textwrap import dedent


def test_model_import_and_reload_preserve_logging():
    script = dedent(
        """
        import logging
        from importlib import reload

        logger = logging.getLogger("energia")
        handler = logging.NullHandler()
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)

        def check_logging():
            assert logger.level == logging.WARNING, logger.level
            assert logger.handlers == [handler], logger.handlers

        from energia.represent import model

        check_logging()
        reload(model)
        check_logging()
        """
    )
    subprocess.run([sys.executable, "-c", script], check=True)
