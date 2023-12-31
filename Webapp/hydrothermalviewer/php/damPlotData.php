<?php

require_once('dbConfig.php');

$mysqli_connection = new MySQLi($host, $username, $password, $dbname, $port);

// if ($mysqli_connection->connect_error) {
//     echo "Not connected, error: " . $mysqli_connection->connect_error;
// }

// echo ($_POST['row_count'] and $_POST['offset']);

# Build JSON
$plotData = array(
    'landsatTempSMDates' => array(),
    'landsatTempSMTemp'  => array(),
    'landsatTempMDates'  => array(),
    'landsatTempMTemp'   => array(),
    'landsatLTMMMonth' => array(),
    'landsatLTMM' => array(),
    'landsatLTMM5' => array(),
    'landsatLTMM95' => array(),
    'landsatLTMSMMonth' => array(),
    'landsatLTMSMDay' => array(),
    'landsatLTMSM' => array(),
    'landsatLTMSM5' => array(),
    'landsatLTMSM95' => array(),
    'deviationMDate' => array(),
    'deviationMDeviation' => array(),
    'deviationSMDate' => array(),
    'deviationSMDeviation' => array(),
    'estimatedTempSMDate' => array(),
    'estimatedTempSM' => array(),
    'estimatedTempMDate' => array(),
    'estimatedTempM' => array(),
);


// query for actual landsat observations semi-monthly
$landsatTempQuerySM = <<<QUERY
    SELECT 
        STR_TO_DATE(CONCAT(Year,
                        '-',
                        LPAD(Month, 2, '00'),
                        '-',
                        LPAD(DayOfMonth, 2, '00')),
                '%Y-%m-%d') AS Date,
        ROUND(WaterTemp, 2) AS watertemp
    FROM
        (SELECT 
            IF(DAY(DamLandsatWaterTemp.date) < 15, 1, 15) AS DayOfMonth,
                MONTH(DamLandsatWaterTemp.date) AS Month,
                YEAR(DamLandsatWaterTemp.date) AS Year,
                AVG(DamLandsatWaterTemp.Value) AS WaterTemp
        FROM
            DamLandsatWaterTemp
        WHERE
            DamID = {$_POST['DamID']}
                AND DamLandsatWaterTemp.Value > 0
        GROUP BY DayOfMonth , Month , Year , DamID) AS T
    ORDER BY Date;
    QUERY;

// echo $landsatTempQuerySM;

$result = $mysqli_connection->query($landsatTempQuerySM);


# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {
    # Add feature arrays to feature collection array

    array_push($plotData['landsatTempSMDates'], $row['Date']);
    array_push($plotData['landsatTempSMTemp'], $row['watertemp']);
}

// query for actual landsat observations monthly
$landsatTempQueryM = <<<QUERY
    SELECT 
    STR_TO_DATE(CONCAT(Year,
                    '-',
                    LPAD(Month, 2, '00'),
                    '-',
                    LPAD(DayOfMonth, 2, '00')),
            '%Y-%m-%d') AS Date,
    ROUND(WaterTemp, 2) AS watertemp
    FROM
    (SELECT 
        1 AS DayOfMonth,
            MONTH(DamLandsatWaterTemp.date) AS Month,
            YEAR(DamLandsatWaterTemp.date) AS Year,
            AVG(DamLandsatWaterTemp.Value) AS WaterTemp
    FROM
        DamLandsatWaterTemp
    WHERE
        DamID = {$_POST['DamID']}
            AND DamLandsatWaterTemp.Value > 0
    GROUP BY DayOfMonth , Month , Year , DamID) AS T
    ORDER BY Date;
    QUERY;

// echo $landsatTempQueryM;

