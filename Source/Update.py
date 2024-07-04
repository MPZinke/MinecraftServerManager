

from database.queries import get_version, get_world, update_running_world, update_stopped_world


with open("/Users/mpzinke/Workspace/Minecraft/data.tar.gz", "rb") as file:
	data = file.read()

update_stopped_world(7, data)
