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


import os
from typing import Optional
from urllib.parse import urljoin


import aiohttp


_session: Optional[aiohttp.ClientSession] = None


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
	global _session

	if(_session is None):
		if(os.getenv("DOCKER") != "true"):
			connector = aiohttp.UnixConnector("/Users/mpzinke/.docker/run/docker.sock")
		else:
			connector = aiohttp.UnixConnector("/var/run/docker.sock")
		_session = aiohttp.ClientSession(connector=connector)

	url = urljoin("http://localhost", path)
	async with _session.request(method, url, params=params, headers=headers, data=data) as response:
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
