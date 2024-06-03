<?php

require_once('dbConfig.php');

$mysqli_connection = new MySQLi($host, $username, $password, $dbname, $port);

// The name of the text file
$filename = "temp_download.csv";

// Open a file in write mode ('w')
$fp = fopen($filename, 'w');

// Write the column headers to the file
fputcsv($fp, array('ReachID', 'RiverID', 'Name', 'geometry', 'EstTempC'));


if ($_POST['ReachID']) {
    $sql = <<<QUERY
    SELECT 
        ReachID, RiverID, Name, geometry, EstTempC
    FROM
        (SELECT 
            RiverID,
                ReachID,
                CONCAT(Rivers.Name, ' (', Reaches.RKm, ' km)') AS Name,
                ST_ASTEXT(Reaches.geometry) AS geometry
        FROM
            thorr.Rivers
        INNER JOIN Reaches USING (RiverID)) AS T
            INNER JOIN
        (SELECT 
            ReachID, ROUND(EstTempC, 2) AS EstTempC
        FROM
            thorr.ReachData
        WHERE
            ReachID = {$_POST['ReachID']} AND Date > '{$_POST['StartDate']}'
                AND Date < '{$_POST['EndDate']}'
                AND EstTempC IS NOT NULL) AS R USING (ReachID)
    QUERY;
} elseif ($_POST['RiverID']) {
    $sql = <<<QUERY
    SELECT 
        ReachID, RiverID, Name, geometry, EstTempC
    FROM
        (SELECT 
            RiverID,
                ReachID,
                CONCAT(Rivers.Name, ' (', Reaches.RKm, ' km)') AS Name,
                ST_ASTEXT(Reaches.geometry) AS geometry
        FROM
            thorr.Rivers
        INNER JOIN Basins USING (BasinID)
        INNER JOIN Reaches USING (RiverID)
        WHERE
            RiverID = {$_POST['RiverID']}) AS T
            INNER JOIN
        (SELECT 
            ReachID, ROUND(AVG(EstTempC), 2) AS EstTempC
        FROM
            thorr.ReachData
        WHERE
            Date > '{$_POST['StartDate']}'
                AND Date < '{$_POST['EndDate']}'
        GROUP BY ReachID) AS R USING (ReachID)
    QUERY;
} elseif ($_POST['BasinID']) {
    $sql = <<<QUERY
    SELECT 
        ReachID, RiverID, Name, geometry, EstTempC
    FROM
        (SELECT 
            RiverID,
                ReachID,
                CONCAT(Rivers.Name, ' (', Reaches.RKm, ' km)') AS Name,
                ST_ASTEXT(Reaches.geometry) AS geometry
        FROM
            thorr.Rivers
        INNER JOIN Basins USING (BasinID)
        INNER JOIN Reaches USING (RiverID)
        WHERE
            BasinID = {$_POST['BasinID']}) AS T
            INNER JOIN
        (SELECT 
            ReachID, ROUND(AVG(EstTempC), 2) AS EstTempC
        FROM
            thorr.ReachData
        WHERE
            Date > '{$_POST['StartDate']}'
                AND Date < '{$_POST['EndDate']}'
        GROUP BY ReachID) AS R USING (ReachID)
    QUERY;
}

$result = $mysqli_connection->query($sql);

// // write the query results to the file
// if (!$result) {
//     echo "Error: " . $sql . "<br>" . $mysqli_connection->error;
// }

while ($row = $result->fetch_assoc()) {
    fputcsv($fp, array($row['ReachID'], $row['RiverID'], $row['Name'], $row['geometry'], $row['EstTempC']));
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
