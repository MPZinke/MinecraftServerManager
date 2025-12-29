

import asyncio
import shutil
import subprocess
from threading import Event, Thread
import traceback
from typing import Tuple


from database.classes import World
from database.queries.worlds import get_running_worlds, set_world_port, set_world_state, set_world_stopped
from docker import Container


def update_world_statuses() -> None:
	process = subprocess.run(
		[
			"docker",
			"ps",
			"--format",
			"{{.Names}}",
		],
		capture_output=True,
		check=True,
		text=True,
	)
	worlds: list[World] = get_running_worlds()

	docker_container_names: list[str] = process.stdout.strip().split("\n")

	for world in worlds:
		if(Container(world).name in docker_container_names):
			print(f"Skipping world [{world.id}]{world.name}")
			continue

		print(f"Updating world [{world.id}]{world.name}")
		try:
			asyncio.run(world.read_data())
			print("async ran")

		except FileNotFoundError:
			print("FileNotFoundError")
			world.state = "offline"
			set_world_port(world)
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

	print("Exited event loop.")


def run_update() -> Tuple[Event, Thread]:
	event = Event()
	thread = Thread(target=update_loop, args=(event,))
	thread.start()

	return event, thread
