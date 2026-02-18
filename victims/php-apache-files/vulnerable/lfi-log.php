<?php
// Log poisoning target
// Include the access log which can be poisoned via User-Agent header
$log = $_GET['log'] ?? '/var/log/apache2/access.log';
echo "Reading log: $log<br>";
if (file_exists($log)) {
    highlight_file($log);
} else {
    echo "Log file not found.";
}
?>
