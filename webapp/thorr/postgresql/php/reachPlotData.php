<?php

require_once('dbConfig.php');

$connStr = "host=$host port=$port dbname=$dbname user=$username password=$password";
$pgsql_connection = pg_connect($connStr);

// if ($mysqli_connection->connect_error) {
//     echo "Not connected, error: " . $mysqli_connection->connect_error;
// }

// echo ($_POST['row_count'] and $_POST['offset']);

# Build JSON
$plotData = array(
    'estimatedTempDates' => array(),
    'estimatedTemp' => array(),
    'estimatedTempWDates' => array(),
    'estimatedTempW' => array(),
    'estimatedTempBWDates' => array(),
    'estimatedTempBW' => array(),
    'estimatedTempMDates' => array(),
    'estimatedTempM' => array(),
    'LTMDates' => array(),
    'LTM' => array(),
    'LTMWDates' => array(),
    'LTMW' => array(),
    'LTMBWDates' => array(),
    'LTMBW' => array(),
    'LTMMDates' => array(),
    'LTMM' => array(),
    'deviationDates' => array(),
    'deviation' => array(),
    'deviationWDates' => array(),
    'deviationW' => array(),
    'deviationBWDates' => array(),
    'deviationBW' => array(),
    'deviationMDates' => array(),
    'deviationM' => array(),
);
// query for water temperatures as is (not resampled)
$estimatedTempQuery = <<<QUERY
SELECT 
    "Date"::DATE AS "Date", "EstTempC" AS "WaterTemperature"
FROM
    "$schema"."ReachData"
WHERE
    "ReachID" = {$_POST['ReachID']} AND "EstTempC" > 0
ORDER BY "Date";
QUERY;

$result = pg_query($pgsql_connection, $estimatedTempQuery);

# Loop through rows to build feature arrays
while ($row = pg_fetch_assoc($result)) {

    array_push($plotData['estimatedTempDates'], $row['Date']);
    array_push($plotData['estimatedTemp'], $row['WaterTemperature']);
}

// query for weekly water temperatures
$estimatedTempBWQuery = <<<QUERY
    SELECT
        DATE_ADD (
            TO_DATE(
                CONCAT(
                    EXTRACT(
                        YEAR
                        FROM
                            "Date"
                    ),
                    '-',
                    LPAD('01', 2, '00'),
                    '-',
                    LPAD('01', 2, '00')
                ),
                'YYYY-MM-DD'
            ),
            CONCAT(
                2 * FLOOR(
                    EXTRACT(
                        DOY
                        FROM
                            "Date"
                    ) / 14
                ),
                ' week'
            )::INTERVAL
        )::DATE AS "Date",
        ROUND(AVG("EstTempC")::NUMERIC, 2) AS "WaterTemperature"
    FROM
        "$schema"."ReachData"
    WHERE
        "ReachID" = {$_POST['ReachID']}
        AND "EstTempC" > 0
    GROUP BY
        DATE_ADD (
            TO_DATE(
                CONCAT(
                    EXTRACT(
                        YEAR
                        FROM
                            "Date"
                    ),
                    '-',
                    LPAD('01', 2, '00'),
                    '-',
                    LPAD('01', 2, '00')
                ),
                'YYYY-MM-DD'
            ),
            CONCAT(
                2 * FLOOR(
                    EXTRACT(
                        DOY
                        FROM
                            "Date"
                    ) / 14
                ),
                ' week'
            )::INTERVAL
        )
    ORDER BY
        "Date";
    QUERY;

$result = pg_query($pgsql_connection, $estimatedTempBWQuery);

# Loop through rows to build feature arrays
while ($row = pg_fetch_assoc($result)) {

    array_push($plotData['estimatedTempBWDates'], $row['Date']);
    array_push($plotData['estimatedTempBW'], $row['WaterTemperature']);
}

