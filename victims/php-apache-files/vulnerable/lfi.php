<?php
// Vulnerable Local File Inclusion
// Example: lfi.php?file=../../../etc/passwd
$file = $_GET['file'] ?? 'index.php';
if (isset($file)) {
    include($file);
}
?>
