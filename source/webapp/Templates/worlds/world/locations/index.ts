

function onSubmit(event: SubmitEvent, element: HTMLFormElement, originalValue: string)
{
	let input: HTMLInputElement|null = element.firstElementChild as HTMLInputElement;
	if(input === null)
	{
		event.preventDefault();
		return;
	}

	let inputValue = input.value;
	if(inputValue === "" || inputValue === originalValue)
	{
		element.parentElement!.innerHTML = originalValue;
		event.preventDefault();
	}
}


function editValue(element: HTMLTableCellElement, endpoint: string)
{
	// Prevent inputs within inputs
	if(element.firstElementChild !== null)
	{
		console.log("First element is not null");
		console.log(element.innerHTML);
		return;
	}

	let originalValue: string = element.innerHTML.trim();
	let inputString = `
		<form
			action="${endpoint}"
			method="POST"
		>
			<input
				id="edit_value-input"
				name="edit_value-input"
				onchange="this.parentElement.requestSubmit();"
				onfocusout="this.parentElement.requestSubmit();"
				value="${originalValue}"
			/>
		</form>
	`;
	element.innerHTML = inputString;

	let form: HTMLFormElement = element.firstElementChild! as HTMLFormElement;
	form.onsubmit = (event: SubmitEvent) => { onSubmit(event, form, originalValue); };
	
	document.getElementById("edit_value-input")!.focus();
}
