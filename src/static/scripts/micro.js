function triggerMicro(path, names = [], onSuccess = function(x){}, onFailure = function(x){})
{

    const event = new CustomEvent('MicroRequestEvent', {
        detail: {
            path: path,
            params: getParams(names),
            onSuccess: onSuccess,
            onFailure: onFailure
        }
    });

    document.dispatchEvent(event);
}

document.addEventListener('DOMContentLoaded', function(){
    const forms = document.querySelectorAll('form');

    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent the form from submitting
        });
    });

    try {
        validators.forEach(validator => {
            document.addEventListener('MicroRequestEvent', (e) => {
                if (e.detail.params[validator.label]) {
                    const validationResult = validator.validator(e.detail.params[validator.label]);
                    if (!validationResult) {
                        e.stopImmediatePropagation();
                    }
                }
            });
        });
    } catch (error) {
        console.error(error);
    }

    document.addEventListener('MicroRequestEvent', (e) => sendRequest(e));
});

function getCSRFToken()
{
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

function getParams(names)
{
    const params = {};

    names.forEach(name => {
        let inputElement = document.querySelector(`input[name="${name}"]`);
        let key = "value";

        if (!inputElement) {
            inputElement = document.querySelector(`#${name}`);
            if (inputElement.tagName === 'TEXTAREA') key = 'value';
            else key = "textContent";
        }

        if (inputElement) {
            params[name] = (name !== 'image') ? inputElement[key] : inputElement.files.length > 0 ? inputElement.files[0] : '';
        }
        else {
            console.warn(`Input field with name or ID '"${name}"' not found`);
        }
    });

    return params
}

function sendRequest(event)
{
    const serverPath = event.detail.path;
    const params = event.detail.params;
    const onSuccess = event.detail.onSuccess;
    const onFailure = event.detail.onFailure;

    let is_multiparted = params.hasOwnProperty('image') && params.image;
    let contentType = (is_multiparted) ? '' : 'application/x-www-form-urlencoded';
    const headers = is_multiparted ? {'X-CSRFToken': getCSRFToken()} : {'X-CSRFToken': getCSRFToken(), 'Content-Type': contentType}

    const form = (is_multiparted) ? new FormData() : new URLSearchParams(params);
    if (is_multiparted) {
        for (let param in params) {
            form.append(param, params[param]);
        }
    }

    fetch(serverPath, {
        method: 'POST',
        headers: headers,
        body: form
    })
    .then(response => {
        if (response.ok) {
            if (response.redirected) {
                window.location.href = response.url;
                return;
            }
            return response.json();
        }
        throw new Error(`Request failed with status ${response.status}`);
    })
    .then(data => {
        try {
            if (data.status === 200) {
                onSuccess(data);
                return;
            }
            onFailure(data);
        } catch(ignored) {}
    })
    .catch(error => {
        console.error(error);
    })
}