$result = $mysqli_connection->query($landsatTempQueryM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {
    # Add feature arrays to feature collection array

    array_push($plotData['landsatTempMDates'], $row['Date']);
    array_push($plotData['landsatTempMTemp'], $row['watertemp']);
}

// query for actual landsat observations monthly
$landsatLTMQueryM = <<<QUERY
    SELECT 
        MONTH(Date) AS Month,
        DamID,
        ROUND(AVG(VALUE), 2) AS WaterTemperature
    FROM
        DamLandsatWaterTemp
    WHERE
        DamID = {$_POST['DamID']} AND Date < CURRENT_DATE()
            AND Date > DATE_SUB(CURRENT_DATE(),
            INTERVAL 30 YEAR)
    GROUP BY Month , DamID
    ORDER BY DamID , Month;
    QUERY;

// echo $landsatTempQueryM;

$result = $mysqli_connection->query($landsatLTMQueryM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {
    # Add feature arrays to feature collection array

    array_push($plotData['landsatLTMMMonth'], $row['Month']);
    array_push($plotData['landsatLTMM'], $row['WaterTemperature']);
    // array_push($plotData['landsatLTMM5'], $row['WaterTemperature5']);
    // array_push($plotData['landsatLTMM95'], $row['WaterTemperature95']);
}

// query for actual landsat observations monthly
$landsatLTMQuerySM = <<<QUERY
    SELECT 
        MONTH(DATE) + IF(DAY(DATE) = 1, 0, 0.5) AS Month,
        DamID,
        ROUND(AVG(VALUE), 2) AS WaterTemperature
    FROM
        DamLandsatWaterTemp
    WHERE
        DamID = {$_POST['DamID']} AND Date < CURRENT_DATE()
            AND Date > DATE_SUB(CURRENT_DATE(),
            INTERVAL 30 YEAR)
    GROUP BY Month , DamID
    ORDER BY DamID , Month
    QUERY;

// echo $landsatLTMQuerySM;

$result = $mysqli_connection->query($landsatLTMQuerySM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {
    # Add feature arrays to feature collection array

    array_push($plotData['landsatLTMSMMonth'], $row['Month']);
    // array_push($plotData['landsatLTMSMDay'], $row['DayOfMonth']);
    array_push($plotData['landsatLTMSM'], $row['WaterTemperature']);
    // array_push($plotData['landsatLTMSM5'], $row['WaterTemperature5']);
    // array_push($plotData['landsatLTMSM95'], $row['WaterTemperature95']);
}

// query for monthly deviations
$deviationQueryM = <<<QUERY
    SELECT 
        STR_TO_DATE(CONCAT(Year,
                        '-',
                        LPAD(T.Month, 2, '00'),
                        '-',
                        LPAD(T.DayOfMonth, 2, '00')),
                '%Y-%m-%d') AS Date,
        ROUND(LTM.Value - T.Value, 2) AS Deviation
    FROM
        (SELECT 
            YEAR(Date) AS Year,
                AVG(VALUE) AS Value,
                1 AS DayOfMonth,
                DamID,
                MONTH(Date) AS Month
        FROM
            DamLandsatWaterTemp
        GROUP BY Year , DayOfMonth , DamID , Month) AS T
            INNER JOIN
        (SELECT 
            1 AS DayOfMonth,
                MONTH(DATE) AS Month,
                DamID,
                ROUND(AVG(VALUE), 2) AS Value
        FROM
            DamLandsatWaterTemp
        WHERE
            DamID = {$_POST['DamID']}
        GROUP BY Month , DamID , DayOfMonth
        ORDER BY DamID , Month , DayOfMonth) AS LTM ON (T.DamID = LTM.DamID
            AND T.Month = LTM.Month
            AND T.DayOfMonth = LTM.DayOfMonth)
    WHERE
        T.DamID = {$_POST['DamID']}
    ORDER BY Date;
    QUERY;

// echo $landsatLTMQuerySM;i

$result = $mysqli_connection->query($deviationQueryM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {
    # Add feature arrays to feature collection array

    array_push($plotData['deviationMDate'], $row['Date']);
    array_push($plotData['deviationMDeviation'], $row['Deviation']);
}

// query for semi-monthly deviations
$deviationQuerySM = <<<QUERY
    SELECT 
        STR_TO_DATE(CONCAT(Year,
                        '-',
                        LPAD(T.Month, 2, '00'),
                        '-',
                        LPAD(T.DayOfMonth, 2, '00')),
                '%Y-%m-%d') AS Date,
        ROUND(LTM.Value - T.Value, 2) AS Deviation
    FROM
        (SELECT 
            YEAR(Date) AS Year,
                AVG(VALUE) AS Value,
                IF(DAY(Date) < 15, 1, 15) AS DayOfMonth,
                DamID,
                MONTH(Date) AS Month
        FROM
            DamLandsatWaterTemp
        GROUP BY Year , DayOfMonth , DamID , Month) AS T
            INNER JOIN
        (SELECT 
            IF(DAY(Date) < 15, 1, 15) AS DayOfMonth,
                MONTH(DATE) AS Month,
                DamID,
                ROUND(AVG(VALUE), 2) AS Value
        FROM
            DamLandsatWaterTemp
        WHERE
            DamID = {$_POST['DamID']}
        GROUP BY Month , DamID , DayOfMonth
        ORDER BY DamID , Month , DayOfMonth) AS LTM ON (T.DamID = LTM.DamID
            AND T.Month = LTM.Month
            AND T.DayOfMonth = LTM.DayOfMonth)
    WHERE
        T.DamID = {$_POST['DamID']}
    ORDER BY Date;
    QUERY;

// echo $landsatLTMQuerySM;i

$result = $mysqli_connection->query($deviationQuerySM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {
    # Add feature arrays to feature collection array

    array_push($plotData['deviationSMDate'], $row['Date']);
    array_push($plotData['deviationSMDeviation'], $row['Deviation']);
}

// // query for semi-monthly estimated temperatures
// $estimatedTempQuerySM = <<<QUERY
//     SELECT
//         Date,
//         ROUND(Value, 2) as WaterTemperature
//     FROM
//         ReachEstimatedWaterTemp
//     WHERE ReachEstimatedWaterTemp.ReachID = {$_POST['ReachID']} AND ReachEstimatedWaterTemp.Tag = 'SM'
//     ORDER BY Date;
//     QUERY;

// // echo $landsatLTMQuerySM;i

// $result = $mysqli_connection->query($estimatedTempQuerySM);

// # Loop through rows to build feature arrays
// while ($row = $result->fetch_assoc()) {

//     array_push($plotData['estimatedTempSMDate'], $row['Date']);
//     array_push($plotData['estimatedTempSM'], $row['WaterTemperature']);
// }

// // query for monthly estimated temperatures
// $estimatedTempQueryM = <<<QUERY
//     SELECT
//         Date,
//         ROUND(Value, 2) as WaterTemperature
//     FROM
//         ReachEstimatedWaterTemp
//     WHERE ReachEstimatedWaterTemp.ReachID = {$_POST['ReachID']} AND ReachEstimatedWaterTemp.Tag = 'M'
//     ORDER BY Date;
//     QUERY;

// // echo $landsatLTMQuerySM;i

// $result = $mysqli_connection->query($estimatedTempQueryM);

// # Loop through rows to build feature arrays
// while ($row = $result->fetch_assoc()) {

//     array_push($plotData['estimatedTempMDate'], $row['Date']);
//     array_push($plotData['estimatedTempM'], $row['WaterTemperature']);
// }



// // header('Content-type: application/json');
echo json_encode($plotData, JSON_NUMERIC_CHECK);


$mysqli_connection->close();
