
const DELETE_TD = document.getElementById("delete-td")!;
const LAST_PLAYED_TD = document.getElementById("last_played-td")!;
const RUN_BUTTON_DIV = document.getElementById("run_button-td")!;
const RUNNING_CONTAINER_DIV = document.getElementById("running_container-div")!;
const STATE_TD = document.getElementById("state-td")!;


async function get_online_players()
{
	let online_players_td = document.getElementById("online_players-td");
	if(online_players_td != null)
	{
		let response = await fetch(
			`/worlds/{{ world.id }}/players/online`,
			{
				method: `GET`,
				headers: {"Content-Type": "application/json"},
			}
		);
		let response_body = await response.text();
		online_players_td.innerHTML = response_body;
	}
}


async function get_stats()
{
	let stats_td = document.getElementById("stats-td");
	if(stats_td != null)
	{
		let response = await fetch(`/worlds/{{ world.id }}/stats`, {method: `GET`});

		let response_body = await response.text();
		stats_td.innerHTML = response_body;
	}
}


async function update_state()
/*
Only called in a state transition.
*/
{
	let response = await fetch(
		`/worlds/{{ world.id }}/state/json`,
		{
			method: `GET`,
			headers: {"Content-Type": "application/json"},
		}
	);

	let response_json = await response.json();

	DELETE_TD.innerHTML = response_json.html.delete_button;
	RUNNING_CONTAINER_DIV.innerHTML = response_json.html.running_container;
	RUN_BUTTON_DIV.innerHTML = response_json.html.run_button;
	LAST_PLAYED_TD.innerHTML = response_json.last_played;
	STATE_TD.innerHTML = response_json.state;

	if(response_json.state == "Running" || response_json.state == "Offline")
	{
		clearInterval(UPDATE_STATE_INTERVAL);
	}
	if(response_json.state == "Running")
	{
		GET_ONLINE_PLAYERS_INTERVAL = setInterval(get_online_players, 5000);
		GET_STATS_INTERVAL = setInterval(get_stats, 5000);
		get_online_players();
		get_stats();
	}
	if(response_json.state == "Offline")
	{
		clearInterval(GET_ONLINE_PLAYERS_INTERVAL);
		clearInterval(GET_STATS_INTERVAL);
	}
}


let GET_ONLINE_PLAYERS_INTERVAL: ReturnType<typeof setInterval>;
let GET_STATS_INTERVAL: ReturnType<typeof setInterval>;
let UPDATE_STATE_INTERVAL: ReturnType<typeof setInterval>;
if({{ world.state | tojson }} !== "Offline" && {{ world.state | tojson }} !== "Running")
{
	UPDATE_STATE_INTERVAL = setInterval(update_state, 1000);
}
else if({{ world.state | tojson }} === "Running")
{
	get_online_players();
	get_stats();
	GET_ONLINE_PLAYERS_INTERVAL = setInterval(get_online_players, 5000);
	GET_STATS_INTERVAL = setInterval(get_stats, 5000);
}