// query for weekly water temperatures
$estimatedTempWQuery = <<<QUERY
    SELECT
        DATE_ADD (
            TO_DATE(
                CONCAT(
                    EXTRACT(
                        YEAR
                        FROM
                            "Date"
                    ),
                    '-',
                    LPAD('01', 2, '00'),
                    '-',
                    LPAD('01', 2, '00')
                ),
                'YYYY-MM-DD'
            ),
            CONCAT(
                FLOOR(
                    EXTRACT(
                        DOY
                        FROM
                            "Date"
                    ) / 7
                ),
                ' week'
            )::INTERVAL
        )::DATE AS "Date",
        ROUND(AVG("EstTempC")::numeric, 2) AS "WaterTemperature"
    FROM
        "$schema"."ReachData"
    WHERE
        "ReachID" = {$_POST['ReachID']} AND "EstTempC" > 0
    GROUP BY
        DATE_ADD (
            TO_DATE(
                CONCAT(
                    EXTRACT(
                        YEAR
                        FROM
                            "Date"
                    ),
                    '-',
                    LPAD('01', 2, '00'),
                    '-',
                    LPAD('01', 2, '00')
                ),
                'YYYY-MM-DD'
            ),
            CONCAT(
                FLOOR(
                    EXTRACT(
                        DOY
                        FROM
                            "Date"
                    ) / 7
                ),
                ' week'
            )::INTERVAL
        )
    ORDER BY "Date";
    QUERY;

$result = pg_query($pgsql_connection, $estimatedTempWQuery);

# Loop through rows to build feature arrays
while ($row = pg_fetch_assoc($result)) {

    array_push($plotData['estimatedTempWDates'], $row['Date']);
    array_push($plotData['estimatedTempW'], $row['WaterTemperature']);
}

// query for weekly water temperatures
$estimatedTempMQuery = <<<QUERY
    SELECT
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
                LPAD('01', 2, '00')
            ),
            'YYYY-MM-DD'
        )::DATE AS "Date",
        ROUND(AVG("EstTempC")::NUMERIC, 2) AS "WaterTemperature"
    FROM
        "$schema"."ReachData"
    WHERE
        ("ReachID" = {$_POST['ReachID']})
        AND ("EstTempC" > 0)
    GROUP BY
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
                LPAD('01', 2, '00')
            ),
            'YYYY-MM-DD'
        )
    ORDER BY
        "Date";
    QUERY;

$result = pg_query($pgsql_connection, $estimatedTempMQuery);

# Loop through rows to build feature arrays
while ($row = pg_fetch_assoc($result)) {

    array_push($plotData['estimatedTempMDates'], $row['Date']);
    array_push($plotData['estimatedTempM'], $row['WaterTemperature']);
}

// query for long term mean temperatures as is (not resampled)
$LTMQuery = <<<QUERY
SELECT
    TO_DATE(
        CONCAT(
            '2000-',
            EXTRACT(
                MONTH
                FROM
                    "Date"
            ),
            '-',
            EXTRACT(
                DAY
                FROM
                    "Date"
            )
        ),
        'YYYY-MM-DD'
    )::DATE AS "Date",
    ROUND(AVG("EstTempC")::NUMERIC, 2) AS "WaterTemperature"
FROM
    "$schema"."ReachData"
WHERE
    ("ReachID" = {$_POST['ReachID']})
    AND ("EstTempC" > 0)
GROUP BY
    TO_DATE(
        CONCAT(
            '2000-',
            EXTRACT(
                MONTH
                FROM
                    "Date"
            ),
            '-',
            EXTRACT(
                DAY
                FROM
                    "Date"
            )
        ),
        'YYYY-MM-DD'
    )
ORDER BY
    "Date";
QUERY;

$result = pg_query($pgsql_connection, $LTMQuery);

# Loop through rows to build feature arrays
while ($row = pg_fetch_assoc($result)) {

    array_push($plotData['LTMDates'], $row['Date']);
    array_push($plotData['LTM'], $row['WaterTemperature']);
}

// query for long term mean temperatures (weekly)
$LTMWQuery = <<<QUERY
SELECT
    DATE_ADD (
        TO_DATE(
            CONCAT(
                EXTRACT(
                    YEAR
                    FROM
                        CURRENT_DATE
                ),
                '-',
                LPAD('01', 2, '00'),
                '-',
                LPAD('01', 2, '00')
            ),
            'YYYY-MM-DD'
        ),
        CONCAT(
            FLOOR(
                EXTRACT(
                    DOY
                    FROM
                        "Date"
                ) / 7
            ),
            ' week'
        )::INTERVAL
    )::DATE AS "Date",
    ROUND(AVG("EstTempC")::numeric, 2) AS "WaterTemperature"
