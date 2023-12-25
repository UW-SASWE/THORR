<?php

require_once('dbConfig.php');
$mysqli_connection = new MySQLi($host, $username, $password, $dbname, $port);

// if ($mysqli_connection->connect_error) {
//     echo "Not connected, error: " . $mysqli_connection->connect_error;
// } else {
//     echo "Connected.";
// }

$sql = "SELECT BasinID, Name FROM Basins ORDER BY Name ASC";
$result = $mysqli_connection->query($sql);
if ($_POST['priorityBasinID']) {
    echo '<option value="" disabled>Select Basin</option>';
} else {
    echo '<option value="" selected disabled>Select Basin</option>';
}
if ($result->num_rows > 0) {
    // output data of each row
    while ($row = $result->fetch_assoc()) {
        if ($_POST['priorityBasinID'] == $row["BasinID"]) {
            echo "<option value=" . $row["BasinID"] . " selected>" . $row["Name"] . "</option>";
        } else
            echo "<option value=" . $row["BasinID"] . ">" . $row["Name"] . "</option>";
        // echo "id: " . $row["BasinID"] . " - Name: " . $row["Name"] . "<br>";
    }
}

$mysqli_connection->close();
