
const WORLD_TD = document.getElementById("world-td") as HTMLElement;

async function get_player_world(): Promise<void>
{
	let response = await fetch(
		`/players/{{ player.id }}/world`,
		{
			method: `GET`,
			headers: {"Content-Type": "application/json"},
		}
	);
	let world_info = await response.text();
	WORLD_TD.innerHTML = world_info;
}


get_player_world();
setInterval(get_player_world, 5000);
