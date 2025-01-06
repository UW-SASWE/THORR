<?php

require_once('dbConfig.php');

$connStr = "host=$host port=$port dbname=$dbname user=$username password=$password";
$pgsql_connection = pg_connect($connStr);

// if ($mysqli_connection->connect_error) {
//     echo "Not connected, error: " . $mysqli_connection->connect_error;
// } else {
//     echo "Connected.";
// }

if ($_POST['BasinID']) {
    if (isset($_POST['RiverID'])) {
        $sql = <<<QUERY
        SELECT * 
        FROM (SELECT
        "Dams"."BasinID", "Dams"."RiverID", "Dams"."Name" as "Name", "Dams"."DamID" as "DamID"
        FROM
        "$schema"."Dams"
        INNER JOIN "$schema"."Basins" USING ("BasinID")
        INNER JOIN "$schema"."Rivers" USING ("RiverID")
        WHERE "Basins"."BasinID" = {$_POST['BasinID']} AND "RiverID" = {$_POST['RiverID']}
        ) as T
        ORDER BY "Name" ASC;
        QUERY;
    } else {
        $sql = <<<QUERY
        SELECT * 
        FROM (SELECT
        "Dams"."BasinID", "Dams"."RiverID", "Dams"."Name" as "Name", "Dams"."DamID" as "DamID"
        FROM
        "$schema"."Dams"
        INNER JOIN "$schema"."Basins" USING ("BasinID")
        INNER JOIN "$schema"."Rivers" USING ("RiverID")
        WHERE "Basins"."BasinID" = {$_POST['BasinID']}
        ) as T
        ORDER BY "Name" ASC;
        QUERY;
    }
} else {
    $sql = <<<QUERY
        SELECT * 
        FROM (SELECT
        "Dams"."BasinID", "Dams"."RiverID", "Dams"."Name" as "Name", "Dams"."DamID" as "DamID"
        FROM
        "$schema"."Dams"
        INNER JOIN "$schema"."Basins" USING ("BasinID")
        INNER JOIN "$schema"."Rivers" USING ("RiverID")
        ) as T
        ORDER BY "Name" ASC;
    QUERY;
}
// echo $sql;

$result = pg_query($pgsql_connection, $sql);
echo '<option value="" selected disabled>Select Dam</option>';

if (pg_num_rows($result) > 0) {
    // output data of each row
    while ($row = pg_fetch_assoc($result)) {
        echo "<option value=" . $row["DamID"] . ">" . $row["Name"] . "</option>";
    }
}

pg_close($pgsql_connection);
