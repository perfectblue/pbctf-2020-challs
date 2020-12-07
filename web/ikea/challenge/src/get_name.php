<?php

header("Content-Type: application/json");
$names = array(
  "BASSLEKATILLÖT",
  "ÅR",
  "ELIPET",
  "SOLM",
  "ODANDHEL",
  "STER",
  "OXSK",
  "NORABRATA",
  "ÅSUN",
  "FON",
  "HEN",
  "ÖRRSESTER",
  "FÖR",
  "BETTJANÄR",
  "HJÄRLIG",
  "SIG",
  "RAM",
  "TRUM",
  "VACKIS",
  "MÖRT",
  "SORPOÄNGEN",
  "LIATS",
  "KOSTEN",
  "KOT"
);

$new_name = $_POST['name'];
$message = array(
  "text" => $names[crc32($new_name) % count($names)]
);


echo json_encode($message);
?>
