# pragma: exclude file
import inspect
import logging.config
import pathlib

import yaml


class CallerFilter(logging.Filter):
    """Format the caller's stack frame for logging."""

    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        """Determine if the specified record is to be logged.

        Returns True if the record should be logged, or False otherwise. If
        deemed appropriate, the record may be modified in-place.
        """
        frame = None
        filename = pathlib.Path()
        # Find the caller's stack frame
        for frame in [*inspect.stack(), None]:
            if pathlib.Path(record.pathname).samefile(filename):
                break
            if frame:
                filename = pathlib.Path(frame.filename)

        # Format caller frame
        if frame is None:
            record.caller = ""
        else:
            file = pathlib.Path(frame.filename)
            record.caller = f"{file.name}:{frame.lineno}"

        return True


def setup_logging() -> None:
    """Load config file config/logging.yaml."""
    project_root = pathlib.Path(__file__).resolve().parent.parent.parent.parent

    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    config_path = project_root / "config" / "logging.yaml"
    with pathlib.Path.open(config_path) as f:
        config = yaml.safe_load(f)
        logging.config.dictConfig(config)
