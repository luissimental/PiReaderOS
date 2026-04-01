import inspect
import logging.config
import yaml
from pathlib import Path


class CallerFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        frame = None
        filename = Path()
        # Find the caller's stack frame
        for frame in inspect.stack() + [None]:
            if Path(record.pathname).samefile(filename):
                break
            if frame:
                filename = Path(frame.filename)

        # Format caller frame
        if frame is None:
            record.caller = ""
        else:
            file = Path(frame.filename)
            record.caller = f"{file.name}:{frame.lineno}"

        return True


def setup_logging():
    "Load config file config/logging.yaml"
    project_root = Path(__file__).resolve().parent.parent.parent.parent

    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    config_path = project_root / "config" / "logging.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
        logging.config.dictConfig(config)