FROM
    "$schema"."ReachData"
WHERE
    "ReachID" = {$_POST['ReachID']} AND "EstTempC" IS NOT NULL
GROUP BY
    DATE_ADD (
        TO_DATE(
            CONCAT(
                EXTRACT(
                    YEAR
                    FROM
                        CURRENT_DATE
                ),
                '-',
                LPAD('01', 2, '00'),
                '-',
                LPAD('01', 2, '00')
            ),
            'YYYY-MM-DD'
        ),
        CONCAT(
            FLOOR(
                EXTRACT(
                    DOY
                    FROM
                        "Date"
                ) / 7
            ),
            ' week'
        )::INTERVAL
    )
ORDER BY "Date";
QUERY;

$result = pg_query($pgsql_connection, $LTMWQuery);

# Loop through rows to build feature arrays
while ($row = pg_fetch_assoc($result)) {

    array_push($plotData['LTMWDates'], $row['Date']);
    array_push($plotData['LTMW'], $row['WaterTemperature']);
}

// query for long term mean temperatures (bi-weekly)
$LTMBWQuery = <<<QUERY
SELECT
    DATE_ADD (
        TO_DATE(
            CONCAT(
                EXTRACT(
                    YEAR
                    FROM
                        CURRENT_DATE
                ),
                '-',
                LPAD('01', 2, '00'),
                '-',
                LPAD('01', 2, '00')
            ),
            'YYYY-MM-DD'
        ),
        CONCAT(
            2 * FLOOR(
                EXTRACT(
                    DOY
                    FROM
                        "Date"
                ) / 14
            ),
            ' week'
        )::INTERVAL
    )::DATE AS "Date",
    ROUND(AVG("EstTempC")::NUMERIC, 2) AS "WaterTemperature"
FROM
    "$schema"."ReachData"
WHERE
    "ReachID" = {$_POST['ReachID']}
    AND "EstTempC" IS NOT NULL
GROUP BY
    DATE_ADD (
        TO_DATE(
            CONCAT(
                EXTRACT(
                    YEAR
                    FROM
                        CURRENT_DATE
                ),
                '-',
                LPAD('01', 2, '00'),
                '-',
                LPAD('01', 2, '00')
            ),
            'YYYY-MM-DD'
        ),
        CONCAT(
            2 * FLOOR(
                EXTRACT(
                    DOY
                    FROM
                        "Date"
                ) / 14
            ),
            ' week'
        )::INTERVAL
    )
ORDER BY
    "Date";
QUERY;

$result = pg_query($pgsql_connection, $LTMBWQuery);

# Loop through rows to build feature arrays
while ($row = pg_fetch_assoc($result)) {

    array_push($plotData['LTMBWDates'], $row['Date']);
    array_push($plotData['LTMBW'], $row['WaterTemperature']);
}

// query for long term mean temperatures (monthly)
$LTMMQuery = <<<QUERY
SELECT
    TO_DATE(
        CONCAT(
            EXTRACT(
                YEAR
                FROM
                    CURRENT_DATE
            ),
            '-',
            EXTRACT(
                MONTH
                FROM
                    "Date"
            ),
            '-',
            LPAD('01', 2, '00')
        ),
        'YYYY-MM-DD'
    )::DATE AS "Date",
    ROUND(AVG("EstTempC")::NUMERIC, 2) AS "WaterTemperature"
FROM
    "$schema"."ReachData"
WHERE
    ("ReachID" = {$_POST['ReachID']})
    AND ("EstTempC" > 0)
GROUP BY
    TO_DATE(
        CONCAT(
            EXTRACT(
                YEAR
                FROM
                    CURRENT_DATE
            ),
            '-',
            EXTRACT(
                MONTH
                FROM
                    "Date"
            ),
            '-',
            LPAD('01', 2, '00')
        ),
        'YYYY-MM-DD'
    )
ORDER BY
    "Date";
QUERY;

$result = pg_query($pgsql_connection, $LTMMQuery);

# Loop through rows to build feature arrays
while ($row = pg_fetch_assoc($result)) {

    array_push($plotData['LTMMDates'], $row['Date']);
    array_push($plotData['LTMM'], $row['WaterTemperature']);
}

