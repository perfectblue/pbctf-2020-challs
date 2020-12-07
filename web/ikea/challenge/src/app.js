function createFromObject(obj) {
  var el = document.createElement("span");

  for (var key in obj) {
    el[key] = obj[key]
  }

  return el
}

function generateName() {

  var default_config = {
    "style": "color: red;",
    "text": "Could not generate name"
  }

  var output = document.getElementById('output')
  var req = new XMLHttpRequest();

  req.open("POST", CONFIG.url);
  req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
  req.onreadystatechange = function () {

    if (req.readyState === XMLHttpRequest.DONE) {
      if (req.status === 200) {
        var obj = JSON.parse(req.responseText);
        var config = _.merge(default_config, obj)


        sandbox = document.createElement("iframe")
        sandbox.src = "/sandbox.php"
        var el = createFromObject({
          style: config.style,
          innerText: config.text
        })

        output.appendChild(sandbox)
        sandbox.onload = function () {
          sandbox.contentWindow.output.appendChild(el)
        }
      }
    }
  }

  req.send("name=" + CONFIG.name)
}

window.onload = function() {
  document.getElementById("button-submit").onclick = function() {
    window.location = "/?name=" + document.getElementById("input-name").value
  }

  generateName();
}
