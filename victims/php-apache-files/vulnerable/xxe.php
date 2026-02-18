<?php
// Vulnerable XXE via XML parsing
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $xml = file_get_contents('php://input');
    $doc = new DOMDocument();
    $doc->loadXML($xml);

    $xsl = new XSLTProcessor();
    $xsl->importStyleSheet($doc);

    echo "<h2>XXE Result:</h2>";
    echo "<pre>";
    echo htmlspecialchars($doc->saveXML());
    echo "</pre>";

    try {
        $result = $xsl->transformToXML($doc);
        if ($result) {
            echo "<h2>Transformed:</h2><pre>" . htmlspecialchars($result) . "</pre>";
        }
    } catch (Exception $e) {
        echo "<p style='color:red'>Error: " . htmlspecialchars($e->getMessage()) . "</p>";
    }
} else {
    echo "<html><head><title>XXE Vulnerability</title></head><body>";
    echo "<h1>XXE Vulnerability Test</h1>";
    echo "<p>Send POST request with XML data containing XXE payload.</p>";
    echo "</body></html>";
}
?>