// query for deviations (irregular)
$deviationQuery = <<<QUERY
SELECT
    EST.Date::DATE AS "Date",
    ROUND((EST.WaterTemperature - LTM.WaterTemperature), 2) AS "Deviation"
FROM
    (
        SELECT
            "Date" AS Date,
            ROUND("EstTempC"::NUMERIC, 2) AS WaterTemperature
        FROM
            "$schema"."ReachData"
        WHERE
            "ReachID" = {$_POST['ReachID']}
            AND "EstTempC" IS NOT NULL
    ) AS EST
    LEFT JOIN (
        SELECT
            TO_DATE(
                CONCAT(
                    '2000-',
                    EXTRACT(
                        MONTH
                        FROM
                            "Date"
                    ),
                    '-',
                    EXTRACT(
                        DAY
                        FROM
                            "Date"
                    )
                ),
                'YYYY-MM-DD'
            ) AS Date,
            ROUND(AVG("EstTempC")::NUMERIC, 2) AS WaterTemperature
        FROM
            "$schema"."ReachData"
        WHERE
            ("ReachID" = {$_POST['ReachID']})
            AND ("EstTempC" IS NOT NULL)
        GROUP BY
            TO_DATE(
                CONCAT(
                    '2000-',
                    EXTRACT(
                        MONTH
                        FROM
                            "Date"
                    ),
                    '-',
                    EXTRACT(
                        DAY
                        FROM
                            "Date"
                    )
                ),
                'YYYY-MM-DD'
            )
    ) AS LTM ON (
        EXTRACT(
            MONTH
            FROM
                LTM.Date
        ) = EXTRACT(
            MONTH
            FROM
                EST.Date
        )
        AND EXTRACT(
            DOY
            FROM
                LTM.Date
        ) = EXTRACT(
            DOY
            FROM
                EST.Date
        )
    )
ORDER BY
    "Date";
QUERY;

$result = pg_query($pgsql_connection, $deviationQuery);

# Loop through rows to build feature arrays
while ($row = pg_fetch_assoc($result)) {

    array_push($plotData['deviationDates'], $row['Date']);
    array_push($plotData['deviation'], $row['Deviation']);
}

// query for deviations (monthly)
$deviationMQuery = <<<QUERY
SELECT 
    Est.Date::DATE AS "Date",
    Round((Est.WaterTemperature - LTM.WaterTemperature), 2) AS "Deviation"
FROM
    (
        SELECT
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
                    LPAD('01', 2, '00')
                ),
                'YYYY-MM-DD'
            ) AS Date,
            ROUND(AVG("EstTempC")::NUMERIC, 2) AS WaterTemperature
        FROM
            "$schema"."ReachData"
        WHERE
            ("ReachID" = {$_POST['ReachID']})
            AND ("EstTempC" IS NOT NULL)
        GROUP BY
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
                    LPAD('01', 2, '00')
                ),
                'YYYY-MM-DD'
            )) AS Est
                LEFT JOIN
            (SELECT
            TO_DATE(
                CONCAT(
                    EXTRACT(
                        YEAR
                        FROM
                            CURRENT_DATE
                    ),
                    '-',
                    EXTRACT(
                        MONTH
                        FROM
                            "Date"
                    ),
                    '-',
                    LPAD('01', 2, '00')
                ),
                'YYYY-MM-DD'
            ) AS Date,
            ROUND(AVG("EstTempC")::NUMERIC, 2) AS WaterTemperature
        FROM
            "$schema"."ReachData"
        WHERE
            ("ReachID" = {$_POST['ReachID']})
            AND ("EstTempC" IS NOT NULL)
        GROUP BY
            TO_DATE(
                CONCAT(
                    EXTRACT(
                        YEAR
                        FROM
                            CURRENT_DATE
                    ),
                    '-',
                    EXTRACT(
                        MONTH
                        FROM
                            "Date"
                    ),
                    '-',
                    LPAD('01', 2, '00')
                ),
                'YYYY-MM-DD'
            )) AS LTM ON (EXTRACT(
                        MONTH
                        FROM
                            LTM.Date) = EXTRACT(
                        MONTH
                        FROM
                            Est.Date))
ORDER BY 
    "Date";
QUERY;

