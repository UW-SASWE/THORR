<?php

// TODO: determine if it's a redundant file or not
require_once('dbConfig.php');

$mysqli_connection = new MySQLi($host, $username, $password, $dbname, $port);

// if ($mysqli_connection->connect_error) {
//     echo "Not connected, error: " . $mysqli_connection->connect_error;
// }

// echo ($_POST['row_count'] and $_POST['offset']);

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

// query for actual landsat observations monthly
$landsatLTMQueryM = <<<QUERY
    SELECT
        Month,
        1 AS DayOfMonth,
        ROUND(WaterTemperature, 2) AS WaterTemperature,
        ROUND(WaterTemperature5, 2) AS WaterTemperature5,
        ROUND(WaterTemperature95, 2) AS WaterTemperature95,
        ReachID
    FROM
        ReachLandsatLTMMonthly
    WHERE ReachID = {$_POST['ReachID']}
    ORDER BY Month, DayOfMonth;
    QUERY;

// echo $landsatTempQueryM;

$result = $mysqli_connection->query($landsatLTMQueryM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {
    # Add feature arrays to feature collection array

    array_push($plotData['landsatLTMMMonth'], $row['Month']);
    array_push($plotData['landsatLTMM'], $row['WaterTemperature']);
    array_push($plotData['landsatLTMM5'], $row['WaterTemperature5']);
    array_push($plotData['landsatLTMM95'], $row['WaterTemperature95']);
}

// query for actual landsat observations monthly
$landsatLTMQuerySM = <<<QUERY
    SELECT
        Month,
        DayOfMonth,
        ROUND(WaterTemperature, 2) AS WaterTemperature,
        ROUND(WaterTemperature5, 2) AS WaterTemperature5,
        ROUND(WaterTemperature95, 2) AS WaterTemperature95,
        ReachID
    FROM
        ReachLandsatLTMSemiMonthly
    WHERE ReachID = {$_POST['ReachID']}
    ORDER BY Month, DayOfMonth;
    QUERY;

// echo $landsatLTMQuerySM;i

$result = $mysqli_connection->query($landsatLTMQuerySM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {
    # Add feature arrays to feature collection array

    array_push($plotData['landsatLTMSMMonth'], $row['Month']);
    array_push($plotData['landsatLTMSMDay'], $row['DayOfMonth']);
    array_push($plotData['landsatLTMSM'], $row['WaterTemperature']);
    array_push($plotData['landsatLTMSM5'], $row['WaterTemperature5']);
    array_push($plotData['landsatLTMSM95'], $row['WaterTemperature95']);
}

// query for monthly deviations
$deviationQueryM = <<<QUERY
    SELECT
        Date,
        ROUND(Value - WaterTemperature, 2) as Deviation
    FROM
        ReachEstimatedWaterTemp
    INNER JOIN ReachLandsatLTMMonthly ON 
        (ReachEstimatedWaterTemp.ReachID = ReachLandsatLTMMonthly.ReachID
        AND
        MONTH(ReachEstimatedWaterTemp.Date) = ReachLandsatLTMMonthly.Month)
    WHERE ReachEstimatedWaterTemp.ReachID = {$_POST['ReachID']} AND ReachEstimatedWaterTemp.Tag = 'M'
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
        Date,
        ROUND(Value - WaterTemperature, 2) as Deviation
    FROM
        ReachEstimatedWaterTemp
    INNER JOIN ReachLandsatLTMSemiMonthly ON 
        (ReachEstimatedWaterTemp.ReachID = ReachLandsatLTMSemiMonthly.ReachID
        AND
        MONTH(ReachEstimatedWaterTemp.Date) = ReachLandsatLTMSemiMonthly.Month
        AND
        DAY(ReachEstimatedWaterTemp.Date) = ReachLandsatLTMSemiMonthly.DayOfMonth)
    WHERE ReachEstimatedWaterTemp.ReachID = {$_POST['ReachID']} AND ReachEstimatedWaterTemp.Tag = 'SM'
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
        Date,
        ROUND(Value, 2) as WaterTemperature
    FROM
        ReachEstimatedWaterTemp
    WHERE ReachEstimatedWaterTemp.ReachID = {$_POST['ReachID']} AND ReachEstimatedWaterTemp.Tag = 'SM'
    ORDER BY Date;
    QUERY;

// echo $landsatLTMQuerySM;i

$result = $mysqli_connection->query($estimatedTempQuerySM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['estimatedTempSMDate'], $row['Date']);
    array_push($plotData['estimatedTempSM'], $row['WaterTemperature']);
}

// query for monthly estimated temperatures
$estimatedTempQueryM = <<<QUERY
    SELECT
        Date,
        ROUND(Value, 2) as WaterTemperature
    FROM
        ReachEstimatedWaterTemp
    WHERE ReachEstimatedWaterTemp.ReachID = {$_POST['ReachID']} AND ReachEstimatedWaterTemp.Tag = 'M'
    ORDER BY Date;
    QUERY;

// echo $landsatLTMQuerySM;i

$result = $mysqli_connection->query($estimatedTempQueryM);

# Loop through rows to build feature arrays
while ($row = $result->fetch_assoc()) {

    array_push($plotData['estimatedTempMDate'], $row['Date']);
    array_push($plotData['estimatedTempM'], $row['WaterTemperature']);
}



// // header('Content-type: application/json');
echo json_encode($plotData, JSON_NUMERIC_CHECK);


$mysqli_connection->close();
