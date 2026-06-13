

import asyncio
import shutil
import traceback
from typing import Awaitable


from database.classes import World
from database.queries.worlds import get_running_worlds, set_world_container, set_world_state, set_world_offline
from docker import Container
from docker.api import request_json
from logger import logger



async def update_world_statuses() -> None:
	worlds_promise: Awaitable[list[World]] = get_running_worlds()
	# FROM: https://docs.docker.com/reference/api/engine/version/v1.47/#tag/Container/operation/ContainerList
	containers_promise: Awaitable[list[dict]] = request_json(
		"containers/json",
		params={"label": f"service={Container.SERVICE_LABEL}"}
	)
	worlds, containers = await asyncio.gather(worlds_promise, containers_promise)  # : list[World], list[dict]

	container_ids: list[str] = list(map(lambda container: container["Id"], containers))

	for world in worlds:
		if(world.container_id is not None and world.container_id in container_ids):
			logger.info(f"Skipping world {world.name}")
			continue

		logger.info(f"Updating world {world.name}")
		try:
			await world.read_data()

		except FileNotFoundError:
			logger.info(f"World folder '{world._data_path!s}' not found. Resetting world.")
			world.state = "offline"
			world.container_id = None
			world.port = None
			set_world_container_promise: Awaitable[None] = set_world_container(world)
			set_world_state_promise: Awaitable[None] = set_world_state(world)
			await asyncio.gather(set_world_container_promise, set_world_state_promise)

		else:
			await set_world_offline(world)
			shutil.rmtree(world._data_path)


async def update_loop():
	while(True):
		try:
			await update_world_statuses()

		except Exception:
			logger.error(traceback.format_exc())

		await asyncio.sleep(60)

	logger.info("Updater stopped.")
