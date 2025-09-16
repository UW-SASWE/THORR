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
    if ($_POST['RiverID']) {
        $sql = <<<QUERY
        SELECT
            "ReachID",
            "RiverID",
            CONCAT("Rivers"."Name", ' (', "Reaches"."RKm", ' km)') AS "Name"
        FROM
            "$schema"."Rivers"
            INNER JOIN "$schema"."Regions" USING ("RegionID")
            INNER JOIN "$schema"."Reaches" USING ("RiverID")
        WHERE
            "Regions"."RegionID" = {$_POST['BasinID']}
            AND "RiverID" = {$_POST['RiverID']}
        ORDER BY
            "Name" ASC;
        QUERY;
    } else {
        $sql = <<<QUERY
        SELECT
            "ReachID",
            "RiverID",
            CONCAT("Rivers"."Name", ' (', "Reaches"."RKm", ' km)') AS "Name"
        FROM
            "$schema"."Rivers"
            INNER JOIN "$schema"."Regions" USING ("RegionID")
            INNER JOIN "$schema"."Reaches" USING ("RiverID")
        WHERE
            "Regions"."RegionID" = {$_POST['BasinID']}
        ORDER BY
            "Name" ASC;
        QUERY;
    }
} else {
    $sql = <<<QUERY
    SELECT
        "ReachID",
        "RiverID",
        CONCAT("Rivers"."Name", ' (', "Reaches"."RKm", ' km)') AS "Name"
    FROM
        "$schema"."Rivers"
        INNER JOIN "$schema"."Regions" USING ("RegionID")
        INNER JOIN "$schema"."Reaches" USING ("RiverID")
    ORDER BY
        "Name" ASC;
    QUERY;
}
echo $sql;

$result = pg_query($pgsql_connection, $sql);
echo '<option value="" selected disabled>Select Reach</option>';


switch ($_POST['BasinID']) {
    case "1":
        echo <<<EOT
        <!-- <option disabled>-CRITFC Interest-</option> -->
        <option value="155">Below Bonneville Dam</option>
        <option value="226">Below Chief Joseph Dam</option>
        <option value="235">Below Grand Coulee Dam</option>
        <option value="826">Below Hells Canyon Dam</option>
        <option value="167">Below John Day Dam</option>
        <option value="180">Below McNary Dam</option>
        <option value="200">Below Priest Rapids Dam</option>
        <option value="210">Below Rock Island Dam</option>
        <option value="213">Below Rocky Reach Dam</option>
        <option value="163">Below The Dalles Dam</option>
        <option value="66">Below US/Canada Border (Columbia)</option>
        <option value="202">Below Wanapum Dam</option>
        <option value="221">Below Wells Dam</option>
        <option value="807">Clearwater River Confluence</option>
        <option value="54">Cowlitz Confluence (Columbia)</option>
        <option value="249">Cowlitz Confluence (Cowlitz)</option>
        <option value="166">Deschutes River Confluence (Columbia)</option>
        <option value="274">Deschutes River Confluence (Deschutes)</option>
        <option value="159">Hood River Confluence (Columbia)</option>
        <option value="363">Hood River Confluence (Hood)</option>
        <option value="161">Klickitat River Confluence (Columbia)</option>
        <option value="488">Klickitat River Confluence (Klickitat)</option>
        <option value="158">L. White Salmon Confluence (Columbia)</option>
        <option value="605">L. White Salmon Confluence (LWS)</option>
        <option value="188">Snake River Confluence (Columbia)</option>
        <option value="717">Snake River Confluence (Snake)</option>
        <option value="181">Umatilla River Confluence (Columbia)</option>
        <option value="929">Umatilla River Confluence (Umatilla)</option>
        <option value="159">White Salmon Confluence (Columbia)</option>
        <option value="977">White Salmon Confluence (W. Salmon)</option>
        <option value="157">Wind River Confluence</option>
        <option value="189">Yakima River Confluence (Columbia)</option>
        <option value="1020">Yakima River Confluence (Yakima)</option>
        <option disabled>---</option>
        EOT;
        break;
}

if (pg_num_rows($result) > 0) {
    // output data of each row
    while ($row = pg_fetch_assoc($result)) {
        echo "<option value=" . $row["ReachID"] . ">" . $row["Name"] . "</option>";
    }
}

pg_close($pgsql_connection);