$result = pg_query($pgsql_connection, $deviationMQuery);

# Loop through rows to build feature arrays
while ($row = pg_fetch_assoc($result)) {

    array_push($plotData['deviationMDates'], $row['Date']);
    array_push($plotData['deviationM'], $row['Deviation']);
}

// query for deviations (monthly)
$deviationWQuery = <<<QUERY
SELECT
    EST.Date::DATE AS "Date",
    ROUND((EST.WaterTemperature - LTM.WaterTemperature), 2) AS "Deviation"
FROM
    (
        SELECT
            DATE_ADD (
                TO_DATE(
                    CONCAT(
                        EXTRACT(
                            YEAR
                            FROM
                                "Date"
                        ),
                        '-',
                        LPAD('01', 2, '00'),
                        '-',
                        LPAD('01', 2, '00')
                    ),
                    'YYYY-MM-DD'
                ),
                CONCAT(
                    FLOOR(
                        EXTRACT(
                            DOY
                            FROM
                                "Date"
                        ) / 7
                    ),
                    ' week'
                )::INTERVAL
            ) AS Date,
            ROUND(AVG("EstTempC")::NUMERIC, 2) AS WaterTemperature,
            FLOOR(
                EXTRACT(
                    DOY
                    FROM
                        "Date"
                ) / 7
            ) AS week
        FROM
            "$schema"."ReachData"
        WHERE
            "ReachID" = {$_POST['ReachID']}
            AND "EstTempC" IS NOT NULL
        GROUP BY
            DATE_ADD (
                TO_DATE(
                    CONCAT(
                        EXTRACT(
                            YEAR
                            FROM
                                "Date"
                        ),
                        '-',
                        LPAD('01', 2, '00'),
                        '-',
                        LPAD('01', 2, '00')
                    ),
                    'YYYY-MM-DD'
                ),
                CONCAT(
                    FLOOR(
                        EXTRACT(
                            DOY
                            FROM
                                "Date"
                        ) / 7
                    ),
                    ' week'
                )::INTERVAL
            ),
            FLOOR(
                EXTRACT(
                    DOY
                    FROM
                        "Date"
                ) / 7
            )
        ORDER BY
            Date
    ) AS EST
    LEFT JOIN (
        SELECT
            DATE_ADD (
                TO_DATE(
                    CONCAT(
                        EXTRACT(
                            YEAR
                            FROM
                                CURRENT_DATE
                        ),
                        '-',
                        LPAD('01', 2, '00'),
                        '-',
                        LPAD('01', 2, '00')
                    ),
                    'YYYY-MM-DD'
                ),
                CONCAT(
                    FLOOR(
                        EXTRACT(
                            DOY
                            FROM
                                "Date"
                        ) / 7
                    ),
                    ' week'
                )::INTERVAL
            ) AS DATE,
            ROUND(AVG("EstTempC")::NUMERIC, 2) AS WaterTemperature,
            FLOOR(
                EXTRACT(
                    DOY
                    FROM
                        "Date"
                ) / 7
            ) AS week
        FROM
            "$schema"."ReachData"
        WHERE
            "ReachID" = {$_POST['ReachID']}
            AND "EstTempC" IS NOT NULL
        GROUP BY
            DATE_ADD (
                TO_DATE(
                    CONCAT(
                        EXTRACT(
                            YEAR
                            FROM
                                CURRENT_DATE
                        ),
                        '-',
                        LPAD('01', 2, '00'),
                        '-',
                        LPAD('01', 2, '00')
                    ),
                    'YYYY-MM-DD'
                ),
                CONCAT(
                    FLOOR(
                        EXTRACT(
                            DOY
                            FROM
                                "Date"
                        ) / 7
                    ),
                    ' week'
                )::INTERVAL
            ),
            FLOOR(
                EXTRACT(
                    DOY
                    FROM
                        "Date"
                ) / 7
            )
        ORDER BY
            Date
    ) AS LTM ON (LTM.week = EST.week)
ORDER BY
    "Date";
QUERY;

$result = pg_query($pgsql_connection, $deviationWQuery);

# Loop through rows to build feature arrays
while ($row = pg_fetch_assoc($result)) {

    array_push($plotData['deviationWDates'], $row['Date']);
    array_push($plotData['deviationW'], $row['Deviation']);
}

