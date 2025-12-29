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


from update import update_world_statuses, run_update
from webapp import app


def main():
	try:
		update_world_statuses()

	except Exception:
		print(traceback.format_exc())

	event, thread = run_update()

	uvicorn.run(app, host="0.0.0.0", port=80)

	print("Setting thread")
	event.set()
	print("Joining thread")
	thread.join()
	print("Bye bye")


if(__name__ == "__main__"):
	main()
