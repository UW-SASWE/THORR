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
        ReachID, RiverID, Reaches.Name
        FROM
        hydrothermal_history.Rivers
        INNER JOIN Basins USING (BasinID)
        INNER JOIN Reaches USING (RiverID)
        WHERE Basins.BasinID = {$_POST['BasinID']} AND RiverID = {$_POST['RiverID']}
        ) as T
        ORDER BY Name ASC;
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
        ) as T
        ORDER BY Name ASC;
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
    ) as T
    ORDER BY Name ASC;
    QUERY;
}

$result = $mysqli_connection->query($sql);
echo '<option value="" selected disabled>Select Reach</option>';


switch ($_POST['BasinID']) {
    case "1":
        echo <<<EOT
        <!-- <option disabled>-CRITFC Interest-</option> -->
        <option value="376">Below Bonneville Dam</option>
        <option value="298">Below Chief Joseph Dam</option>
        <option value="286">Below Grand Coulee Dam</option>
        <option value="1236">Below Hells Canyon Dam</option>
        <option value="376">Below John Day Dam</option>
        <option value="358">Below McNary Dam</option>
        <option value="333">Below Priest Rapids Dam</option>
        <option value="320">Below Rock Island Dam</option>
        <option value="315">Below Rocky Reach Dam</option>
        <option value="381">Below The Dalles Dam</option>
        <option value="276">Below US/Canada Border (Columbia)</option>
        <option value="329">Below Wanapum Dam</option>
        <option value="305">Below Wells Dam</option>
        <option value="1261">Clearwater River Confluence</option>
        <option value="410">Cowlitz Confluence (Columbia)</option>
        <option value="930">Cowlitz Confluence (Cowlitz)</option>
        <option value="">Deschutes River Confluence (Columbia)</option>
        <option value="">Deschutes River Confluence (Deschutes)</option>
        <option value="">Hood River Confluence (Columbia)</option>
        <option value="">Hood River Confluence (Hood)</option>
        <option value="">Klickitat River Confluence</option>
        <option value="">L. White Salmon Confluence (Columbia)</option>
        <option value="">L. White Salmon Confluence (LWS)</option>
        <option value="">Snake River Confluence</option>
        <option value="">Umatilla River Confluence</option>
        <option value="232">White Salmon Confluence (Columbia)</option>
        <option value="11">White Salmon Confluence (W. Salmon)</option>
        <option value="235">Wind River Confluence</option>
        <option disabled>---</option>
        EOT;
        break;
}

if ($result->num_rows > 0) {
    // output data of each row
    while ($row = $result->fetch_assoc()) {
        echo "<option value=" . $row["ReachID"] . ">" . $row["Name"] . "</option>";
    }
}

$mysqli_connection->close();
