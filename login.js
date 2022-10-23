let login_button;
let loading_icon
let epic_icon


let auth_id;
let url;


function locale_request(method, path, data = null, headers = null, callback = null) {
    let req = new XMLHttpRequest();
    req.open(method, window.location.protocol + '//' + window.location.host + '/api' + path)

    if (headers) {
        for (const [name, value] of Object.entries(headers)) {
            req.setRequestHeader(name, value);
        }
    }

    req.send(data);

    if (callback) {
        req.onload = () => {
            callback(req.status, req.responseText);
        }
    }
    return req;
}


function create_link() {
    locale_request('POST', '/create-auth', null, null, (status, resp) => {
        if (status == 200) {
            let data = JSON.parse(resp);
            auth_id = data['auth-id'];
            url = data['url'];

            loading_icon.classList.add('hidden');
            epic_icon.classList.remove('hidden');
        }
    })
}


function authentificate() {
    locale_request(
        'POST',
        '/epic-authentificate',
        JSON.stringify({'auth-id': auth_id}),
        null,
        (status, resp) => {
            if (status == 200) {
                window.location.href = '/?token=' + resp;
            }
        }
    )
}


window.onload = () => {
    login_button = document.getElementById('login-btn');
    login_text = document.getElementById('login-text');
    loading_icon = document.getElementById('load');
    epic_icon = document.getElementById('init');

    create_link();

    login_button.onclick = () => {
        // wierd but true.
        login_button.onclick = () => {
            epic_icon.classList.add('hidden');
            loading_icon.classList.remove('hidden');
            authentificate();
        }
        login_text.innerText = 'continue...';
        window.open(url, '_blank');
    }
}