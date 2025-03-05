<?php

///////////////////////////////////////////////////////////////////////////
// this is likely a redundant file, as it is not used in the application //
///////////////////////////////////////////////////////////////////////////

require_once('dbConfig.php');

$mysqli_connection = new MySQLi($host, $username, $password, $dbname, $port);

// if ($mysqli_connection->connect_error) {
//     echo "Not connected, error: " . $mysqli_connection->connect_error;
// }
$sql = "SELECT BasinID, Name, ST_AsGeoJSON(ST_Simplify(geometry, 0.005), 2) AS geometry FROM Basins WHERE BasinID = " . $_POST['BasinID'] . " ORDER BY Name ASC";
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
