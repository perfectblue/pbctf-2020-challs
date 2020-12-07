<?php
error_reporting(0);

header("Content-Type: application/json");

function fail() {
  echo "{}";
  die();
}

if (!isset($_GET['url'])) {
  fail();
}


$url = $_GET['url'];

if ($url === '') {
  fail();
}

try {
  $json = file_get_contents("http://splash:8050/render.json?timeout=1&url=" . urlencode($url));
  $out = array("geometry" => json_decode($json)->geometry);
  echo json_encode($out);
} catch(Exception $e) {
  fail();
}
?>
