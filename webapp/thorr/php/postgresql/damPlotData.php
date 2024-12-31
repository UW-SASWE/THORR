<?php

require_once('dbConfig.php');

$mysqli_connection = new MySQLi($host, $username, $password, $dbname, $port);

// if ($mysqli_connection->connect_error) {
//     echo "Not connected, error: " . $mysqli_connection->connect_error;
// }

// echo ($_POST['row_count'] and $_POST['offset']);

# Build JSON
$plotData = array(
    'waterTempDates' => array(),
    'waterTemp' => array(),
    'waterTempWDates' => array(),
    'waterTempW' => array(),
    'waterTempBWDates' => array(),
    'waterTempBW' => array(),
    'waterTempMDates' => array(),
    'waterTempM' => array(),
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
$waterTempQuery = <<<QUERY
SELECT 
    "Date" AS Date, "WaterTempC" AS WaterTemperature
FROM
    thorr."DamData"
WHERE
    "DamID" = {$_POST['DamID']} AND "WaterTempC" > 0
ORDER BY Date;
QUERY;

$result = $mysqli_connection->query($waterTempQuery);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['waterTempDates'], $row['Date']);
    array_push($plotData['waterTemp'], $row['WaterTemperature']);
}

// query for weekly water temperatures
$waterTempBWQuery = <<<QUERY
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
        ROUND(AVG("WaterTempC")::NUMERIC, 2) AS WaterTemperature
    FROM
        thorr."DamData"
    WHERE
        "DamID" = {$_POST['DamID']}
        AND "WaterTempC" > 0
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
        Date;
    QUERY;

$result = $mysqli_connection->query($waterTempBWQuery);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['waterTempBWDates'], $row['Date']);
    array_push($plotData['waterTempBW'], $row['WaterTemperature']);
}

// query for weekly water temperatures
$waterTempWQuery = <<<QUERY
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
        ROUND(AVG("WaterTempC")::numeric, 2) AS WaterTemperature
    FROM
        thorr."DamData"
    WHERE
        "DamID" = {$_POST['DamID']} AND "WaterTempC" > 0
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
    ORDER BY Date;
    QUERY;

$result = $mysqli_connection->query($waterTempWQuery);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['waterTempWDates'], $row['Date']);
    array_push($plotData['waterTempW'], $row['WaterTemperature']);
}

// query for weekly water temperatures
$waterTempMQuery = <<<QUERY
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
            ROUND(AVG("WaterTempC")::NUMERIC, 2) AS WaterTemperature
        FROM
            thorr."DamData"
        WHERE
            ("DamID" = {$_POST['DamID']})
            AND ("WaterTempC" > 0)
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
            Date;
    QUERY;

$result = $mysqli_connection->query($waterTempMQuery);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['waterTempMDates'], $row['Date']);
    array_push($plotData['waterTempM'], $row['WaterTemperature']);
}

// query for long term mean temperatures as is (not resampled)
$LTMQuery = <<<QUERY
SELECT 
    STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE),
                    '-',
                    LPAD(MONTH(Date), 2, '00'),
                    '-',
                    LPAD(DAY(Date), 2, '00')),
            '%Y-%m-%d') AS Date,
    ROUND(AVG(WaterTempC), 2) AS WaterTemperature
FROM
    DamData
WHERE
    DamID = {$_POST['DamID']} AND WaterTempC > 0
GROUP BY STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE),
            '-',
            LPAD(MONTH(Date), 2, '00'),
            '-',
            LPAD(DAY(Date), 2, '00')),
    '%Y-%m-%d')
ORDER BY Date;
QUERY;

$result = $mysqli_connection->query($LTMQuery);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['LTMDates'], $row['Date']);
    array_push($plotData['LTM'], $row['WaterTemperature']);
}

// query for long term mean temperatures (weekly)
$LTMWQuery = <<<QUERY
SELECT 
    DATE_ADD(STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE),
                        '-',
                        LPAD(01, 2, '00'),
                        '-',
                        LPAD(01, 2, '00')),
                '%Y-%m-%d'),
        INTERVAL (FLOOR(DAYOFYEAR(Date) / 7)) WEEK) AS Date,
    ROUND(AVG(WaterTempC), 2) AS WaterTemperature
FROM
    DamData
WHERE
    DamID = {$_POST['DamID']} AND WaterTempC > 0
GROUP BY DATE_ADD(STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE),
                    '-',
                    LPAD(01, 2, '00'),
                    '-',
                    LPAD(01, 2, '00')),
            '%Y-%m-%d'),
    INTERVAL (FLOOR(DAYOFYEAR(Date) / 7)) WEEK)
ORDER BY Date;
QUERY;

$result = $mysqli_connection->query($LTMWQuery);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['LTMWDates'], $row['Date']);
    array_push($plotData['LTMW'], $row['WaterTemperature']);
}

