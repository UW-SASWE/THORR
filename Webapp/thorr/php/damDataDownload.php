<?php

require_once('dbConfig.php');

$mysqli_connection = new MySQLi($host, $username, $password, $dbname, $port);

// The name of the text file
$filename = "temp_download_dam.csv";

// Open a file in write mode ('w')
$fp = fopen($filename, 'w');

// Write the column headers to the file
if ($_POST['DataType'] == "deviations") {
    fputcsv($fp, array('Date', 'deviation(C)'));
} else {
    fputcsv($fp, array('Date', 'WaterTemperature(C)'));
}

if ($_POST['DataType'] == "water-temperature") {
    if ($_POST['TimeScale'] == "weekly") {
        $sql = <<<QUERY
        SELECT 
            DATE_ADD(STR_TO_DATE(CONCAT(YEAR(Date),
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
            DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL
        GROUP BY DATE_ADD(STR_TO_DATE(CONCAT(YEAR(Date),
                            '-',
                            LPAD(01, 2, '00'),
                            '-',
                            LPAD(01, 2, '00')),
                    '%Y-%m-%d'),
            INTERVAL ( FLOOR(DAYOFYEAR(Date) / 7)) WEEK)
        ORDER BY Date;
        QUERY;
    } elseif ($_POST['TimeScale'] == "monthly") {
        $sql = <<<QUERY
        SELECT 
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
            DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL
        GROUP BY STR_TO_DATE(CONCAT(YEAR(Date),
                        '-',
                        LPAD(MONTH(Date), 2, '00'),
                        '-',
                        LPAD(01, 2, '00')),
                '%Y-%m-%d')
        ORDER BY Date;
        QUERY;
    } elseif ($_POST['TimeScale'] == "bi-weekly") {
        $sql = <<<QUERY
        SELECT 
            DATE_ADD(STR_TO_DATE(CONCAT(YEAR(Date),
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
            DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL
        GROUP BY DATE_ADD(STR_TO_DATE(CONCAT(YEAR(Date),
                            '-',
                            LPAD(01, 2, '00'),
                            '-',
                            LPAD(01, 2, '00')),
                    '%Y-%m-%d'),
            INTERVAL (2 * FLOOR(DAYOFYEAR(Date) / 14)) WEEK)
        ORDER BY Date;
        QUERY;
    } elseif ($_POST['TimeScale'] == "irregular") {
        $sql = <<<QUERY
        SELECT 
            Date AS Date, WaterTempC AS WaterTemperature
        FROM
            DamData
        WHERE
            DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL
        ORDER BY Date;
        QUERY;
    }
} elseif ($_POST['DataType'] == "long-term-mean") {
    if ($_POST['TimeScale'] == "weekly") {
        $sql = <<<QUERY
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
            DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL
        GROUP BY DATE_ADD(STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE),
                            '-',
                            LPAD(01, 2, '00'),
                            '-',
                            LPAD(01, 2, '00')),
                    '%Y-%m-%d'),
            INTERVAL (FLOOR(DAYOFYEAR(Date) / 7)) WEEK)
        ORDER BY Date;
        QUERY;
    } elseif ($_POST['TimeScale'] == "monthly") {
        $sql = <<<QUERY
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
            DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL
        GROUP BY STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE),
                        '-',
                        LPAD(MONTH(Date), 2, '00'),
                        '-',
                        LPAD(01, 2, '00')),
                '%Y-%m-%d')
        ORDER BY Date;
        QUERY;
    } elseif ($_POST['TimeScale'] == "bi-weekly") {
        $sql = <<<QUERY
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
            DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL
        GROUP BY DATE_ADD(STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE),
                            '-',
                            LPAD(01, 2, '00'),
                            '-',
                            LPAD(01, 2, '00')),
                    '%Y-%m-%d'),
            INTERVAL (2 * FLOOR(DAYOFYEAR(Date) / 14)) WEEK)
        ORDER BY Date;
        QUERY;
    } elseif ($_POST['TimeScale'] == "irregular") {
        $sql = <<<QUERY
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
            DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL
        GROUP BY STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE),
                    '-',
                    LPAD(MONTH(Date), 2, '00'),
                    '-',
                    LPAD(DAY(Date), 2, '00')),
            '%Y-%m-%d')
        ORDER BY Date;
        QUERY;
    }
} elseif ($_POST['DataType'] == "deviations") {
    if ($_POST['TimeScale'] == "weekly") {
        $sql = <<<QUERY
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
                DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL
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
                DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL
            GROUP BY DATE_ADD(STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE), '-', LPAD(01, 2, '00'), '-', LPAD(01, 2, '00')), '%Y-%m-%d'), INTERVAL (FLOOR(DAYOFYEAR(Date) / 7)) WEEK)
                , FLOOR(DAYOFYEAR(Date) / 7)) AS LTM ON (LTM.Week = Est.Week)
        ORDER BY Est.Date;
        QUERY;
    } elseif ($_POST['TimeScale'] == "monthly") {
        $sql = <<<QUERY
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
                DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL
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
            DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL
        GROUP BY STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE),
                        '-',
                        LPAD(MONTH(Date), 2, '00'),
                        '-',
                        LPAD(01, 2, '00')),
                '%Y-%m-%d')) AS LTM ON (MONTH(LTM.Date) = MONTH(Est.Date))
        ORDER BY Est.Date;
        QUERY;
    } elseif ($_POST['TimeScale'] == "bi-weekly") {
        $sql = <<<QUERY
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
                DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL
            GROUP BY DATE_ADD(STR_TO_DATE(CONCAT(YEAR(Date), '-', LPAD(01, 2, '00'), '-', LPAD(01, 2, '00')), '%Y-%m-%d'), INTERVAL (2 * (FLOOR(DAYOFYEAR(Date) / 14))) WEEK) , (2 * (FLOOR(DAYOFYEAR(Date) / 14)))) AS Est
                LEFT JOIN
            (SELECT 
                DATE_ADD(STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE), '-', LPAD(01, 2, '00'), '-', LPAD(01, 2, '00')), '%Y-%m-%d'), INTERVAL (2 * (FLOOR(DAYOFYEAR(Date) / 14))) WEEK) AS Date,
                    ROUND(AVG(WaterTempC), 2) AS WaterTemperature,
                    (2 * (FLOOR(DAYOFYEAR(Date) / 14))) AS week
            FROM
                DamData
            WHERE
                DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL
            GROUP BY DATE_ADD(STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE), '-', LPAD(01, 2, '00'), '-', LPAD(01, 2, '00')), '%Y-%m-%d'), INTERVAL (2 * (FLOOR(DAYOFYEAR(Date) / 14))) WEEK) , (2 * (FLOOR(DAYOFYEAR(Date) / 14)))) AS LTM ON (LTM.Week = Est.Week)
        ORDER BY Est.Date;
        QUERY;
    } elseif ($_POST['TimeScale'] == "irregular") {
        $sql = <<<QUERY
        SELECT 
            Est.Date AS Date,
            Round((Est.WaterTemperature - LTM.WaterTemperature), 2) AS Deviation
        FROM
            (SELECT 
                Date AS Date, WaterTempC AS WaterTemperature
            FROM
                DamData
            WHERE
                DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL) AS Est
                LEFT JOIN
            (SELECT 
                STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE), '-', LPAD(MONTH(Date), 2, '00'), '-', LPAD(DAY(Date), 2, '00')), '%Y-%m-%d') AS Date,
                    ROUND(AVG(WaterTempC), 2) AS WaterTemperature
            FROM
                DamData
            WHERE
                DamID = {$_POST['DamID']} AND WaterTempC IS NOT NULL
            GROUP BY STR_TO_DATE(CONCAT(YEAR(CURRENT_DATE), '-', LPAD(MONTH(Date), 2, '00'), '-', LPAD(DAY(Date), 2, '00')), '%Y-%m-%d')) AS LTM ON (MONTH(LTM.Date) = MONTH(Est.Date) and Day(LTM.Date) = Day(Est.Date))
        ORDER BY Est.Date;
        QUERY;
    }
}

$result = $mysqli_connection->query($sql);

// write the query results to the file
if ($_POST['DataType'] == "deviations") {
    while ($row = $result->fetch_assoc()) {
        fputcsv($fp, array($row['Date'], $row['Deviation']));
    }
} else {
    while ($row = $result->fetch_assoc()) {
        fputcsv($fp, array($row['Date'], $row['WaterTemperature']));
    }
}


// Close the file
fclose($fp);

// Set headers to force download on the client side
header('Content-Description: File Transfer');
header('Content-Type: application/octet-stream');
header('Content-Disposition: attachment; filename="' . basename($filename) . '"');
header('Expires: 0');
header('Cache-Control: must-revalidate');
header('Pragma: public');
header('Content-Length: ' . filesize($filename));

// Clear the output buffer
ob_clean();
flush();

// Read the file and output its contents
readfile($filename);

// delete file
unlink($filename);

// Terminate the script
exit;
