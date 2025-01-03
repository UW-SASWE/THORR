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
    $sql = <<<QUERY
    SELECT
        "RiverID",
        "Name"
    FROM
        "$schema"."Rivers"
    WHERE
        "BasinID" = {$_POST['BasinID']}
    ORDER BY
        "Name" ASC;
    QUERY;
} else {
    $sql = <<<QUERY
    SELECT
        "RiverID",
        "Name"
    FROM
        "$schema"."Rivers"
    ORDER BY
        "Name" ASC;
    QUERY;
}

echo '<option value="" selected disabled>Select River</option>';

switch ($_POST['BasinID']) {
    case "1":
        echo <<<EOT
        <!-- <option disabled>-CRITFC Interest-</option> -->
        <option value="9">Columbia River</option>
        <option value="11">Cowlitz River</option>
        <option value="13">Deschutes River</option>
        <option value="22">Hood River</option>
        <option value="32">Klickitat River</option>
        <option value="37">Little White Salmon River</option>
        <option value="45">Snake River</option>
        <option value="55">White Salmon River</option>
        <option disabled>---</option>
        EOT;
        break;
}

$result = pg_query($pgsql_connection, $sql);

if (pg_num_rows($result) > 0) {
    // output data of each row
    while ($row = pg_fetch_assoc($result)) {
        echo "<option value=" . $row["RiverID"] . ">" . $row["Name"] . "</option>";
    }
}

pg_close($pgsql_connection);