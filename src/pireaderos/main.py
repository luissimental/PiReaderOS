# pragma: exclude file
import logging

from pireaderos.core.logging import setup_logging
from pireaderos.core.manager import AppManager


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Started PiReaderOS")

    # Run PiReaderOS
    manager = AppManager()
    manager.run()


if __name__ == "__main__":
    main()
