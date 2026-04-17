# pragma: exclude file
import logging

from pireaderos.core import logging as core_logging
from pireaderos.core import manager


def main() -> None:
    """Entry point of PiReaderOS."""
    core_logging.setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Started PiReaderOS")

    # Run PiReaderOS
    app_manager = manager.AppManager()
    app_manager.run()


if __name__ == "__main__":
    main()
