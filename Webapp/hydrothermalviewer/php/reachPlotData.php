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
    'estimatedTempSMDates' => array(),
    'estimatedTempSM' => array(),
    'estimatedTempMDates' => array(),
    'estimatedTempM' => array(),
    'estimatedLTMMMonth' => array(),
    'estimatedLTMM' => array(),
    'estimatedLTMM5' => array(),
    'estimatedLTMM95' => array(),
    'estimatedLTMSMMonth' => array(),
    'estimatedLTMSMDay' => array(),
    'estimatedLTMSM' => array(),
    'estimatedLTMSM5' => array(),
    'estimatedLTMSM95' => array(),
);

// query for actual landsat observations semi-monthly
$landsatTempQuerySM = <<<QUERY
    SELECT 
        STR_TO_DATE(CONCAT(Year,'-',LPAD(Month,2,'00'),'-',LPAD(DayOfMonth,2,'00')), '%Y-%m-%d') AS Date,
        Round(WaterTemp, 2) as watertemp
    FROM (SELECT
            IF(DAY(ReachLandsatWaterTemp.date) < 15, 1, 15) AS DayOfMonth,
            MONTH(ReachLandsatWaterTemp.date) AS Month,
            YEAR(ReachLandsatWaterTemp.date) AS Year,
            AVG(ReachLandsatWaterTemp.Value) as WaterTemp
        FROM
            ReachLandsatWaterTemp
        WHERE ReachID={$_POST['ReachID']} AND ReachLandsatWaterTemp.Value > 0
        GROUP BY DayOfMonth, Month, Year, ReachID) AS T
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
    STR_TO_DATE(CONCAT(Year,'-',LPAD(Month,2,'00'),'-',LPAD(DayOfMonth,2,'00')), '%Y-%m-%d') AS Date,
    Round(WaterTemp, 2) as watertemp
    FROM (SELECT
        1 AS DayOfMonth,
        MONTH(ReachLandsatWaterTemp.date) AS Month,
        YEAR(ReachLandsatWaterTemp.date) AS Year,
        AVG(ReachLandsatWaterTemp.Value) as WaterTemp
    FROM
        ReachLandsatWaterTemp
    WHERE ReachID={$_POST['ReachID']} AND ReachLandsatWaterTemp.Value > 0
    GROUP BY DayOfMonth, Month, Year, ReachID) AS T
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

// query for long term means monthly
$landsatLTMQueryM = <<<QUERY
    SELECT
        MONTH(DATE) AS Month,
        ReachID,
        ROUND(AVG(VALUE), 2) AS WaterTemperature
    FROM
        ReachLandsatWaterTemp
    WHERE
        ReachID = {$_POST['ReachID']} AND Date < CURRENT_DATE() AND Date > DATE_SUB(CURRENT_DATE(), INTERVAL 30 YEAR)
    GROUP BY Month , ReachID
    ORDER BY ReachID , Month
    QUERY;

// echo $landsatTempQueryM;

