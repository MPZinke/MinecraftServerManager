#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2025.12.25                                                                                                      #
#                                                                                                                      #
#   DESCRIPTION:                                                                                                       #
#   BUGS:                                                                                                              #
#   FUTURE:                                                                                                            #
#                                                                                                                      #
########################################################################################################################


import traceback


import uvicorn


from logger import logger
from updater import update_world_statuses, start_updater
from webapp import app


def main():
	try:
		update_world_statuses()

	except Exception:
		logger.error(traceback.format_exc())

	event, thread = start_updater()

	uvicorn.run(app, host="0.0.0.0", port=80)

	logger.info("Shutting down updater.")
	event.set()
	thread.join()


if(__name__ == "__main__"):
	main()
