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


import re
from typing import Optional, Tuple


from database.classes import Player
from docker.api import Attach
from logger import logger


LOG_FORMAT_INFO_REGEX = r"\[[0-9]{2}:[0-9]{2}:[0-9]{2}\] \[Server thread/INFO\]"


async def get_player_location(container_id: str, player: str) -> Tuple[str, Tuple[int, int, int]]:
	# EG. `[17:19:38] [Server thread/INFO]: No entity was found`
	no_entity_regex = r"(?P<no_entity>No entity was found)"
	# EG. `[21:18:23] [Server thread/INFO]: MPZinke has the following entity data: "minecraft:overworld"`
	dimension_regex = rf"{player} has the following entity data: \"minecraft:(?P<dimension>[_\w]+)\""
	entity_dimension_regex = rf"{LOG_FORMAT_INFO_REGEX}: {dimension_regex}"

	# EG. `[15:11:07] [Server thread/INFO]: MPZinke has the following entity data: [257.30000001192093d, 93.0d, -290.06413177702524d]`
	coordinate_regex = r"\[(?P<X>-?\d+)\.\d+d, (?P<Y>-?\d+)\.\d+d, (?P<Z>-?\d+)\.\d+d\]"
	location_regex = rf"{player} has the following entity data: {coordinate_regex}"
	entity_location_regex = rf"{LOG_FORMAT_INFO_REGEX}: ({location_regex}|{no_entity_regex})"
	async with Attach(container_id) as connection:
		await connection.send(f"data get entity {player} Dimension")  # FROM: https://minecraft.wiki/w/Commands/data
		dimension_match: Optional[re.Match] = await connection.match(entity_dimension_regex, timeout=5.0)
		if(dimension_match is None):
			logger.error(f"The dimension command did not return any viable results for {player}.")
			return None, None

		await connection.send(f"data get entity {player} Pos")  # FROM: https://minecraft.wiki/w/Commands/data
		location_match: Optional[re.Match] = await connection.match(entity_location_regex, timeout=5.0)
		if(location_match is None):
			logger.error(f"The location command did not return any viable results for {player}.")
			return None, None

	dimension_match_dict = dimension_match.groupdict()
	dimension = dimension_match_dict["dimension"]
	location_match_dict: dict = location_match.groupdict()
	location = [int(location_match_dict["X"]), int(location_match_dict["Y"]), int(location_match_dict["Z"])]

	return dimension, location


async def get_online_players(container_id: str) -> Optional[list[Player]]:
	# EG. `[02:01:10] [Server thread/INFO]: There are 0 of a max of 20 players online: `
	# OR  `[02:00:18] [Server thread/INFO]: There are 1 of a max of 20 players online: MPZinke (67c84847-04c1-4b52-945f-ec377ee607a4)`
	player_info_regex = r"(?:(\w+) \(([\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12})\))"
	players_info_list_regex = rf"(?P<online_players>(?:{player_info_regex}(?:, {player_info_regex})*)?)"
	regex = rf"{LOG_FORMAT_INFO_REGEX}: There are \d+ of a max of \d+ players online: {players_info_list_regex}"
	async with Attach(container_id) as connection:
		await connection.send("list uuids")  # FROM: https://minecraft.fandom.com/wiki/Commands/list
		match: Optional[re.Match] = await connection.match(regex, timeout=5.0)

	if(match is None):
		return None

	return [Player(0, name, uuid) for name, uuid in re.findall(player_info_regex, match.groupdict()["online_players"])]


async def get_seed(container_id: str) -> Optional[int]:
	# Wait for server to fully start.
	# EG. `[18:53:08] [Server thread/INFO]: Done (0.250s)! For help, type "help"`
	server_start_regex = rf"{LOG_FORMAT_INFO_REGEX}: Done \(\d+\.\d+s\)! For help, type \"help\""
	# EG. `[04:26:45] [Server thread/INFO]: Seed: [2817679626123392159]`
	seed_regex = rf"{LOG_FORMAT_INFO_REGEX}: Seed: \[(?P<seed>-?\d+)\]"

	async with Attach(container_id) as connection:
		await connection.match(server_start_regex, timeout=30.0)
		await connection.send("seed")  # FROM: https://minecraft.fandom.com/wiki/Commands/seed
		seed_match: Optional[str] = await connection.match(seed_regex, timeout=5.0)

	if(seed_match is None):
		return None

	return seed_match.groupdict()["seed"]


async def op_player(container_id: str, player: str) -> None:
	# EG. `[22:38:32] [Server thread/INFO]: Made MPZinke a server operator`
	# OR  `[02:38:56] [Server thread/INFO]: Nothing changed. The player already is an operator`
	log_regex = rf"(Made {player} a server operator|Nothing changed\. The player already is an operator)"
	regex = rf"{LOG_FORMAT_INFO_REGEX}: {log_regex}"
	async with Attach(container_id) as connection:
		await connection.send(f"op {player}")  # FROM: https://minecraft.fandom.com/wiki/Commands/op
		result = await connection.match(regex, timeout=5.0)

	if(result is not None):
		logger.info(f"Successfully made {player} an OP.")
	else:
		logger.error(f"Failed to make {player} an OP.")


async def stop_server(container_id: str) -> bool:
	# EG. `[17:40:06] [Server thread/INFO]: ThreadedAnvilChunkStorage: All dimensions are saved`
	regex = rf"{LOG_FORMAT_INFO_REGEX}: ThreadedAnvilChunkStorage: All dimensions are saved"
	async with Attach(container_id) as connection:
		await connection.send("stop")  # FROM: https://minecraft.fandom.com/wiki/Commands/stop
		return (await connection.match(regex, timeout=30.0)) is not None


async def teleport_player(container_id: str, player: str, location: Tuple[int, int, int], dimension: str) -> None:
	# EG. `[22:56:10] [Server thread/INFO]: Teleported MPZinke to 2.500000, 88.000000, 11.500000`
	regex = rf"{LOG_FORMAT_INFO_REGEX}: Teleported MPZinke to .*"
	async with Attach(container_id) as connection:
		# FROM: https://minecraft.fandom.com/wiki/Commands/tp
		await connection.send(f"execute in {dimension} run tp {player} {" ".join(map(str, location))}")
		await connection.match(regex, timeout=5.0)
