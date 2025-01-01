<?php

require_once('dbConfig.php');

$connStr = "host=$host port=$port dbname=$dbname user=$username password=$password";
$pgsql_connection = pg_connect($connStr);

// if ($mysqli_connection->connect_error) {
//     echo "Not connected, error: " . $mysqli_connection->connect_error;
// }

// echo ($_POST['row_count'] and $_POST['offset']);

if ($_POST['type'] == 'dam') {
    $sql = <<<QUERY
        SELECT ST_AsGeoJSON(ST_Envelope("ReservoirGeometry")) as geometry, "Name", "Reservoir"
        FROM $schema."Dams"
        WHERE "DamID" = {$_POST['id']};
        QUERY;
} elseif ($_POST['type'] == 'reach') {
    $sql = <<<QUERY
        SELECT ST_AsGeoJSON(ST_Envelope("Reaches"."geometry")) as geometry, "Rivers"."Name" as Name,
        "ReachID",
        "RKm"
        FROM $schema."Reaches"
        INNER JOIN $schema."Rivers" USING ("RiverID")
        WHERE "ReachID" = {$_POST['id']};
        QUERY;
} elseif ($_POST['type'] == 'basin') {
    $sql = <<<QUERY
        SELECT ST_AsGeoJSON(ST_Envelope("geometry")) as geometry, "Basins"."Name" as Name
        FROM $schema."Basins"
        WHERE "BasinID" = {$_POST['id']};
        QUERY;
} else {
    $sql = <<<QUERY
        SELECT ST_AsGeoJSON(ST_Envelope("geometry")) as geometry, "Name"
        FROM $schema."Rivers"
        WHERE "RiverID" = {$_POST['id']};
        QUERY;
};



// echo $sql;

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
