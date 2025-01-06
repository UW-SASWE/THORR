<?php

require_once('dbConfig.php');

$connStr = "host=$host port=$port dbname=$dbname user=$username password=$password";
$pgsql_connection = pg_connect($connStr);

// if ($mysqli_connection->connect_error) {
//     echo "Not connected, error: " . $mysqli_connection->connect_error;
// }

// echo ($_POST['row_count'] and $_POST['offset']);

if (isset($_POST['offset']) || isset($_POST['row_count'])) {
    $sql = <<<QUERY
        SELECT 
            "ReachData"."Date"::Date as "Date",
            "EstTempC",
            R."ReachID",
            "RiverID",
            "Name",
            "RKm",
            "geometry"
        FROM
            (SELECT 
                "ReachID",
                    "RiverID",
                    "Rivers"."Name" AS "Name",
                    "Reaches"."RKm" AS "RKm",
                    ST_ASGEOJSON("Reaches"."geometry") AS "geometry"
            FROM
                "$schema"."Rivers"
            INNER JOIN "$schema"."Basins" USING ("BasinID")
            INNER JOIN "$schema"."Reaches" USING ("RiverID")
            WHERE
                "Basins"."BasinID" = {$_POST['BasinID']}) AS R
                INNER JOIN
            "$schema"."ReachData" USING ("ReachID")
                INNER JOIN
            (SELECT 
                "ReachID", MAX("Date") AS "Date"
            FROM
                "$schema"."ReachData"
            WHERE
                "EstTempC" IS NOT NULL
            GROUP BY "ReachID") AS latestEstimate ON latestEstimate."Date" = "$schema"."ReachData"."Date"
                AND latestEstimate."ReachID" = "$schema"."ReachData"."ReachID"
        OFFSET
            {$_POST['offset']}
        LIMIT
            {$_POST['row_count']};
        QUERY;
} else {
    $sql = <<<QUERY
        SELECT 
            "ReachData"."Date"::Date as "Date",
            "EstTempC",
            R."ReachID",
            "RiverID",
            "Name",
            "RKm",
            "geometry"
        FROM
            (SELECT 
                "ReachID",
                    "RiverID",
                    "Rivers"."Name" AS "Name",
                    "Reaches"."RKm" AS "RKm",
                    ST_ASGEOJSON("Reaches"."geometry") AS "geometry"
            FROM
                "$schema"."Rivers"
            INNER JOIN "$schema"."Basins" USING ("BasinID")
            INNER JOIN "$schema"."Reaches" USING ("RiverID")
            WHERE
                "Basins"."BasinID" = {$_POST['BasinID']}) AS R
                INNER JOIN
            "$schema"."ReachData" USING ("ReachID")
                INNER JOIN
            (SELECT 
                "ReachID", MAX("Date") AS "Date"
            FROM
                "$schema"."ReachData"
            WHERE
                "EstTempC" IS NOT NULL
            GROUP BY "ReachID") AS latestEstimate ON latestEstimate."Date" = "$schema"."ReachData"."Date"
                AND latestEstimate."ReachID" = "$schema"."ReachData"."ReachID"
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