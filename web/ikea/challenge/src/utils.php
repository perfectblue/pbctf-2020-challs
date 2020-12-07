<?php
function js_filter($str) {
  return str_replace("/", "\\/", addslashes($str));
}
?>
