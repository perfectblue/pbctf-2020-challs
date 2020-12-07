<!DOCTYPE HTML>
<html>
  <head>
      <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
  </head>

  <body class="mt-5">
    <div class="container d-flex justify-content-center">
      <h1>Sploosh</h1>
    </div>

    <div class="container d-flex justify-content-center">
      <p>Sploosh is a state of the art GAAS (geometry as a service) product, offering an easy-to-use API for fetching the geometry of any website.</p>
    </div>
    <div class="container d-flex justify-content-center">
      <p>Currently free to use; you can find the source code <a href="/dist.zip">here</a>.</p>
    </div>

    <div class="container d-flex justify-content-center">
      <div class="input-group mb-3">
        <input id="url" type="text" class="form-control" placeholder="Enter URL to scrape">
        <div class="input-group-append">
          <button class="btn btn-outline-secondary" type="button" onclick="scrape();">Submit</button>
        </div>
      </div>
    </div>

    <div class="mt-5 container d-flex justify-content-center"><b>Output:</b></div>
    <div id="output" class="mt-5 container d-flex justify-content-center"></div>

    <script>
      function scrape() {
        var urlToScrape = url.value;
        fetch("/api.php?url=" + urlToScrape).then(response => response.json()).then(function(data) {
          output.innerHTML = `
            <code>${data['geometry']}</code>
          `
        })
      }
    </script>
  </body>
</html>
