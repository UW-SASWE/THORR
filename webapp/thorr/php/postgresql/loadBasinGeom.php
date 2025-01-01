<?php

require_once('dbConfig.php');

$connStr = "host=$host port=$port dbname=$dbname user=$username password=$password";
$pgsql_connection = pg_connect($connStr);

// if ($mysqli_connection->connect_error) {
//     echo "Not connected, error: " . $mysqli_connection->connect_error;
// }
$sql = <<<QUERY
SELECT
	"BasinID",
	"Name",
	ST_ASGEOJSON (ST_SIMPLIFY ("geometry", 0.005), 2) AS GEOMETRY
FROM
	$schema."Basins"
WHERE
	"BasinID" = {$_POST['BasinID']}
ORDER BY
	"Name" ASC;
QUERY;
// echo $sql;
// $sql = "SELECT BasinID, Name, ST_AsGeoJSON(ST_Simplify(geometry, 0.005), 2) AS geometry, ST_SRID(geometry) as SRID FROM Basins WHERE BasinID = " . $_POST['BasinID'] . " ORDER BY Name ASC";

$result = pg_query($pgsql_connection, $sql);

# Build GeoJSON feature collection array
$geojson = array(
    'type'      => 'FeatureCollection',
    'features'  => array()
);

# Loop through rows to build feature arrays
while ($row = pg_fetch_assoc($result)) {
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

pg_close($pgsql_connection);