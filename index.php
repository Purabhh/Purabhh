<?php
// Database credentials
$servername = "localhost";
$username = "root";
$password = "griezmann7";
$dbname = "sakila";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// SQL query to select data from the specific table
$sql = "SELECT * FROM purabh";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // Output data of each row
    echo "<table border='1'>
            <tr>";
    // Fetch field names and print table headers
    $field_info = $result->fetch_fields();
    foreach ($field_info as $field) {
        echo "<th>" . $field->name . "</th>";
    }
    echo "</tr>";

    // Fetch rows and print table data
    while($row = $result->fetch_assoc()) {
        echo "<tr>";
        foreach ($row as $data) {
            echo "<td>" . $data . "</td>";
        }
        echo "</tr>";
    }
    echo "</table>";
} else {
    echo "0 results";
}
$conn->close();
?>
