<?php

require_once('dbConfig.php');

$mysqli_connection = new MySQLi($host, $username, $password, $dbname, $port);

// The name of the text file
$filename = "temp_download_dam.csv";

// Open a file in write mode ('w')
$fp = fopen($filename, 'w');

$sql = <<<QUERY
{$_POST['SQL']}
QUERY;


$result = $mysqli_connection->query($sql);

// write column headers
fputcsv($fp, array_keys($result->fetch_assoc()));

// write the query results to the file
while ($row = $result->fetch_assoc()) {
    fputcsv($fp, $row);
}


// Close the file
fclose($fp);

// Set headers to force download on the client side
header('Content-Description: File Transfer');
header('Content-Type: application/octet-stream');
header('Content-Disposition: attachment; filename="' . basename($filename) . '"');
header('Expires: 0');
header('Cache-Control: must-revalidate');
header('Pragma: public');
header('Content-Length: ' . filesize($filename));

// Clear the output buffer
ob_clean();
flush();

// Read the file and output its contents
readfile($filename);

// delete file
unlink($filename);

// Terminate the script
exit;
