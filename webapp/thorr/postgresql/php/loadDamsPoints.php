<?php

require_once('dbConfig.php');

$connStr = "host=$host port=$port dbname=$dbname user=$username password=$password";
$pgsql_connection = pg_connect($connStr);

// if ($mysqli_connection->connect_error) {
//     echo "Not connected, error: " . $mysqli_connection->connect_error;
// }

// echo ($_POST['row_count'] and $_POST['offset']);

if (isset($_POST['offset']) || isset($_POST['row_count'])) {
    echo "Offset and row count";
    $sql = <<<QUERY
        SELECT
            "DamData"."Date",
            ROUND("WaterTempC"::NUMERIC, 2) AS "WaterTempC",
            "DamData"."DamID",
            "RiverID",
            "Name",
            "geometry"
        FROM
            (
                SELECT
                    "DamID",
                    "RiverID",
                    "BasinID",
                    "Name",
                    "Reservoir",
                    ST_ASGEOJSON ("Dams"."DamGeometry") AS "geometry"
                FROM
                    "$schema"."Dams"
                WHERE
                    "BasinID" = {$_POST['BasinID']}
            ) AS D
            INNER JOIN "$schema"."DamData" USING ("DamID")
            INNER JOIN (
                SELECT
                    "DamID",
                    MAX("Date") AS "Date"
                FROM
                    "$schema"."DamData"
                WHERE
                    "WaterTempC" IS NOT NULL
                GROUP BY
                    "DamID"
            ) AS LATESTESTIMATE ON LATESTESTIMATE."Date" = "DamData"."Date"
            AND LATESTESTIMATE."DamID" = "DamData"."DamID"
        OFFSET
            {$_POST['offset']}
        LIMIT
            {$_POST['row_count']};
        QUERY;
} else {
    $sql = <<<QUERY
        SELECT
            "DamData"."Date",
            ROUND("WaterTempC"::NUMERIC, 2) AS "WaterTempC",
            "DamData"."DamID",
            "RiverID",
            "Name",
            "geometry"
        FROM
            (
                SELECT
                    "DamID",
                    "RiverID",
                    "BasinID",
                    "Name",
                    "Reservoir",
                    ST_ASGEOJSON ("Dams"."DamGeometry") AS "geometry"
                FROM
                    "$schema"."Dams"
                WHERE
                    "BasinID" = {$_POST['BasinID']}
            ) AS D
            INNER JOIN "$schema"."DamData" USING ("DamID")
            INNER JOIN (
                SELECT
                    "DamID",
                    MAX("Date") AS "Date"
                FROM
                    "$schema"."DamData"
                WHERE
                    "WaterTempC" IS NOT NULL
                GROUP BY
                    "DamID"
            ) AS LATESTESTIMATE ON LATESTESTIMATE."Date" = "DamData"."Date"
            AND LATESTESTIMATE."DamID" = "DamData"."DamID"
        QUERY;
};

