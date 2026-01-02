#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2025.12.26                                                                                                      #
#                                                                                                                      #
#   DESCRIPTION:                                                                                                       #
#   BUGS:                                                                                                              #
#   FUTURE:                                                                                                            #
#                                                                                                                      #
########################################################################################################################


import asyncio
import os
import re
import socket


from database.classes import World
from docker.image import Image
from logger import logger


async def get_available_port() -> None:
	if(os.getenv("DOCKER") != "true"):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			if(s.connect_ex(('', 25565)) != 0):
				return 25565

		# FROM: https://stackoverflow.com/a/1365284
		sock = socket.socket()
		sock.bind(("localhost", 0))
		return sock.getsockname()[1]

	port_window_size = 10
	for starting_port in range(25565, 65536, port_window_size):
		process = await asyncio.create_subprocess_exec(
			"nc",
			"-zv",
			"host.docker.internal",
			f"{starting_port}–{starting_port+port_window_size}",
			stderr=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
		)
		_, stderr = map(lambda io: io.decode().strip(), await process.communicate())

		# EG. `host.docker.internal [192.168.65.254] 25565 (?) open`
		port_match_regex = r"host\.docker\.internal \[\d+\.\d+\.\d+\.\d+\] (\d+) \(\?\) open"
		occupied_ports: list[int] = list(map(int, re.findall(port_match_regex, stderr)))
		for port in range(starting_port, starting_port+port_window_size):
			if(port not in occupied_ports):
				return port

	raise Exception("No available port found.")


class Container:
	SERVICE_LABEL = "managed-minecraft-server"
	RUNNING = "running"


	def __init__(self, world: World):
		self.world: World = world


	async def run(self):
		image = Image(self.world.version)
		if(not await image.exists()):
			logger.info("Image does not exist. Building it now.")
			await image.build()

		# Get an available port.
		self.world.port = await get_available_port()
		logger.info(f"Allocated port {self.world.port} for world '{self.world.name}'.")

		command_args: list[str] = []  # Default to preexisting command_args
		if(self.world.last_played is None):
			logger.info("Adding bonus chest.")
			command_args.append("--bonusChest")

		process = await asyncio.create_subprocess_exec(
			"docker",
			"run",
			"--detach",
			"--interactive",
			"--rm",
			"--tty",
			"--label",
			f"service={self.SERVICE_LABEL}",
			"--publish",
			f"{self.world.port}:25565",
			"--volume",
			f"{self.world._data_path}:/usr/app",
			image.reference,
			*command_args,
			stderr=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
		)
		stdout, stderr = map(lambda io: io.decode().strip(), await process.communicate())
		if(process.returncode != 0):
			raise Exception(f"Failed to run docker container with stderr: {stderr}")

		self.world.container_id = stdout
		logger.info(f"Started container {self.world.container_id}.")


	async def state(self) -> str:
		process = await asyncio.create_subprocess_exec(
			"docker",
			"ps",
			"--all",
			"--filter",
			f"id={self.world.container_id}",
			"--format",
			"{{.State}}",
			stderr=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
		)
		stdout, stderr = map(lambda io: io.decode().strip(), await process.communicate())
		if(process.returncode != 0):
			raise Exception(f"Failed to check docker container with stderr: {stderr}")

		return stdout


	async def stop(self) -> None:
		process = await asyncio.create_subprocess_exec(
			"docker",
			"stop",
			self.world.container_id,
			stderr=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
		)
		_stdout, stderr = map(lambda io: io.decode().strip(), await process.communicate())
		if(process.returncode != 0):
			raise Exception(f"Failed to stop docker container with stderr: {stderr}")

		logger.info(f"Stopped container {self.world.container_id}")
