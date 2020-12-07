<?php
  error_reporting(0);
  if (isset($_POST['url'])) {

    if (stripos($_POST['url'], 'http://') !== 0 and (stripos($_POST['url'], 'https://') !== 0)) {
      echo 'URL must start with http:// or https://';
      die();
    }

    $redis = new Redis();
    $redis->connect('redis', 6379);

    $latest_attempt = time();

    $ips = explode(", ", $_SERVER["HTTP_X_FORWARDED_FOR"]);
    $ip = $ips[count($ips)-2];

    if (!isset($ip)) {
      $ip = '127.0.0.1';
    }

    $last_attempt = $redis->get('time.' . $ip);
    if ($last_attempt != null) {
      $last_attempt = intval($last_attempt);
    } else {
      $last_attempt = 0;
    }

    $time_diff = $latest_attempt - $last_attempt;

    if ($time_diff > 1) {
      $redis->rpush('submissions', $_POST['url']);
      $redis->setex('time.' . $ip, 60, $latest_attempt);
      echo 'Submitted';
    } else {
      echo 'Slow down please :)';
    }
  }
?>
<form action="/report.php" method="POST">
  <input placeholder="URL to report" type="text" name="url"></input>
  <input type="submit" />
</form>
