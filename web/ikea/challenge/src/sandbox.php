<?php
  $csp_1 = "Content-Security-Policy: ";
  $csp_1 .= "default-src 'none';";
  $csp_1 .= "script-src 'self' https://cdnjs.cloudflare.com/ajax/libs/angular.js/1.8.2/angular.js;";
  $csp_1 .= "style-src 'self' https://maxcdn.bootstrapcdn.com/;";
  $csp_1 .= "connect-src https:;";
  $csp_1 .= "base-uri 'none';";
  header($csp_1);

?>

<!DOCTYPE HTML>
<html>
  <head></head>
  <body>
    <div id="output"></div>
  </body>
</html>