$result = $mysqli_connection->query($landsatLTMQueryM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {
    # Add feature arrays to feature collection array

    array_push($plotData['landsatLTMMMonth'], $row['Month']);
    array_push($plotData['landsatLTMM'], $row['WaterTemperature']);
}

// query for long term means semi-monthly
$landsatLTMQuerySM = <<<QUERY
    SELECT 
        -- DAY(DATE) AS Day,
        -- MONTH(DATE) AS Month,
        MONTH(DATE) + IF(DAY(DATE)=1,0, 0.5) AS Month,
        ReachID,
        ROUND(AVG(VALUE), 2) AS WaterTemperature
    FROM
        ReachLandsatWaterTemp
    WHERE
        ReachID = {$_POST['ReachID']} AND Date < CURRENT_DATE() AND Date > DATE_SUB(CURRENT_DATE(), INTERVAL 30 YEAR)
    GROUP BY Month , ReachID
    ORDER BY ReachID , Month
    QUERY;

// echo $landsatLTMQuerySM;i

$result = $mysqli_connection->query($landsatLTMQuerySM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {
    # Add feature arrays to feature collection array

    array_push($plotData['landsatLTMSMMonth'], $row['Month']);
    // array_push($plotData['landsatLTMSMDay'], $row['Day']);
    array_push($plotData['landsatLTMSM'], $row['WaterTemperature']);
}

// query for monthly deviations
// $deviationQueryM = <<<QUERY
//     SELECT
//         Date,
//         ROUND(Value - WaterTemperature, 2) as Deviation
//     FROM
//         ReachEstimatedWaterTemp
//     INNER JOIN ReachLandsatLTMMonthly ON 
//         (ReachEstimatedWaterTemp.ReachID = ReachLandsatLTMMonthly.ReachID
//         AND
//         MONTH(ReachEstimatedWaterTemp.Date) = ReachLandsatLTMMonthly.Month)
//     WHERE ReachEstimatedWaterTemp.ReachID = {$_POST['ReachID']} AND ReachEstimatedWaterTemp.Tag = 'M'
//     ORDER BY Date;
//     QUERY;

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
                ReachID,
                MONTH(Date) AS Month,
                Tag
        FROM
            ReachEstimatedWaterTemp
        GROUP BY Year , DayOfMonth , ReachID , Month , Tag) AS T
            INNER JOIN
        (SELECT 
            1 AS DayOfMonth,
                MONTH(DATE) AS Month,
                ReachID,
                ROUND(AVG(VALUE), 2) AS Value
        FROM
            ReachEstimatedWaterTemp
        WHERE
            ReachID = {$_POST['ReachID']}
        GROUP BY Month , ReachID , DayOfMonth
        ORDER BY ReachID , Month , DayOfMonth) AS LTM ON (T.ReachID = LTM.ReachID
            AND T.Month = LTM.Month
            AND T.DayOfMonth = LTM.DayOfMonth)
    WHERE
        T.ReachID = {$_POST['ReachID']}
    ORDER BY Date;
    QUERY;

// echo $landsatLTMQuerySM;

$result = $mysqli_connection->query($deviationQueryM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {
    # Add feature arrays to feature collection array

    array_push($plotData['deviationMDate'], $row['Date']);
    array_push($plotData['deviationMDeviation'], $row['Deviation']);
}

// query for semi-monthly deviations
// $deviationQuerySM = <<<QUERY
//     SELECT
//         Date,
//         ROUND(Value - WaterTemperature, 2) as Deviation
//     FROM
//         ReachEstimatedWaterTemp
//     INNER JOIN ReachLandsatLTMSemiMonthly ON 
//         (ReachEstimatedWaterTemp.ReachID = ReachLandsatLTMSemiMonthly.ReachID
//         AND
//         MONTH(ReachEstimatedWaterTemp.Date) = ReachLandsatLTMSemiMonthly.Month
//         AND
//         DAY(ReachEstimatedWaterTemp.Date) = ReachLandsatLTMSemiMonthly.DayOfMonth)
//     WHERE ReachEstimatedWaterTemp.ReachID = {$_POST['ReachID']} AND ReachEstimatedWaterTemp.Tag = 'SM'
//     ORDER BY Date;
//     QUERY;

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
                DAY(Date) AS DayOfMonth,
                ReachID,
                MONTH(Date) AS Month,
                Tag
        FROM
            ReachEstimatedWaterTemp
        GROUP BY Year , DayOfMonth , ReachID , Month , Tag) AS T
            INNER JOIN
        (SELECT 
            DAY(Date) AS DayOfMonth,
                MONTH(DATE) AS Month,
                ReachID,
                ROUND(AVG(VALUE), 2) AS Value
        FROM
            ReachEstimatedWaterTemp
        WHERE
            ReachID = {$_POST['ReachID']}
        GROUP BY Month , ReachID , DayOfMonth
        ORDER BY ReachID , Month , DayOfMonth) AS LTM ON (T.ReachID = LTM.ReachID
            AND T.Month = LTM.Month
            AND T.DayOfMonth = LTM.DayOfMonth)
    WHERE
        T.ReachID = {$_POST['ReachID']}
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

// query for semi-monthly estimated temperatures
$estimatedTempQuerySM = <<<QUERY
    SELECT 
        STR_TO_DATE(CONCAT(Year,
                        '-',
                        LPAD(Month, 2, '00'),
                        '-',
                        LPAD(DayOfMonth, 2, '00')),
                '%Y-%m-%d') AS Date,
        ROUND(Value, 2) AS WaterTemperature
    FROM
        (SELECT 
            YEAR(Date) AS Year,
                MONTH(Date) AS Month,
                DAY(Date) AS DayOfMonth,
                AVG(Value) AS Value
        FROM
            ReachEstimatedWaterTemp
        WHERE
            ReachEstimatedWaterTemp.ReachID = {$_POST['ReachID']}
        GROUP BY Year , Month , DayOfMonth) AS T
    ORDER BY Date;
    QUERY;

// echo $landsatLTMQuerySM;i

$result = $mysqli_connection->query($estimatedTempQuerySM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['estimatedTempSMDates'], $row['Date']);
    array_push($plotData['estimatedTempSM'], $row['WaterTemperature']);
}

// query for monthly estimated temperatures
$estimatedTempQueryM = <<<QUERY
    SELECT 
        STR_TO_DATE(CONCAT(Year,
                        '-',
                        LPAD(Month, 2, '00'),
                        '-',
                        LPAD(DayOfMonth, 2, '00')),
                '%Y-%m-%d') AS Date,
        ROUND(Value, 2) AS WaterTemperature
    FROM
        (SELECT 
            YEAR(Date) AS Year,
                MONTH(Date) AS Month,
                1 AS DayOfMonth,
                AVG(Value) AS Value
        FROM
            ReachEstimatedWaterTemp
        WHERE
            ReachEstimatedWaterTemp.ReachID = {$_POST['ReachID']}
        GROUP BY Year , Month , DayOfMonth) AS T
    ORDER BY Date;
    QUERY;

// echo $landsatLTMQuerySM;

