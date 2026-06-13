# MinecraftServerManager
A webapp for easily creating, storing, starting, interacting with & stopping Minecraft servers in a docker image.

## Features
- Creates, stores, starts, & downloads minecraft worlds as standalone docker containers.
- Adds location tracking to mark a notable place in the minecraft world based on the users location in the world.
- Teleport a player to a saved location.
- OP a player.


## Setup

1. Create DB
```bash
createdb Minecraft
psql Minecraft
\i Database/Schema.sql
\i Data.sql
```

2. Build & run the Docker image
```bash
export VERSION='0.0.1'
docker compose build
docker compose up
```