// query for deviations (monthly)
$deviationBWQuery = <<<QUERY
SELECT
    EST.Date::DATE AS "Date",
    ROUND((EST.WaterTemperature - LTM.WaterTemperature), 2) AS "Deviation"
FROM
    (
        SELECT
            DATE_ADD (
                TO_DATE(
                    CONCAT(
                        EXTRACT(
                            YEAR
                            FROM
                                "Date"
                        ),
                        '-',
                        LPAD('01', 2, '00'),
                        '-',
                        LPAD('01', 2, '00')
                    ),
                    'YYYY-MM-DD'
                ),
                CONCAT(
                    2 * FLOOR(
                        EXTRACT(
                            DOY
                            FROM
                                "Date"
                        ) / 14
                    ),
                    ' week'
                )::INTERVAL
            ) AS Date,
            ROUND(AVG("EstTempC")::NUMERIC, 2) AS WaterTemperature,
            2 * FLOOR(
                EXTRACT(
                    DOY
                    FROM
                        "Date"
                ) / 14
            ) AS week
        FROM
            "$schema"."ReachData"
        WHERE
            "ReachID" = {$_POST['ReachID']}
            AND "EstTempC" IS NOT NULL
        GROUP BY
            DATE_ADD (
                TO_DATE(
                    CONCAT(
                        EXTRACT(
                            YEAR
                            FROM
                                "Date"
                        ),
                        '-',
                        LPAD('01', 2, '00'),
                        '-',
                        LPAD('01', 2, '00')
                    ),
                    'YYYY-MM-DD'
                ),
                CONCAT(
                    2 * FLOOR(
                        EXTRACT(
                            DOY
                            FROM
                                "Date"
                        ) / 14
                    ),
                    ' week'
                )::INTERVAL
            ),
            2 * FLOOR(
                EXTRACT(
                    DOY
                    FROM
                        "Date"
                ) / 14
            )
        ORDER BY
            Date
    ) AS EST
    LEFT JOIN (
        SELECT
            DATE_ADD (
                TO_DATE(
                    CONCAT(
                        EXTRACT(
                            YEAR
                            FROM
                                CURRENT_DATE
                        ),
                        '-',
                        LPAD('01', 2, '00'),
                        '-',
                        LPAD('01', 2, '00')
                    ),
                    'YYYY-MM-DD'
                ),
                CONCAT(
                    2 * FLOOR(
                        EXTRACT(
                            DOY
                            FROM
                                "Date"
                        ) / 14
                    ),
                    ' week'
                )::INTERVAL
            ) AS DATE,
            ROUND(AVG("EstTempC")::NUMERIC, 2) AS WaterTemperature,
            2 * FLOOR(
                EXTRACT(
                    DOY
                    FROM
                        "Date"
                ) / 14
            ) AS week
        FROM
            "$schema"."ReachData"
        WHERE
            "ReachID" = {$_POST['ReachID']}
            AND "EstTempC" IS NOT NULL
        GROUP BY
            DATE_ADD (
                TO_DATE(
                    CONCAT(
                        EXTRACT(
                            YEAR
                            FROM
                                CURRENT_DATE
                        ),
                        '-',
                        LPAD('01', 2, '00'),
                        '-',
                        LPAD('01', 2, '00')
                    ),
                    'YYYY-MM-DD'
                ),
                CONCAT(
                    2 * FLOOR(
                        EXTRACT(
                            DOY
                            FROM
                                "Date"
                        ) / 14
                    ),
                    ' week'
                )::INTERVAL
            ),
            2 * FLOOR(
                EXTRACT(
                    DOY
                    FROM
                        "Date"
                ) / 14
            )
        ORDER BY
            Date
    ) AS LTM ON (LTM.week = EST.week)
ORDER BY
    "Date";
QUERY;

$result = pg_query($pgsql_connection, $deviationBWQuery);

# Loop through rows to build feature arrays
while ($row = pg_fetch_assoc($result)) {

    array_push($plotData['deviationBWDates'], $row['Date']);
    array_push($plotData['deviationBW'], $row['Deviation']);
}

// header('Content-type: application/json');
echo json_encode($plotData, JSON_NUMERIC_CHECK);


pg_close($pgsql_connection);
