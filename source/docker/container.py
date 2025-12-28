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
from io import BytesIO
import socket
import subprocess
import tarfile
from threading import Thread
from typing import Optional


from docker.image import Image


class Container:
	EXITED = "exited"
	PAUSED = "paused"
	RUNNING = "running"


	def __init__(self, id: str, image: Image, port: Optional[int]):
		self.id: str = id
		self.image: Image = image
		self.port: Optional[int] = port


	@staticmethod
	def run(image: Image) -> object:
		port: Optional[int] = None
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			if(s.connect_ex(('', 25565)) != 0):
				port: int = 25565

		if(port is None):
			# FROM: https://stackoverflow.com/a/1365284
			sock = socket.socket()
			sock.bind(("localhost", 0))
			port: int = sock.getsockname()[1]

		run_process = subprocess.run(
			[
				"docker",
				"run",
				"--detach",
				"--rm",
				"--publish",
				f"{port}:25565",
				"--name",
				f"minecraft-{image.id}",
				image.id,
			],
			capture_output=True,
			check=True,
			text=True,
		)
		if(run_process.returncode != 0):
			print(run_process.stderr, run_process.stdout)

		return Container(run_process.stdout.strip().replace("sha256:", ""), image, port)


	async def state(self) -> str:
		process = await asyncio.create_subprocess_exec(
			"docker",
			"ps",
			"--all",
			"--filter",
			f"id={self.id}",
			"--format",
			"{{.State}}",
			stderr=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
		)

		await process.wait()

		if(process.returncode != 0):
			return None

		return (await process.communicate())[0].decode().strip()


	def stop(self) -> bytes:
		# Pause the container.
		subprocess.run(
			[
				"docker",
				"pause",
				self.id,
			],
			capture_output=True,
			check=True,
			text=True,
		)

		# Get the world data from the container.
		data_process: subprocess.CompletedProcess = subprocess.run(
			[
				"docker",
				"cp",
				f"{self.id}:/usr/app",
				"-",
			],
			capture_output=True,
			check=True,
		)
		data: bytes = data_process.stdout
		compressed_bytes_file = BytesIO()
		with tarfile.open(fileobj=compressed_bytes_file, mode="w:gz") as compressed_file:
			with tarfile.open(fileobj=BytesIO(data), mode="r") as tar_file:
				for file in tar_file.getmembers():
					if(file.name not in ["app", "app/server.jar"]):
						compressed_file.addfile(file, tar_file.extractfile(file))

		compressed_bytes_file.seek(0)

		# Fully stop & remove container.
		subprocess.run(
			[
				"docker",
				"stop",
				self.id,
			],
			capture_output=True,
			check=False,
		)

		return compressed_bytes_file.read()
