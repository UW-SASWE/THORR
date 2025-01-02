<?php

require_once('dbConfig.php');

$connStr = "host=$host port=$port dbname=$dbname user=$username password=$password";
$pgsql_connection = pg_connect($connStr);

// The name of the text file
$filename = "temp_download.csv";

// Open a file in write mode ('w')
$fp = fopen($filename, 'w');

// Write the column headers to the file
fputcsv($fp, array('ReachID', 'RiverID', 'Name', 'geometry', 'EstTempC'));


if ($_POST['ReachID']) {
    $sql = <<<QUERY
    SELECT 
        "ReachID", "RiverID", "Name", "geometry", "EstTempC"
    FROM
        (SELECT 
            "RiverID",
                "ReachID",
                CONCAT("Rivers"."Name", ' (', "Reaches"."RKm", ' km)') AS "Name",
                ST_ASTEXT("Reaches"."geometry") AS "geometry"
        FROM
            "$schema"."Rivers"
        INNER JOIN "$schema"."Reaches" USING ("RiverID")) AS T
            INNER JOIN
        (SELECT 
            "ReachID", ROUND("EstTempC"::numeric, 2) AS "EstTempC"
        FROM
            "$schema"."ReachData"
        WHERE
            "ReachID" = {$_POST['ReachID']} AND "Date" > '{$_POST['StartDate']}'
                AND "Date" < '{$_POST['EndDate']}'
                AND "EstTempC" IS NOT NULL) AS R USING ("ReachID")
    QUERY;
} elseif ($_POST['RiverID']) {
    $sql = <<<QUERY
    SELECT 
        "ReachID", "RiverID", "Name", "geometry", "EstTempC"
    FROM
        (SELECT 
            "RiverID",
                "ReachID",
                CONCAT("Rivers"."Name", ' (', "Reaches"."RKm", ' km)') AS "Name",
                ST_ASGEOJSON("Reaches"."geometry") AS "geometry"
        FROM
            "$schema"."Rivers"
        INNER JOIN "$schema"."Basins" USING ("BasinID")
        INNER JOIN "$schema"."Reaches" USING ("RiverID")
        WHERE
            "RiverID" = {$_POST['RiverID']}) AS T
            INNER JOIN
        (SELECT 
            "ReachID", ROUND(AVG("EstTempC")::numeric, 2) AS "EstTempC"
        FROM
            "$schema"."ReachData"
        WHERE
            "Date" > '{$_POST['StartDate']}'
                AND "Date" < '{$_POST['EndDate']}'
        GROUP BY "ReachID") AS R USING ("ReachID")
    QUERY;
} elseif ($_POST['BasinID']) {
    $sql = <<<QUERY
    SELECT 
        "ReachID", "RiverID", "Name", "geometry", "EstTempC"
    FROM
        (SELECT 
            "RiverID",
                "ReachID",
                CONCAT("Rivers"."Name", ' (', "Reaches"."RKm", ' km)') AS "Name",
                ST_ASGEOJSON("Reaches"."geometry") AS geometry
        FROM
            "$schema"."Rivers"
        INNER JOIN "$schema"."Basins" USING ("BasinID")
        INNER JOIN "$schema"."Reaches" USING ("RiverID")
        WHERE
            "BasinID" = {$_POST['BasinID']}) AS T
            INNER JOIN
        (SELECT 
            "ReachID", ROUND(AVG("EstTempC")::numeric, 2) AS "EstTempC"
        FROM
            "$schema"."ReachData"
        WHERE
            "Date" > '{$_POST['StartDate']}'
                AND "Date" < '{$_POST['EndDate']}'
        GROUP BY "ReachID") AS R USING ("ReachID")
    QUERY;
}

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
