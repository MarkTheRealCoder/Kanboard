function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}


function sendRequest(serverPath, inputNames, onSuccess = () => {}, onFailure = () => {}){
    const data = {}

    inputNames.forEach(name => {
        let inputElement = document.querySelector(`input[name="${name}"]`);
        let key = "value"

        if(!inputElement){
            key = "textContent";
            inputElement = document.querySelector(`#${name}`);
        }

        if(inputElement) data[name] = inputElement[key];
        else console.warn(`Input field with name "${name}" not found`);
    });

    fetch(serverPath, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(data)
    })
    .then(response => {
        if (response.ok) return response.json();
        throw new Error(`Request failed with status ${response.status}`);
    })
    .then(data => {
        if(data.status === 200) onSuccess(data);
        else onFailure(data);
    })
    .catch(error => {
        console.error(error);
    })
}