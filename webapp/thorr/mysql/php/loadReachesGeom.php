<?php

require_once('dbConfig.php');

$mysqli_connection = new MySQLi($host, $username, $password, $dbname, $port);

// if ($mysqli_connection->connect_error) {
//     echo "Not connected, error: " . $mysqli_connection->connect_error;
// }

// echo ($_POST['row_count'] and $_POST['offset']);

if ($_POST['offset'] || $_POST['row_count']) {
    $sql = <<<QUERY
            SELECT 
            ReachData.Date,
            EstTempC,
            R.ReachID,
            RiverID,
            Name,
            RKm,
            geometry
        FROM
            (SELECT 
                ReachID,
                    RiverID,
                    Rivers.Name AS Name,
                    Reaches.RKm AS RKm,
                    ST_ASGEOJSON(Reaches.geometry) AS geometry
            FROM
                thorr.Rivers
            INNER JOIN Basins USING (BasinID)
            INNER JOIN Reaches USING (RiverID)
            WHERE
                Basins.BasinID = {$_POST['BasinID']}) AS R
                INNER JOIN
            ReachData USING (ReachID)
                INNER JOIN
            (SELECT 
                ReachID, MAX(Date) AS Date
            FROM
                ReachData
            WHERE
                EstTempC IS NOT NULL
            GROUP BY ReachID) AS latestEstimate ON latestEstimate.Date = ReachData.Date
                AND latestEstimate.ReachID = ReachData.ReachID
        LIMIT {$_POST['offset']}, {$_POST['row_count']};
        QUERY;
} else {
    $sql = <<<QUERY
            SELECT 
            ReachData.Date,
            EstTempC,
            R.ReachID,
            RiverID,
            Name,
            RKm,
            geometry
        FROM
            (SELECT 
                ReachID,
                    RiverID,
                    Rivers.Name AS Name,
                    Reaches.RKm AS RKm,
                    ST_ASGEOJSON(Reaches.geometry) AS geometry
            FROM
                thorr.Rivers
            INNER JOIN Basins USING (BasinID)
            INNER JOIN Reaches USING (RiverID)
            WHERE
                Basins.BasinID = {$_POST['BasinID']}) AS R
                INNER JOIN
            ReachData USING (ReachID)
                INNER JOIN
            (SELECT 
                ReachID, MAX(Date) AS Date
            FROM
                ReachData
            WHERE
                EstTempC IS NOT NULL
            GROUP BY ReachID) AS latestEstimate ON latestEstimate.Date = ReachData.Date
                AND latestEstimate.ReachID = ReachData.ReachID
        QUERY;
};



// echo $sql;

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