$result = $mysqli_connection->query($estimatedTempQueryM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['estimatedTempMDates'], $row['Date']);
    array_push($plotData['estimatedTempM'], $row['WaterTemperature']);
}

// // query for actual landsat observations semi-monthly
// $estimateTempQuerySM = <<<QUERY
//     SELECT 
//         STR_TO_DATE(CONCAT(Year,'-',LPAD(Month,2,'00'),'-',LPAD(DayOfMonth,2,'00')), '%Y-%m-%d') AS Date,
//         Round(WaterTemp, 2) as watertemp
//     FROM (SELECT
//             DAY(ReachEstimatedWaterTemp.date) AS DayOfMonth,
//             MONTH(ReachEstimatedWaterTemp.date) AS Month,
//             YEAR(ReachEstimatedWaterTemp.date) AS Year,
//             AVG(ReachEstimatedWaterTemp.Value) as WaterTemp
//         FROM
//             ReachEstimatedWaterTemp
//         WHERE ReachID={$_POST['ReachID']} AND ReachEstimatedWaterTemp.Value > 0
//         GROUP BY DayOfMonth, Month, Year, ReachID) AS T
//     ORDER BY Date;
//     QUERY;

// // echo $estimateTempQuerySM;

// $result = $mysqli_connection->query($estimateTempQuerySM);

// # Loop through rows to build feature arrays
// while ($row = $result->fetch_assoc()) {
//     # Add feature arrays to feature collection array

//     array_push($plotData['estimatedTempSMDates'], $row['Date']);
//     array_push($plotData['estimatedTempSMTemp'], $row['watertemp']);
// }

// // query for actual landsat observations monthly
// $estimatedTempQueryM = <<<QUERY
//     SELECT 
//     STR_TO_DATE(CONCAT(Year,'-',LPAD(Month,2,'00'),'-',LPAD(DayOfMonth,2,'00')), '%Y-%m-%d') AS Date,
//     Round(WaterTemp, 2) as watertemp
//     FROM (SELECT
//         1 AS DayOfMonth,
//         MONTH(ReachEstimatedWaterTemp.date) AS Month,
//         YEAR(ReachEstimatedWaterTemp.date) AS Year,
//         AVG(ReachEstimatedWaterTemp.Value) as WaterTemp
//     FROM
//         ReachEstimatedWaterTemp
//     WHERE ReachID={$_POST['ReachID']} AND ReachEstimatedWaterTemp.Value > 0
//     GROUP BY DayOfMonth, Month, Year, ReachID) AS T
//     ORDER BY Date;
//     QUERY;

// // echo $estimatedTempQueryM;

// $result = $mysqli_connection->query($estimatedTempQueryM);

// # Loop through rows to build feature arrays
// while ($row = $result->fetch_assoc()) {
//     # Add feature arrays to feature collection array

//     array_push($plotData['estimatedTempMDates'], $row['Date']);
//     array_push($plotData['estimatedTempMTemp'], $row['watertemp']);
// }

// query for long term means monthly
$estimatedLTMQueryM = <<<QUERY
    SELECT
        MONTH(DATE) AS Month,
        ReachID,
        ROUND(AVG(VALUE), 2) AS WaterTemperature
    FROM
        ReachEstimatedWaterTemp
    WHERE
        ReachID = {$_POST['ReachID']} AND Date < CURRENT_DATE() AND Date > DATE_SUB(CURRENT_DATE(), INTERVAL 30 YEAR)
    GROUP BY Month , ReachID
    ORDER BY ReachID , Month
    QUERY;

// echo $estimatedTempQueryM;

$result = $mysqli_connection->query($estimatedLTMQueryM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {
    # Add feature arrays to feature collection array

    array_push($plotData['estimatedLTMMMonth'], $row['Month']);
    array_push($plotData['estimatedLTMM'], $row['WaterTemperature']);
}

// query for long term means semi-monthly
$estimatedLTMQuerySM = <<<QUERY
    SELECT 
        -- DAY(DATE) AS Day,
        -- MONTH(DATE) AS Month,
        MONTH(DATE) + IF(DAY(DATE)=1,0, 0.5) AS Month,
        ReachID,
        ROUND(AVG(VALUE), 2) AS WaterTemperature
    FROM
        ReachEstimatedWaterTemp
    WHERE
        ReachID = {$_POST['ReachID']} AND Date < CURRENT_DATE() AND Date > DATE_SUB(CURRENT_DATE(), INTERVAL 30 YEAR)
    GROUP BY Month , ReachID
    ORDER BY ReachID , Month
    QUERY;

// echo $estimatedLTMQuerySM;i

$result = $mysqli_connection->query($estimatedLTMQuerySM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {
    # Add feature arrays to feature collection array

    array_push($plotData['estimatedLTMSMMonth'], $row['Month']);
    // array_push($plotData['estimatedLTMSMDay'], $row['Day']);
    array_push($plotData['estimatedLTMSM'], $row['WaterTemperature']);
}




// // header('Content-type: application/json');
echo json_encode($plotData, JSON_NUMERIC_CHECK);


$mysqli_connection->close();
