<?php
// Set the JSON header
header("Content-type: text/json");

$content = file_get_contents("http://duckhunt.api-d.com:6872/" . $_GET['endpoint']);
echo $content;
