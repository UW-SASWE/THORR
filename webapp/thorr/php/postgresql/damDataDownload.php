<?php

require_once('dbConfig.php');

$connStr = "host=$host port=$port dbname=$dbname user=$username password=$password";
$pgsql_connection = pg_connect($connStr);

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
            ) AS "Date",
            ROUND(AVG("WaterTempC")::numeric, 2) AS "WaterTemperature"
        FROM
            $schema."DamData"
        WHERE
            "DamID" = {$_POST['DamID']} AND "WaterTempC" IS NOT NULL
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
    } elseif ($_POST['TimeScale'] == "monthly") {
        $sql = <<<QUERY
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
            ) AS "Date",
            ROUND(AVG("WaterTempC")::NUMERIC, 2) AS "WaterTemperature"
        FROM
            $schema."DamData"
        WHERE
            ("DamID" = {$_POST['DamID']})
            AND ("WaterTempC" IS NOT NULL)
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
    } elseif ($_POST['TimeScale'] == "bi-weekly") {
        $sql = <<<QUERY
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
            ) AS "Date",
            ROUND(AVG("WaterTempC")::NUMERIC, 2) AS "WaterTemperature"
        FROM
            $schema."DamData"
        WHERE
            "DamID" = {$_POST['DamID']}
            AND "WaterTempC" IS NOT NULL
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
    } elseif ($_POST['TimeScale'] == "irregular") {
        $sql = <<<QUERY
        SELECT
            "Date" AS "Date",
            ROUND("WaterTempC"::NUMERIC, 2) AS "WaterTemperature"
        FROM
            $schema."DamData"
        WHERE
            "DamID" = {$_POST['DamID']}
            AND "WaterTempC" IS NOT NULL
        ORDER BY
            "Date";
        QUERY;
    }
} elseif ($_POST['DataType'] == "long-term-mean") {
    if ($_POST['TimeScale'] == "weekly") {
        $sql = <<<QUERY
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
            ) AS "Date",
            ROUND(AVG("WaterTempC")::numeric, 2) AS "WaterTemperature"
        FROM
            $schema."DamData"
        WHERE
            "DamID" = {$_POST['DamID']} AND "WaterTempC" IS NOT NULL
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
    } elseif ($_POST['TimeScale'] == "monthly") {
        $sql = <<<QUERY
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
            ) AS "Date",
            ROUND(AVG("WaterTempC")::NUMERIC, 2) AS "WaterTemperature"
        FROM
            $schema."DamData"
        WHERE
            ("DamID" = {$_POST['DamID']})
            AND ("WaterTempC" IS NOT NULL)
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
    } elseif ($_POST['TimeScale'] == "bi-weekly") {
        $sql = <<<QUERY
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
            ) AS "Date",
            ROUND(AVG("WaterTempC")::NUMERIC, 2) AS "WaterTemperature"
        FROM
            $schema."DamData"
        WHERE
            "DamID" = {$_POST['DamID']}
            AND "WaterTempC" IS NOT NULL
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
    } elseif ($_POST['TimeScale'] == "irregular") {
        $sql = <<<QUERY
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
                    EXTRACT(
                        DAY
                        FROM
                            "Date"
                    )
                ),
                'YYYY-MM-DD'
            ) AS "Date",
            ROUND(AVG("WaterTempC")::NUMERIC, 2) AS "WaterTemperature"
        FROM
            $schema."DamData"
        WHERE
            ("DamID" = {$_POST['DamID']})
            AND ("WaterTempC" IS NOT NULL)
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
    }
} elseif ($_POST['DataType'] == "deviations") {
    if ($_POST['TimeScale'] == "weekly") {
        $sql = <<<QUERY
        SELECT
            EST."Date" AS "Date",
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
                    ) AS "Date",
                    ROUND(AVG("WaterTempC")::NUMERIC, 2) AS WaterTemperature,
                    FLOOR(
                        EXTRACT(
                            DOY
                            FROM
                                "Date"
                        ) / 7
                    ) AS week
                FROM
                    $schema."DamData"
                WHERE
                    "DamID" = {$_POST['DamID']}
                    AND "WaterTempC" IS NOT NULL
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
                    "Date"
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
                    ) AS "Date",
                    ROUND(AVG("WaterTempC")::NUMERIC, 2) AS WaterTemperature,
                    FLOOR(
                        EXTRACT(
                            DOY
                            FROM
                                "Date"
                        ) / 7
                    ) AS week
                FROM
                    $schema."DamData"
                WHERE
                    "DamID" = {$_POST['DamID']}
                    AND "WaterTempC" IS NOT NULL
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
                    "Date"
            ) AS LTM ON (LTM.week = EST.week)
        ORDER BY
            "Date";
        QUERY;
    } elseif ($_POST['TimeScale'] == "monthly") {
        $sql = <<<QUERY
        SELECT 
            Est."Date" AS "Date",
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
                    ) AS "Date",
                    ROUND(AVG("WaterTempC")::NUMERIC, 2) AS WaterTemperature
                FROM
                    $schema."DamData"
                WHERE
                    ("DamID" = {$_POST['DamID']})
                    AND ("WaterTempC" IS NOT NULL)
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
                    ) AS "Date",
                    ROUND(AVG("WaterTempC")::NUMERIC, 2) AS WaterTemperature
                FROM
                    $schema."DamData"
                WHERE
                    ("DamID" = {$_POST['DamID']})
                    AND ("WaterTempC" IS NOT NULL)
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
                                    LTM."Date") = EXTRACT(
                                MONTH
                                FROM
                                    Est."Date"))
        ORDER BY 
            "Date";
        QUERY;
    } elseif ($_POST['TimeScale'] == "bi-weekly") {
        $sql = <<<QUERY
        SELECT
            EST."Date" AS "Date",
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
                    ) AS "Date",
                    ROUND(AVG("WaterTempC")::NUMERIC, 2) AS WaterTemperature,
                    2 * FLOOR(
                        EXTRACT(
                            DOY
                            FROM
                                "Date"
                        ) / 14
                    ) AS week
                FROM
                    $schema."DamData"
                WHERE
                    "DamID" = {$_POST['DamID']}
                    AND "WaterTempC" IS NOT NULL
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
                    "Date"
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
                    ) AS "Date",
                    ROUND(AVG("WaterTempC")::NUMERIC, 2) AS WaterTemperature,
                    2 * FLOOR(
                        EXTRACT(
                            DOY
                            FROM
                                "Date"
                        ) / 14
                    ) AS week
                FROM
                    $schema."DamData"
                WHERE
                    "DamID" = {$_POST['DamID']}
                    AND "WaterTempC" IS NOT NULL
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
                    "Date"
            ) AS LTM ON (LTM.week = EST.week)
        ORDER BY
            "Date";
        QUERY;
    } elseif ($_POST['TimeScale'] == "irregular") {
        $sql = <<<QUERY
        SELECT
            EST."Date" AS "Date",
            ROUND((EST."WaterTemperature" - LTM."WaterTemperature"), 2) AS "Deviation"
        FROM
            (
                SELECT
                    "Date" AS "Date",
                    ROUND("WaterTempC"::NUMERIC, 2) AS "WaterTemperature"
                FROM
                    $schema."DamData"
                WHERE
                    "DamID" = {$_POST['DamID']}
                    AND "WaterTempC" IS NOT NULL
            ) AS EST
            LEFT JOIN (
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
                            EXTRACT(
                                DAY
                                FROM
                                    "Date"
                            )
                        ),
                        'YYYY-MM-DD'
                    ) AS "Date",
                    ROUND(AVG("WaterTempC")::NUMERIC, 2) AS "WaterTemperature"
                FROM
                    $schema."DamData"
                WHERE
                    ("DamID" = {$_POST['DamID']})
                    AND ("WaterTempC" IS NOT NULL)
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
                        LTM."Date"
                ) = EXTRACT(
                    MONTH
                    FROM
                        EST."Date"
                )
                AND EXTRACT(
                    DOY
                    FROM
                        LTM."Date"
                ) = EXTRACT(
                    DOY
                    FROM
                        EST."Date"
                )
            )
        ORDER BY
            "Date";
        QUERY;
    }
}

$result = pg_query($pgsql_connection, $sql);

// write the query results to the file
if ($_POST['DataType'] == "deviations") {
    while ($row = pg_fetch_assoc($result)) {
        fputcsv($fp, array($row['Date'], $row['Deviation']));
    }
} else {
    while ($row = pg_fetch_assoc($result)) {
        fputcsv($fp, array($row['Date'], $row['WaterTemperature']));
    }
}

pg_close($pgsql_connection);

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
