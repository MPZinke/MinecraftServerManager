
const DELETE_TD = document.getElementById("delete-td")!;
const LAST_PLAYED_TD = document.getElementById("last_played-td")!;
const RUN_BUTTON_DIV = document.getElementById("run_button-td")!;
const RUNNING_CONTAINER_TD = document.getElementById("running_container-td")!;
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


async function update_state()
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
	RUNNING_CONTAINER_TD.innerHTML = response_json.html.running_container;
	RUN_BUTTON_DIV.innerHTML = response_json.html.run_button;
	LAST_PLAYED_TD.innerHTML = response_json.last_played;
	STATE_TD.innerHTML = response_json.state;

	if(response_json.state == "running" || response_json.state == "offline")
	{
		clearInterval(UPDATE_STATE_INTERVAL);
	}
	if(response_json.state == "running")
	{
		GET_ONLINE_PLAYERS_INTERVAL = setInterval(get_online_players, 5000);
		get_online_players();
	}
	if(response_json.state == "offline")
	{
		clearInterval(GET_ONLINE_PLAYERS_INTERVAL);
	}
}


function edit_value(
	element: HTMLElement,
	original_value: string,
	endpoint: string,
	original_value_can_be_falsey: boolean=false
): void
{
	// Prevent inputs within inputs
	if(element.firstElementChild !== null)
	{
		return;
	}

	let input_string: string = `
		<form
			action="${endpoint}"
			method="POST"
			onsubmit="update_check(event, this, \`${original_value}\`, \`${element.innerHTML}\`);"
		>
			<input
				id="edit_value-input"
				name="edit_value-input"
				onchange="this.parentElement.requestSubmit();"
				onfocusout="this.parentElement.requestSubmit();"
				value="${(original_value || original_value_can_be_falsey) ? original_value : ``}"
			/>
		</form>
	`;
	element.innerHTML = input_string;

	document.getElementById("edit_value-input")!.focus();
}


function update_check(event: SubmitEvent, element: HTMLElement, original_value: string, original_HTML: string): void
{
	let new_value: string = (element.firstElementChild as HTMLInputElement).value;
	if(new_value === original_value)
	{
		(element.parentElement as HTMLInputElement).innerHTML = original_HTML;
		event.preventDefault();
	}
}



let GET_ONLINE_PLAYERS_INTERVAL: ReturnType<typeof setInterval>;
let UPDATE_STATE_INTERVAL: ReturnType<typeof setInterval>;
if({{ world.state | tojson }} !== "offline" && {{ world.state | tojson }} !== "running")
{
	UPDATE_STATE_INTERVAL = setInterval(update_state, 1000);
}
else if({{ world.state | tojson }} === "running")
{
	get_online_players();
	GET_ONLINE_PLAYERS_INTERVAL = setInterval(get_online_players, 5000);
}
