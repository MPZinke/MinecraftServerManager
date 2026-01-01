

import logging
import sys


class ContextFilter(logging.Filter):
	def filter(self, record):
		record.location = f"{record.module}.{record.funcName}:{record.lineno}"

		frame = sys._getframe(6)
		function_execution = [frame.f_code.co_name]
		while frame:
			function_execution.insert(0, frame.f_code.co_name)
			frame = frame.f_back

		if(function_execution[:3] == ["_run_module_as_main", "_run_code", "<module>"]):
			record.execution = "->".join(function_execution[3:])

		if(function_execution[:1] == ["<module>"]):
			record.execution = "->".join(function_execution[1:])

		return True


logging.basicConfig(
	datefmt="%Y-%m-%d %H:%M:%S",
	format="| %(asctime)s | %(levelname)-8s | %(location)-35s | %(message)s",
	level=logging.INFO,
)
logger = logging.getLogger()
logger.addFilter(ContextFilter())
