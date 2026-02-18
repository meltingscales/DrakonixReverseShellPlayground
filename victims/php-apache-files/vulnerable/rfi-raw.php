<?php
// Vulnerable Remote File Inclusion - no extension added
$url = $_GET['url'] ?? 'index';
if (isset($url)) {
    include($url);
}
?>
