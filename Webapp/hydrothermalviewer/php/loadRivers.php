<?php

require_once('dbConfig.php');
$mysqli_connection = new MySQLi($host, $username, $password, $dbname, $port);

// if ($mysqli_connection->connect_error) {
//     echo "Not connected, error: " . $mysqli_connection->connect_error;
// } else {
//     echo "Connected.";
// }

if ($_POST['BasinID']) {
    $sql = "SELECT RiverID, Name FROM Rivers WHERE BasinID = " . $_POST['BasinID'] . " ORDER BY Name ASC";
} else {
    $sql = "SELECT RiverID, Name FROM Rivers ORDER BY Name ASC";
}

echo '<option value="" selected disabled>Select River</option>';

switch ($_POST['BasinID']) {
    case "1":
        echo <<<EOT
        <!-- <option disabled>-CRITFC Interest-</option> -->
        <option value="12">Columbia River</option>
        <option value="49">Cowlitz River</option>
        <option value="10">Deschutes River</option>
        <option value="32">Hood River</option>
        <option value="21">Klickitat River</option>
        <option value="48">Little White Salmon River</option>
        <option value="57">Snake River</option>
        <option value="18">White Salmon River</option>
        <option disabled>---</option>
        EOT;
        break;
}

$result = $mysqli_connection->query($sql);

if ($result->num_rows > 0) {
    // output data of each row
    while ($row = $result->fetch_assoc()) {
        echo "<option value=" . $row["RiverID"] . ">" . $row["Name"] . "</option>";
    }
}

$mysqli_connection->close();