// query for long term mean temperatures (bi-weekly)
$LTMBWQuery = <<<QUERY
SELECT 
    DATE_ADD(STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE),
                        '-',
                        LPAD(01, 2, '00'),
                        '-',
                        LPAD(01, 2, '00')),
                '%Y-%m-%d'),
        INTERVAL (2 * FLOOR(DAYOFYEAR(Date) / 14)) WEEK) AS Date,
    ROUND(AVG(WaterTempC), 2) AS WaterTemperature
FROM
    DamData
WHERE
    DamID = {$_POST['DamID']} AND WaterTempC > 0
GROUP BY DATE_ADD(STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE),
                    '-',
                    LPAD(01, 2, '00'),
                    '-',
                    LPAD(01, 2, '00')),
            '%Y-%m-%d'),
    INTERVAL (2 * FLOOR(DAYOFYEAR(Date) / 14)) WEEK)
ORDER BY Date;
QUERY;

$result = $mysqli_connection->query($LTMBWQuery);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['LTMBWDates'], $row['Date']);
    array_push($plotData['LTMBW'], $row['WaterTemperature']);
}

// query for long term mean temperatures (monthly)
$LTMMQuery = <<<QUERY
SELECT 
    STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE),
                    '-',
                    LPAD(MONTH(Date), 2, '00'),
                    '-',
                    LPAD(01, 2, '00')),
            '%Y-%m-%d') AS Date,
    ROUND(AVG(WaterTempC), 2) AS WaterTemperature
FROM
    DamData
WHERE
    DamID = {$_POST['DamID']} AND WaterTempC > 0
GROUP BY STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE),
                '-',
                LPAD(MONTH(Date), 2, '00'),
                '-',
                LPAD(01, 2, '00')),
        '%Y-%m-%d')
ORDER BY Date;
QUERY;

$result = $mysqli_connection->query($LTMMQuery);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['LTMMDates'], $row['Date']);
    array_push($plotData['LTMM'], $row['WaterTemperature']);
}

// query for deviations (irregular)
$deviationQuery = <<<QUERY
SELECT 
    Est.Date AS Date,
    Round((Est.WaterTemperature - LTM.WaterTemperature), 2) AS Deviation
FROM
    (SELECT 
        Date AS Date, WaterTempC AS WaterTemperature
    FROM
        DamData
    WHERE
        DamID = {$_POST['DamID']} AND WaterTempC > 0) AS Est
        LEFT JOIN
    (SELECT 
        STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE), '-', LPAD(MONTH(Date), 2, '00'), '-', LPAD(DAY(Date), 2, '00')), '%Y-%m-%d') AS Date,
            ROUND(AVG(WaterTempC), 2) AS WaterTemperature
    FROM
        DamData
    WHERE
        DamID = {$_POST['DamID']} AND WaterTempC > 0
    GROUP BY STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE), '-', LPAD(MONTH(Date), 2, '00'), '-', LPAD(DAY(Date), 2, '00')), '%Y-%m-%d')) AS LTM ON (MONTH(LTM.Date) = MONTH(Est.Date) and Day(LTM.Date) = Day(Est.Date))
ORDER BY Est.Date;
QUERY;

$result = $mysqli_connection->query($deviationQuery);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['deviationDates'], $row['Date']);
    array_push($plotData['deviation'], $row['Deviation']);
}

// query for deviations (monthly)
$deviationMQuery = <<<QUERY
SELECT 
    Est.Date AS Date,
    Round((Est.WaterTemperature - LTM.WaterTemperature), 2) AS Deviation
FROM
    (SELECT 
        STR_TO_DATE(CONCAT(YEAR(Date),
                        '-',
                        LPAD(MONTH(Date), 2, '00'),
                        '-',
                        LPAD(01, 2, '00')),
                '%Y-%m-%d') AS Date,
        ROUND(AVG(WaterTempC), 2) AS WaterTemperature
    FROM
        DamData
    WHERE
        DamID = {$_POST['DamID']} AND WaterTempC > 0
    GROUP BY STR_TO_DATE(CONCAT(YEAR(Date),
                    '-',
                    LPAD(MONTH(Date), 2, '00'),
                    '-',
                    LPAD(01, 2, '00')),
            '%Y-%m-%d')) AS Est
        LEFT JOIN
    (SELECT 
    STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE),
                    '-',
                    LPAD(MONTH(Date), 2, '00'),
                    '-',
                    LPAD(01, 2, '00')),
            '%Y-%m-%d') AS Date,
    ROUND(AVG(WaterTempC), 2) AS WaterTemperature
FROM
    DamData
WHERE
    DamID = {$_POST['DamID']} AND WaterTempC > 0
GROUP BY STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE),
                '-',
                LPAD(MONTH(Date), 2, '00'),
                '-',
                LPAD(01, 2, '00')),
        '%Y-%m-%d')) AS LTM ON (MONTH(LTM.Date) = MONTH(Est.Date))
ORDER BY Est.Date;
QUERY;

$result = $mysqli_connection->query($deviationMQuery);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['deviationMDates'], $row['Date']);
    array_push($plotData['deviationM'], $row['Deviation']);
}

