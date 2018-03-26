<?php

// Super simple caching class
class PhpCache {
    protected $path = null;
    protected $duration = null;

    function __construct ( $path, $duration = 60) {
        $this->path = $path;
        $this->duration = $duration;
    }

    function get( $id ) {
        $file = $this->path . $id . '.cache';
        if (file_exists($file) && time() - filemtime($file) < $this->duration) {
            return unserialize( file_get_contents($file) );
        } else {
            return null;
        }
    }

    function set( $id, $obj) {
        $file = $this->path . $id . '.cache';
        file_put_contents($file, serialize($obj));
    }
}

// Set the JSON header
header("Content-type: text/json");

// Usage
$cache = new PhpCache(dirname(__FILE__).'/cache/', 10);
$key = $_GET['endpoint'];

$value = $cache->get($key);
if ($value == null) {
    $value = file_get_contents("http://duckhunt.api-d.com:6872/" . $key);
    $cache->set($key, $value);
    //echo 'created ' . $value;
}

echo $value;

/*


$content =
echo $content;
*/

