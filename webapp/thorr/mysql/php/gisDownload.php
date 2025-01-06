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
                ST_ASGEOJSON(Reaches.geometry) AS geometry
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
                ST_ASGEOJSON(Reaches.geometry) AS geometry
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

# Build GeoJSON feature collection array
$geojson = array(
    'type'      => 'FeatureCollection',
    'features'  => array()
);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {
    // echo $row['geometry'];
    $properties = $row;
    # Remove wkb and geometry fields from properties
    unset($properties['geometry']);
    $feature = array(
        'type' => 'Feature',
        'geometry' => json_decode($row['geometry']),
        'properties' => $properties
    );
    # Add feature arrays to feature collection array
    array_push($geojson['features'], $feature);
}

// // header('Content-type: application/json');
echo json_encode($geojson, JSON_NUMERIC_CHECK);

$mysqli_connection->close();
