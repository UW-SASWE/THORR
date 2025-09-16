<?php

require_once('dbConfig.php');

$connStr = "host=$host port=$port dbname=$dbname user=$username password=$password";
$pgsql_connection = pg_connect($connStr);

// if ($mysqli_connection->connect_error) {
//     echo "Not connected, error: " . $mysqli_connection->connect_error;
// } else {
//     echo "Connected.";
// }
echo ($_POST['priorityBasinID']);

$sql = <<<QUERY
SELECT "RegionID" as BasinID, "Name" FROM "$schema"."Regions" ORDER BY "Name" ASC;
QUERY;

$result = pg_query($pgsql_connection, $sql);
if ($_POST['priorityBasinID']) {
    echo '<option value="" disabled>Select Basin</option>';
} else {
    echo '<option value="" selected disabled>Select Basin</option>';
}
if (pg_num_rows($result) > 0) {
    // output data of each row
    while ($row = pg_fetch_assoc($result)) {
        if ($_POST['priorityBasinID'] == $row["BasinID"]) {
            echo "<option value=" . $row["BasinID"] . " selected>" . $row["Name"] . "</option>";
        } else
            echo "<option value=" . $row["BasinID"] . ">" . $row["Name"] . "</option>";
        // echo "id: " . $row["BasinID"] . " - Name: " . $row["Name"] . "<br>";
    }
}

pg_close($pgsql_connection);
