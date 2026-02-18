<?php
// Vulnerable XXE via SimpleXML
if (isset($_GET['xml'])) {
    $xml = $_GET['xml'];
    $data = simplexml_load_string($xml);
    echo "<pre>" . print_r($data, true) . "</pre>";
} else {
    echo "<html><head><title>XXE SimpleXML</title></head><body>";
    echo "<h1>XXE via SimpleXML</h1>";
    echo "<p>Pass XML via GET parameter 'xml'</p>";
    echo "</body></html>";
}
?>
