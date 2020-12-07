<?php
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
  </head>

  <body>
    <div class="container">
      <div class="d-flex justify-content-center">
        <h1>Login</h1>
      </div>

      <div class="d-flex justify-content-center">
        <?php
        if ($_COOKIE['session'] === 'be2171a063883cd6f356707eb8dd601d6d8ac26a') {
          echo getenv('FLAG');
        } else {
          echo '<p>Login functionality not implemented yet - Only admins can enter with a special cookie.</p>';
        }
        ?>
      </div>
  </body>
</html>