// query for deviations (monthly)
$deviationWQuery = <<<QUERY
SELECT 
    Est.Date AS Date,
    ROUND((Est.WaterTemperature - LTM.WaterTemperature),
            2) AS Deviation
FROM
    (SELECT 
        DATE_ADD(STR_TO_DATE(CONCAT(YEAR(Date), '-', LPAD(01, 2, '00'), '-', LPAD(01, 2, '00')), '%Y-%m-%d'), INTERVAL (FLOOR(DAYOFYEAR(Date) / 7)) WEEK) AS Date,
            ROUND(AVG(WaterTempC), 2) AS WaterTemperature,
            FLOOR(DAYOFYEAR(Date) / 7) AS week
    FROM
        DamData
    WHERE
        DamID = {$_POST['DamID']} AND WaterTempC > 0
    GROUP BY DATE_ADD(STR_TO_DATE(CONCAT(YEAR(Date), '-', LPAD(01, 2, '00'), '-', LPAD(01, 2, '00')), '%Y-%m-%d'), INTERVAL (FLOOR(DAYOFYEAR(Date) / 7)) WEEK)
        , FLOOR(DAYOFYEAR(Date) / 7)) AS Est
        LEFT JOIN
    (SELECT 
        DATE_ADD(STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE), '-', LPAD(01, 2, '00'), '-', LPAD(01, 2, '00')), '%Y-%m-%d'), INTERVAL (FLOOR(DAYOFYEAR(Date) / 7)) WEEK) AS Date,
            ROUND(AVG(WaterTempC), 2) AS WaterTemperature,
            FLOOR(DAYOFYEAR(Date) / 7) AS week
    FROM
        DamData
    WHERE
        DamID = {$_POST['DamID']} AND WaterTempC > 0
    GROUP BY DATE_ADD(STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE), '-', LPAD(01, 2, '00'), '-', LPAD(01, 2, '00')), '%Y-%m-%d'), INTERVAL (FLOOR(DAYOFYEAR(Date) / 7)) WEEK)
        , FLOOR(DAYOFYEAR(Date) / 7)) AS LTM ON (LTM.Week = Est.Week)
ORDER BY Est.Date;
QUERY;

$result = $mysqli_connection->query($deviationWQuery);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['deviationWDates'], $row['Date']);
    array_push($plotData['deviationW'], $row['Deviation']);
}

// query for deviations (monthly)
$deviationBWQuery = <<<QUERY
SELECT 
    Est.Date AS Date,
    ROUND((Est.WaterTemperature - LTM.WaterTemperature),
            2) AS Deviation
FROM
    (SELECT 
        DATE_ADD(STR_TO_DATE(CONCAT(YEAR(Date), '-', LPAD(01, 2, '00'), '-', LPAD(01, 2, '00')), '%Y-%m-%d'), INTERVAL (2 * (FLOOR(DAYOFYEAR(Date) / 14))) WEEK) AS Date,
            ROUND(AVG(WaterTempC), 2) AS WaterTemperature,
            (2 * (FLOOR(DAYOFYEAR(Date) / 14))) AS week
    FROM
        DamData
    WHERE
        DamID = {$_POST['DamID']} AND WaterTempC > 0
    GROUP BY DATE_ADD(STR_TO_DATE(CONCAT(YEAR(Date), '-', LPAD(01, 2, '00'), '-', LPAD(01, 2, '00')), '%Y-%m-%d'), INTERVAL (2 * (FLOOR(DAYOFYEAR(Date) / 14))) WEEK) , (2 * (FLOOR(DAYOFYEAR(Date) / 14)))) AS Est
        LEFT JOIN
    (SELECT 
        DATE_ADD(STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE), '-', LPAD(01, 2, '00'), '-', LPAD(01, 2, '00')), '%Y-%m-%d'), INTERVAL (2 * (FLOOR(DAYOFYEAR(Date) / 14))) WEEK) AS Date,
            ROUND(AVG(WaterTempC), 2) AS WaterTemperature,
            (2 * (FLOOR(DAYOFYEAR(Date) / 14))) AS week
    FROM
        DamData
    WHERE
        DamID = {$_POST['DamID']} AND WaterTempC > 0
    GROUP BY DATE_ADD(STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE), '-', LPAD(01, 2, '00'), '-', LPAD(01, 2, '00')), '%Y-%m-%d'), INTERVAL (2 * (FLOOR(DAYOFYEAR(Date) / 14))) WEEK) , (2 * (FLOOR(DAYOFYEAR(Date) / 14)))) AS LTM ON (LTM.Week = Est.Week)
ORDER BY Est.Date;
QUERY;

$result = $mysqli_connection->query($deviationBWQuery);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['deviationBWDates'], $row['Date']);
    array_push($plotData['deviationBW'], $row['Deviation']);
}

// header('Content-type: application/json');
echo json_encode($plotData, JSON_NUMERIC_CHECK);


$mysqli_connection->close();
