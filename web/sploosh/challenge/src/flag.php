<?php

$FLAG = getenv("FLAG");

$remote_ip = $_SERVER['REMOTE_ADDR'];
if ($remote_ip === "172.16.0.13" || $remote_ip === '172.16.0.14') {
  echo $FLAG;
} else {
  echo "No flag for you :)";
}
?>
