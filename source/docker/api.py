#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-
__author__ = "MPZinke"

########################################################################################################################
#                                                                                                                      #
#   created by: MPZinke                                                                                                #
#   on 2026.05.24                                                                                                      #
#                                                                                                                      #
#   DESCRIPTION: https://docs.docker.com/reference/api/engine/version/v1.47                                            #
#                                                                                                                      #
########################################################################################################################


import asyncio
import os
import re
from typing import Optional
from urllib.parse import urljoin


import aiohttp


if(os.getenv("DOCKER") != "true"):
	connector_path = f"/Users/{os.getenv("USER")}/.docker/run/docker.sock"
else:
	connector_path = "/var/run/docker.sock"


class Attach:
	def __init__(self, container_id: str):
		self._container_id = container_id
		self._session = None
		self._loop = None
		self._raw_socket = None


	async def __aenter__(self):
		self._session = aiohttp.ClientSession(connector=aiohttp.UnixConnector(connector_path))
		self._loop = asyncio.get_event_loop()

		async with self._session.post(
			f"http://localhost/containers/{self._container_id}/attach",
			params={"stream": "1", "stdin": "1", "stdout": "1", "stderr": "1"},
			headers={"Content-Type": "application/vnd.docker.raw-stream", "Upgrade": "tcp", "Connection": "Upgrade"},
		) as response:
			connection = response.connection
			protocol = connection.protocol
			transport = protocol.transport
			raw_socket = transport.get_extra_info("socket")
			self._raw_socket = raw_socket.dup()
			self._raw_socket.setblocking(False)

			return self


	async def __aexit__(self, exc_type, exc_value, exc_tb):
		if(self._raw_socket is not None):
			self._raw_socket.close()

		await self._session.close()


	async def send(self, message: str) -> None:
		if(not message.endswith("\n")):
			message += "\n"

		await self._loop.sock_sendall(self._raw_socket, message.encode())


	async def match(self, pattern: str, *, timeout: float=5.0):
		compiled_pattern = re.compile(pattern)
		timeout_time = self._loop.time() + timeout

		try:
			while(self._loop.time() < timeout_time):
				try:
					remaining = timeout_time - self._loop.time()
					chunk = await asyncio.wait_for(
						self._loop.sock_recv(self._raw_socket, 4096),
						timeout=min(remaining, 0.5)
					)

				except asyncio.TimeoutError:
					continue

				if(not chunk):
					break

				text = chunk.decode(errors="replace")
				match = compiled_pattern.search(text)
				if(match is not None):
					return match

		except Exception:
			return None


async def request_json(
	path: str,
	method: str="GET",
	*,
	params: Optional[dict]=None,
	data: Optional[bytes]=None,
	headers: Optional[dict]=None,
	quiet: bool=False
) -> Optional[dict|list|str|int|None]:
	"""
	Query the API using UDS, and return the result as a JSON.
	Params:
		- path (str): The docker API path to query.
		- method (str): The HTTP method to request to.
		- quiet (bool, default False): Whether to raise an exception when no result is returned.

	Return:
		- dict|list|str|int|None: The parsed JSON value if the .
		- None: If (the request failed and quiet is True) or (the status is 204).

	Throws:
		- aiohttp.client_exceptions.ClientResponseError: If a non-2XX is returned and quiet is False.
		- aiohttp.client_exceptions.UnixClientConnectorError: If the socket is invalid.
	"""
	async with aiohttp.ClientSession(connector=aiohttp.UnixConnector(connector_path)) as session:
		url = urljoin("http://localhost", path)
		async with session.request(method, url, params=params, headers=headers, data=data) as response:
			if(quiet is False):
				try:
					response.raise_for_status()
				except aiohttp.client_exceptions.ClientResponseError as cause:
					body = await response.text()
					raise Exception(f"Failed with message: '{body}'") from cause

			elif(response.status // 100 != 2):
				return None

			if(response.status == 204):
				return None

			return await response.json()
