

import asyncio
import json
import shutil
import subprocess
from threading import Event, Thread
import traceback
from typing import Tuple


from database.classes import World
from database.queries.worlds import get_running_worlds, set_world_container, set_world_state, set_world_stopped
from docker import Container


def update_world_statuses() -> None:
	worlds: list[World] = get_running_worlds()
	process = subprocess.run(
		[
			"docker",
			"ps",
			"--format",
			"json",
		],
		capture_output=True,
		check=True,
		text=True,
	)
	containers: list[Tuple[str, str]] = list(map(json.loads, filter(None, process.stdout.strip().split("\n"))))
	minecraft_filter = lambda container: f"service={Container.SERVICE_LABEL}" in container["Labels"].split(",")
	minecraft_containers_iter: iter = filter(minecraft_filter, containers)
	minecraft_container_ids: list[str] = list(map(lambda container: container["ID"], minecraft_containers_iter))

	for world in worlds:
		if(world.container_id is not None and world.container_id[:12] in minecraft_container_ids):
			print(f"Skipping world [{world.id}]{world.name}")
			continue

		print(f"Updating world [{world.id}]{world.name}")
		try:
			asyncio.run(world.read_data())

		except FileNotFoundError:
			print("World folder not found. Resetting world.")
			world.state = "offline"
			world.container_id = None
			world.port = None
			set_world_container(world)
			set_world_state(world)

		else:
			set_world_stopped(world)
			shutil.rmtree(world._data_path)


def update_loop(event: Event):
	while(not event.wait(60)):
		try:
			update_world_statuses()

		except Exception:
			print(traceback.format_exc())

	print("Updater stopped.")


def start_updater() -> Tuple[Event, Thread]:
	event = Event()
	thread = Thread(target=update_loop, args=(event,))
	thread.start()

	return event, thread
