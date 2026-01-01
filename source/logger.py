

import logging


# FROM: https://stackoverflow.com/a/57820456
_log_record_factory = logging.getLogRecordFactory()
def _custom_factory(*args, **kwargs):
	record = _log_record_factory(*args, **kwargs)
	record.location = f"{record.module}.{record.funcName}:{record.lineno}"
	return record


logging.basicConfig(
	datefmt="%Y-%m-%d %H:%M:%S",
	format="| %(asctime)s | %(levelname)-8s | %(location)-35s | %(message)s",
	level=logging.INFO,
)
logging.setLogRecordFactory(_custom_factory)
logger = logging.getLogger()
