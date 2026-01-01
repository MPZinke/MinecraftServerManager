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


from typing import Optional, Tuple


import pexpect


LOG_FORMAT_INFO_REGEX = r"\[[0-9]{2}:[0-9]{2}:[0-9]{2}\] \[Server thread/INFO\]"


async def get_player_location(container_id: str, player: str) -> Tuple[int, int, int]:
	# FROM: https://docs.docker.com/reference/cli/docker/container/attach/
	analyzer = pexpect.spawn(f"docker attach {container_id}", encoding='utf-8', timeout=5)
	analyzer.sendline(f"data get entity {player} Pos")  # FROM: https://minecraft.wiki/w/Commands/data

	# EG. `[15:11:07] [Server thread/INFO]: MPZinke has the following entity data: [257.30000001192093d, 93.0d, -290.06413177702524d]`
	coodinates_regex = r"\[(?P<X>-?\d+)\.\d+d, (?P<Y>-?\d+)\.\d+d, (?P<Z>-?\d+)\.\d+d\]"
	entity_location_regex = rf"{LOG_FORMAT_INFO_REGEX}: {player} has the following entity data: {coodinates_regex}"

	await analyzer.expect(entity_location_regex, async_=True)
	match_dict: dict = analyzer.match.groupdict()
	return [int(match_dict["X"]), int(match_dict["Y"]), int(match_dict["Z"])]


async def get_seed(container_id: str) -> Optional[int]:
	# FROM: https://docs.docker.com/reference/cli/docker/container/attach/
	analyzer = pexpect.spawn(f"docker attach {container_id}", encoding='utf-8', timeout=30)

	# Wait for server to fully start.
	# EG. `[18:53:08] [Server thread/INFO]: Done (0.250s)! For help, type "help"`
	server_start_regex = rf"{LOG_FORMAT_INFO_REGEX}: Done \(\d+\.\d+s\)! For help, type \"help\""
	await analyzer.expect([server_start_regex, pexpect.TIMEOUT], async_=True)

	analyzer.sendline("seed")  # FROM: https://minecraft.fandom.com/wiki/Commands/seed
	# EG. `[04:26:45] [Server thread/INFO]: Seed: [2817679626123392159]`
	seed_regex = rf"{LOG_FORMAT_INFO_REGEX}: Seed: \[(?P<seed>-?\d+)\]"
	expect_regexes = [seed_regex, pexpect.TIMEOUT]
	index: int = await analyzer.expect(expect_regexes, async_=True)

	match(expect_regexes[index]):
		case(str() as seed_regex):
			return analyzer.match.groupdict()["seed"]

		case(pexpect.TIMEOUT):
			return None


async def op_player(container_id: str, player: str) -> None:
	# FROM: https://docs.docker.com/reference/cli/docker/container/attach/
	analyzer = pexpect.spawn(f"docker attach {container_id}", encoding='utf-8', timeout=5)
	analyzer.sendline(f"op {player}")  # FROM: https://minecraft.fandom.com/wiki/Commands/op

	# EG. `[22:38:32] [Server thread/INFO]: Made MPZinke a server operator`
	op_regex = rf"{LOG_FORMAT_INFO_REGEX}: Made {player} a server operator"

	await analyzer.expect(op_regex, async_=True)


async def stop_server(container_id: str) -> bool:
	# FROM: https://docs.docker.com/reference/cli/docker/container/attach/
	analyzer = pexpect.spawn(f"docker attach {container_id}", encoding='utf-8', timeout=30)
	analyzer.sendline("stop")  # FROM: https://minecraft.fandom.com/wiki/Commands/stop

	# EG. `[17:40:06] [Server thread/INFO]: ThreadedAnvilChunkStorage: All dimensions are saved`
	stop_regex = rf"{LOG_FORMAT_INFO_REGEX}: ThreadedAnvilChunkStorage: All dimensions are saved"
	expect_regexes = [stop_regex, pexpect.TIMEOUT]

	index: int = await analyzer.expect(expect_regexes, async_=True)
	return expect_regexes[index] == stop_regex


async def teleport_player(container_id: str, player: str, location: Tuple[int, int, int]) -> None:
	# FROM: https://docs.docker.com/reference/cli/docker/container/attach/
	analyzer = pexpect.spawn(f"docker attach {container_id}", encoding='utf-8', timeout=5)
	# FROM: https://minecraft.fandom.com/wiki/Commands/tp
	analyzer.sendline(f"tp {player} {location[0]} {location[1]} {location[2]}")

	# EG. `[22:56:10] [Server thread/INFO]: Teleported MPZinke to 2.500000, 88.000000, 11.500000`
	tp_regex = rf"{LOG_FORMAT_INFO_REGEX}: Teleported MPZinke to .*"

	await analyzer.expect(tp_regex, async_=True)
