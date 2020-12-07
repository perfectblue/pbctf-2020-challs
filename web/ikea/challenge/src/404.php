<?php
header("X-Frame-Options: deny");
header("X-Content-Type-Options: nosniff");
header("Content-Type: text/plain");
header("Content-Security-Policy: default-src 'none'");

$message = $_GET["msg"];
echo $message;
?>
