<?php
include("./utils.php");
header("Content-Type: application/javascript");

$name = $_GET['name'];

if (!is_string($name)) {
  $name = null;
}
?>
CONFIG = {
  url: "/get_name.php",
  name: "<?php echo js_filter($name); ?>"
}
