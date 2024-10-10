function sendRequest(serverPath, inputNames, onSuccess = () => {}, onFailure = () => {}){
    const formData = new FormData();

    inputNames.forEach(name => {
        let inputElement = document.querySelection(`input[name="${name}"]`);
        let key = "value"
        if(!inputElement){
            key = "textContent";
            inputElement = document.querySelection(`#${name}`);
        }
        if(inputElement){
            formData.append(name, inputElement[key]);
        } else {
            console.warn(`Input field with name "${name}" not found`);
        }
    });

    fetch(serverPath, {
        method: 'POST',
        body: formData
    })
        .then(response => {
            console.log(response)
           if(response.ok){
               return response.json();
           } else {
               throw new Error(`Request failed with status ${response.status}`);
           }

        })
    .then(data => {
        console.log(data)
        if(data.status === 200){
            onSuccess(data);
        } else {
            onFailure(data);
        }

    })
        .catch(error => {
            console.log(error);
        })
}