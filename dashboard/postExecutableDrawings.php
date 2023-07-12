<?php
	# MySQL Database Connection Configuration
	include("config.php");
	// Create connection
	$conn = new mysqli(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME);
	// Check connection
	if ($conn->connect_error) {
	  die("Connection failed: " . $conn->connect_error);
	}

	if($_POST["api_key"] && $_POST["api_secret"] && $_POST["symbol"] && $_POST["type"] && $_POST["x1"] && $_POST["y1"] && $_POST["x2"] && $_POST["y2"]){
		// prepare, bind and execute MySQL
		$stmt = $conn->prepare("INSERT INTO executable_drawings (api_key, api_secret, symbol, type, x1, y1, x2, y2) VALUES (?, ?, ?, ?, ?, ?, ?, ?)");
		$stmt->bind_param("sssidddd", $_POST["api_key"], $_POST["api_secret"], $_POST["symbol"], $_POST["type"], $_POST["x1"], $_POST["y1"], $_POST["x2"], $_POST["y2"]);
		$stmt->execute();
		// close connection
		$stmt->close();
		$conn->close();
	}
?>