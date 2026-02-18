<?php
// Vulnerable Remote File Inclusion
$page = $_GET['page'] ?? 'index';
if (isset($page)) {
    include($page . ".php");
}
?>
