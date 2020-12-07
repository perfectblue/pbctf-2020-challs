<?php
  include("./utils.php");

  if (!isset($_GET['name'])) {
    header("Location: ./?name=John");
    die();
  }

  $name = $_GET['name'];
  $nonce = base64_encode(random_bytes(20));

  $csp_1 = "Content-Security-Policy: ";
  $csp_1 .= "default-src 'none';";
  $csp_1 .= "script-src 'self' https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.4/lodash.min.js;";
  $csp_1 .= "connect-src 'self';";
  $csp_1 .= "frame-src 'self';";
  $csp_1 .= "img-src 'self';";
  $csp_1 .= "style-src 'self' https://maxcdn.bootstrapcdn.com/;";
  $csp_1 .= "base-uri 'none';";
  header($csp_1);
?>

<!DOCTYPE HTML>

<html>
  <head>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <link rel="stylesheet" href="/app.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.4/lodash.min.js"></script>
  </head>

  <body>
    <div class="container">
      <div class="d-flex justify-content-end">
        <a href="/login.php">Login</a>
      </div>

      <div class="d-flex justify-content-center">
        <h1>IKEA name generator</h1>
      </div>

      <div class="d-flex justify-content-center">
        <p>Wanna know your IKEA name?</p>
      </div>

      <div class="d-flex justify-content-center">
        <div class="input-group">
          <input id="input-name" value="<?php echo htmlentities($name); ?>"
                 class="form-control" placeholder="Enter your name here"/>
          <div class="input-group-append">
            <button id="button-submit" class="btn">Submit</button>
          </div>
        </div>
      </div>
    </div>


    <br/>
    <br/>
    <br/>

    <div class="d-flex justify-content-center">
      <div id="output"><?php echo $name; ?>, your IKEA name is : </div>
    </div>

    <script src="/config.php?name=<?php echo urlencode($name); ?>"></script>
    <script src="/app.js"></script>

    <div class="container">
      <div class="d-flex justify-content-end">
        Don't like your IKEA name? Report it&nbsp;<a href="/report.php">here</a>.
      </div>
    </div>

    <img id="tracking-pixel" width=1 height=1 src="/track.php">
  </body>
</html>
