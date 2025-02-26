<?php

///////////////////////////////////////////////////////////////////////////
// this is likely a redundant file, as it is not used in the application //
///////////////////////////////////////////////////////////////////////////

require_once('dbConfig.php');
$mysqli_connection = new MySQLi($host, $username, $password, $dbname, $port);

// if ($mysqli_connection->connect_error) {
//     echo "Not connected, error: " . $mysqli_connection->connect_error;
// } else {
//     echo "Connected.";
// }

if ($_POST['BasinID']) {
    if ($_POST['RiverID']) {
        $sql = <<<QUERY
        SELECT * 
        FROM (SELECT
        ReachID, RiverID, Reaches.Name
        FROM
        hydrothermal_history.Rivers
        INNER JOIN Basins USING (BasinID)
        INNER JOIN Reaches USING (RiverID)
        WHERE Basins.BasinID = {$_POST['BasinID']} AND RiverID = {$_POST['RiverID']}
        ) as T;
        QUERY;
    } else {
        $sql = <<<QUERY
        SELECT * 
        FROM (SELECT
        ReachID, RiverID, Reaches.Name
        FROM
        hydrothermal_history.Rivers
        INNER JOIN Basins USING (BasinID)
        INNER JOIN Reaches USING (RiverID)
        WHERE Basins.BasinID = {$_POST['BasinID']}
        ) as T;
        QUERY;
    }
} else {
    $sql = <<<QUERY
    SELECT * 
    FROM (SELECT
    ReachID, RiverID, Reaches.Name as Name
    FROM
    hydrothermal_history.Rivers
    INNER JOIN Basins USING (BasinID)
    INNER JOIN Reaches USING (RiverID)
    ) as T;
    QUERY;
}

$result = $mysqli_connection->query($sql);
echo '<option value="" selected disabled>Select River</option>';

if ($result->num_rows > 0) {
    // output data of each row
    while ($row = $result->fetch_assoc()) {
        echo "<option value=" . $row["ReachID"] . ">" . $row["Name"] . "</option>";
    }
}

$mysqli_connection->close();
