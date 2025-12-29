#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2025.12.29                                                                                                      #
#                                                                                                                      #
#   DESCRIPTION:                                                                                                       #
#   BUGS:                                                                                                              #
#   FUTURE:                                                                                                            #
#                                                                                                                      #
########################################################################################################################


from typing import Tuple


import pexpect


from docker import Container


def get_player_location(container: Container, player: str) -> Tuple[int, int, int]:
	"""
	Not
	"""
	# FROM: https://docs.docker.com/reference/cli/docker/container/attach/
	analyzer = pexpect.spawn(f"docker attach {container.name}", encoding='utf-8', timeout=5)
	analyzer.sendline(f"data get entity {player} Pos")  # FROM: https://minecraft.wiki/w/Commands/data

	log_format_info_regex = r"\[[0-9]{2}:[0-9]{2}:[0-9]{2}\] \[Server thread/INFO\]"
	# EG. [15:18:56] [Server thread/INFO]: No entity was found
	entity_not_found_regex = rf"{log_format_info_regex}: No entity was found"
	# EG. [15:11:07] [Server thread/INFO]: MPZinke has the following entity data: [257.30000001192093d, 93.0d, -290.06413177702524d]
	coodinates_regex = r"\[(?P<X>-?\d+)\.\d+d, (?P<Y>-?\d+)\.\d+d, (?P<Z>-?\d+)\.\d+d\]"
	entity_location_regex = rf"{log_format_info_regex}: {player} has the following entity data: {coodinates_regex}"

	match_regexs: list[str] = [entity_not_found_regex, entity_location_regex,]
	# Not async to ensure no other commands are being run at the same time to confuse it.
	match(match_regexs[analyzer.expect(match_regexs)]):
		case(entity_not_found_regex):
			raise Exception("No entity was found")

		case(entity_location_regex):
			match_dict: dict = analyzer.match.groupdict()
			return [int(match_dict["X"]), int(match_dict["Y"]), int(match_dict["Z"])]


async def op_player(player: str):
	...


async def teleport_player(player: str, x: str="~", y: str="~", z: str="~"):
	...
