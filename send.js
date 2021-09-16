fetch('http://localhost:24654/refresh', {
    method: 'POST',
    body: JSON.stringify(
        document.cookie
    ),
    cache: 'no-cache',
    credentials: 'same-origin',
    headers: {
        'content-type': 'application/json'
    },
    mode: 'cors',
    redirect: 'follow',
    referrer: 'no-referrer',
}).then((resp) => {
    return resp.text()
}).then(uri => {
    console.log(uri)
})