<?php
// Vulnerable eval
if (isset($_GET['code'])) {
    eval($_GET['code']);
}
?>