// if ($_POST['offset'] || $_POST['row_count']) {
//     $sql = <<<QUERY
//             SELECT 
//             D.DamID,
//             Name,
//             Reservoir,
//             Value AS Temperature,
//             startDate AS startDate,
//             IF(DAY = 1,
//                 STR_TO_DATE(CONCAT(Year,
//                                 '-',
//                                 LPAD(Month, 2, '00'),
//                                 '-',
//                                 LPAD(14, 2, '00')),
//                         '%Y-%m-%d'),
//                 LAST_DAY(startDate)) AS endDate,
//             geometry
//         FROM
//             (SELECT 
//                 DamID,
//                     RiverID,
//                     BasinID,
//                     Name,
//                     Reservoir,
//                     ST_ASGEOJSON(Dams.DamGeometry) AS geometry
//             FROM
//                 thorr.Dams
//             WHERE
//                 BasinID = {$_POST['BasinID']}) AS D
//                 INNER JOIN
//             (SELECT 
//                 T.DamID, T.startDate, T.Day, T.Month, T.Value, T.Year
//             FROM
//                 (SELECT 
//                 DamLandsatWaterTemp.DamID AS DamID,
//                     STR_TO_DATE(CONCAT(YEAR(DamLandsatWaterTemp.date), '-', LPAD(MONTH(DamLandsatWaterTemp.date), 2, '00'), '-', LPAD(IF(DAY(DamLandsatWaterTemp.date) < 15, 1, 15), 2, '00')), '%Y-%m-%d') AS startDate,
//                     IF(DAY(DamLandsatWaterTemp.date) < 15, 1, 15) AS Day,
//                     MONTH(DamLandsatWaterTemp.date) AS Month,
//                     YEAR(DamLandsatWaterTemp.date) AS Year,
//                     ROUND(AVG(DamLandsatWaterTemp.value), 2) AS Value
//             FROM
//                 DamLandsatWaterTemp
//             GROUP BY Year , Month , Day , DamID , startDate) AS T
//             INNER JOIN (SELECT 
//                 DamID,
//                     MAX(STR_TO_DATE(CONCAT(YEAR(DamLandsatWaterTemp.date), '-', LPAD(MONTH(DamLandsatWaterTemp.date), 2, '00'), '-', LPAD(IF(DAY(DamLandsatWaterTemp.date) < 15, 1, 15), 2, '00')), '%Y-%m-%d')) AS startDate
//             FROM
//                 DamLandsatWaterTemp
//             GROUP BY DamID) AS latestEstimate ON latestEstimate.startDate = T.startDate
//                 AND latestEstimate.DamID = T.DamID) AS Q ON Q.DamID = D.DamID
//         LIMIT {$_POST['offset']}, {$_POST['row_count']};
//         QUERY;
// } else {
//     $sql = <<<QUERY
//             SELECT 
//             D.DamID,
//             Name,
//             Reservoir,
//             Value AS Temperature,
//             startDate AS startDate,
//             IF(DAY = 1,
//                 STR_TO_DATE(CONCAT(Year,
//                                 '-',
//                                 LPAD(Month, 2, '00'),
//                                 '-',
//                                 LPAD(14, 2, '00')),
//                         '%Y-%m-%d'),
//                 LAST_DAY(startDate)) AS endDate,
//             geometry
//         FROM
//             (SELECT 
//                 DamID,
//                     RiverID,
//                     BasinID,
//                     Name,
//                     Reservoir,
//                     ST_ASGEOJSON(Dams.DamGeometry) AS geometry
//             FROM
//                 thorr.Dams
//             WHERE
//                 BasinID = {$_POST['BasinID']}) AS D
//                 INNER JOIN
//             (SELECT 
//                 T.DamID, T.startDate, T.Day, T.Month, T.Value, T.Year
//             FROM
//                 (SELECT 
//                 DamLandsatWaterTemp.DamID AS DamID,
//                     STR_TO_DATE(CONCAT(YEAR(DamLandsatWaterTemp.date), '-', LPAD(MONTH(DamLandsatWaterTemp.date), 2, '00'), '-', LPAD(IF(DAY(DamLandsatWaterTemp.date) < 15, 1, 15), 2, '00')), '%Y-%m-%d') AS startDate,
//                     IF(DAY(DamLandsatWaterTemp.date) < 15, 1, 15) AS Day,
//                     MONTH(DamLandsatWaterTemp.date) AS Month,
//                     YEAR(DamLandsatWaterTemp.date) AS Year,
//                     ROUND(AVG(DamLandsatWaterTemp.value), 2) AS Value
//             FROM
//                 DamLandsatWaterTemp
//             GROUP BY Year , Month , Day , DamID , startDate) AS T
//             INNER JOIN (SELECT 
//                 DamID,
//                     MAX(STR_TO_DATE(CONCAT(YEAR(DamLandsatWaterTemp.date), '-', LPAD(MONTH(DamLandsatWaterTemp.date), 2, '00'), '-', LPAD(IF(DAY(DamLandsatWaterTemp.date) < 15, 1, 15), 2, '00')), '%Y-%m-%d')) AS startDate
//             FROM
//                 DamLandsatWaterTemp
//             GROUP BY DamID) AS latestEstimate ON latestEstimate.startDate = T.startDate
//                 AND latestEstimate.DamID = T.DamID) AS Q ON Q.DamID = D.DamID
//         QUERY;
// };



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
