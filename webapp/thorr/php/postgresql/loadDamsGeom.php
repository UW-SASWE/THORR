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
            D."DamID",
            "Name",
            "Reservoir",
            "Value" AS "Temperature",
            "startDate" AS "startDate",
            CASE
                WHEN "Day" < 15 THEN TO_DATE(
                    CONCAT("Year", '-', "Month", '-', 14),
                    'YYYY-MM-DD'
                )
                ELSE (
                    DATE_TRUNC('month', "startDate"::DATE) + INTERVAL '1 month' - INTERVAL '1 day'
                )::DATE
            END AS "endDate",
            "geometry"
        FROM
            (
                SELECT
                    "DamID",
                    "RiverID",
                    "BasinID",
                    "Name",
                    "Reservoir",
                    ST_ASGEOJSON ("Dams"."ReservoirGeometry") AS "geometry"
                FROM
                    "$schema"."Dams"
                WHERE
                    "BasinID" = {$_POST['BasinID']}
            ) AS D
            INNER JOIN (
                SELECT
                    T."DamID",
                    T."startDate",
                    T."Day",
                    T."Month",
                    T."Value",
                    T."Year"
                FROM
                    (
                        SELECT
                            "DamID",
                            -- STR_TO_DATE(CONCAT(YEAR(DamLandsatWaterTemp.date), '-', LPAD(MONTH(DamLandsatWaterTemp.date), 2, '00'), '-', LPAD(IF(DAY(DamLandsatWaterTemp.date) < 15, 1, 15), 2, '00')), '%Y-%m-%d') AS startDate,
                            TO_DATE(
                                CONCAT(
                                    EXTRACT(
                                        YEAR
                                        FROM
                                            "Date"
                                    ),
                                    '-',
                                    EXTRACT(
                                        MONTH
                                        FROM
                                            "Date"
                                    ),
                                    '-',
                                    CASE
                                        WHEN EXTRACT(
                                            DAY
                                            FROM
                                                "Date"
                                        ) < 15 THEN 1
                                        ELSE 15
                                    END
                                ),
                                'YYYY-MM-DD'
                            ) AS "startDate",
                            CASE
                                WHEN EXTRACT(
                                    DAY
                                    FROM
                                        "Date"
                                ) < 15 THEN 1
                                ELSE 15
                            END AS "Day",
                            EXTRACT(
                                MONTH
                                FROM
                                    "Date"
                            ) AS "Month",
                            EXTRACT(
                                YEAR
                                FROM
                                    "Date"
                            ) AS "Year",
                            ROUND(AVG("WaterTempC")::NUMERIC, 2) AS "Value"
                        FROM
                            "$schema"."DamData"
                        GROUP BY
                            "Year",
                            "Month",
                            "Day",
                            "DamID",
                            "startDate"
                    ) AS T
                    INNER JOIN (
                        SELECT
                            "DamID",
                            MAX(
                                TO_DATE(
                                    CONCAT(
                                        EXTRACT(
                                            YEAR
                                            FROM
                                                "Date"
                                        ),
                                        '-',
                                        EXTRACT(
                                            MONTH
                                            FROM
                                                "Date"
                                        ),
                                        '-',
                                        CASE
                                            WHEN EXTRACT(
                                                DAY
                                                FROM
                                                    "Date"
                                            ) < 15 THEN 1
                                            ELSE 15
                                        END
                                    ),
                                    'YYYY-MM-DD'
                                )
                            ) AS "startDate"
                        FROM
                            "$schema"."DamData"
                        GROUP BY
                            "DamID"
                    ) AS LATESTESTIMATE ON LATESTESTIMATE."startDate" = T."startDate"
                    AND LATESTESTIMATE."DamID" = T."DamID"
            ) AS Q ON Q."DamID" = D."DamID"
        OFFSET
            {$_POST['offset']}
        LIMIT
            {$_POST['row_count']};
        QUERY;
} else {
    $sql = <<<QUERY
        SELECT
            D."DamID",
            "Name",
            "Reservoir",
            "Value" AS "Temperature",
            "startDate" AS "startDate",
            CASE
                WHEN "Day" < 15 THEN TO_DATE(
                    CONCAT("Year", '-', "Month", '-', 14),
                    'YYYY-MM-DD'
                )
                ELSE (
                    DATE_TRUNC('month', "startDate"::DATE) + INTERVAL '1 month' - INTERVAL '1 day'
                )::DATE
            END AS "endDate",
            "geometry"
        FROM
            (
                SELECT
                    "DamID",
                    "RiverID",
                    "BasinID",
                    "Name",
                    "Reservoir",
                    ST_ASGEOJSON ("Dams"."ReservoirGeometry") AS "geometry"
                FROM
                    "$schema"."Dams"
                WHERE
                    "BasinID" = {$_POST['BasinID']}
            ) AS D
            INNER JOIN (
                SELECT
                    T."DamID",
                    T."startDate",
                    T."Day",
                    T."Month",
                    T."Value",
                    T."Year"
                FROM
                    (
                        SELECT
                            "DamID",
                            -- STR_TO_DATE(CONCAT(YEAR(DamLandsatWaterTemp.date), '-', LPAD(MONTH(DamLandsatWaterTemp.date), 2, '00'), '-', LPAD(IF(DAY(DamLandsatWaterTemp.date) < 15, 1, 15), 2, '00')), '%Y-%m-%d') AS startDate,
                            TO_DATE(
                                CONCAT(
                                    EXTRACT(
                                        YEAR
                                        FROM
                                            "Date"
                                    ),
                                    '-',
                                    EXTRACT(
                                        MONTH
                                        FROM
                                            "Date"
                                    ),
                                    '-',
                                    CASE
                                        WHEN EXTRACT(
                                            DAY
                                            FROM
                                                "Date"
                                        ) < 15 THEN 1
                                        ELSE 15
                                    END
                                ),
                                'YYYY-MM-DD'
                            ) AS "startDate",
                            CASE
                                WHEN EXTRACT(
                                    DAY
                                    FROM
                                        "Date"
                                ) < 15 THEN 1
                                ELSE 15
                            END AS "Day",
                            EXTRACT(
                                MONTH
                                FROM
                                    "Date"
                            ) AS "Month",
                            EXTRACT(
                                YEAR
                                FROM
                                    "Date"
                            ) AS "Year",
                            ROUND(AVG("WaterTempC")::NUMERIC, 2) AS "Value"
                        FROM
                            "$schema"."DamData"
                        GROUP BY
                            "Year",
                            "Month",
                            "Day",
                            "DamID",
                            "startDate"
                    ) AS T
                    INNER JOIN (
                        SELECT
                            "DamID",
                            MAX(
                                TO_DATE(
                                    CONCAT(
                                        EXTRACT(
                                            YEAR
                                            FROM
                                                "Date"
                                        ),
                                        '-',
                                        EXTRACT(
                                            MONTH
                                            FROM
                                                "Date"
                                        ),
                                        '-',
                                        CASE
                                            WHEN EXTRACT(
                                                DAY
                                                FROM
                                                    "Date"
                                            ) < 15 THEN 1
                                            ELSE 15
                                        END
                                    ),
                                    'YYYY-MM-DD'
                                )
                            ) AS "startDate"
                        FROM
                            "$schema"."DamData"
                        GROUP BY
                            "DamID"
                    ) AS LATESTESTIMATE ON LATESTESTIMATE."startDate" = T."startDate"
                    AND LATESTESTIMATE."DamID" = T."DamID"
            ) AS Q ON Q."DamID" = D."DamID"
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
