<?php

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
        Dams.BasinID, Dams.RiverID, Dams.Name as Name, Dams.DamID as DamID
        FROM
        thorr.Dams
        INNER JOIN Basins USING (BasinID)
        INNER JOIN Rivers USING (RiverID)
        WHERE Basins.BasinID = {$_POST['BasinID']} AND RiverID = {$_POST['RiverID']}
        ) as T
        ORDER BY Name ASC;
        QUERY;
    } else {
        $sql = <<<QUERY
        SELECT * 
        FROM (SELECT
        Dams.BasinID, Dams.RiverID, Dams.Name as Name, Dams.DamID as DamID
        FROM
        thorr.Dams
        INNER JOIN Basins USING (BasinID)
        INNER JOIN Rivers USING (RiverID)
        WHERE Basins.BasinID = {$_POST['BasinID']}
        ) as T
        ORDER BY Name ASC;
        QUERY;
    }
} else {
    $sql = <<<QUERY
    SELECT * 
    FROM (SELECT
    Dams.BasinID, Dams.DamID, Dams.RiverID, Dams.Name
    FROM
    thorr.Dams
    INNER JOIN Basins USING (BasinID)
    INNER JOIN Rivers USING (RiverID)) as T
    ORDER BY Name ASC;
    QUERY;
}
// echo $sql;

$result = $mysqli_connection->query($sql);
echo '<option value="" selected disabled>Select Dam</option>';

if ($result->num_rows > 0) {
    // output data of each row
    while ($row = $result->fetch_assoc()) {
        echo "<option value=" . $row["DamID"] . ">" . $row["Name"] . "</option>";
    }
}

$mysqli_connection->close();
