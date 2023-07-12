<?php
	# MySQL Database Connection Configuration
	include("config.php");
	// Create connection
	$conn = new mysqli(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME);
	// Check connection
	if ($conn->connect_error) {
	  die("Connection failed: " . $conn->connect_error);
	}

	if($_POST["api_key"] && $_POST["api_secret"] && $_POST["symbol"] && $_POST["side"] && $_POST["amount"] && $_POST["orderCount"] && $_POST["priceLower"] && $_POST["priceUpper"] && $_POST["ordertype"] && $_POST["orderExec"]){
		setcookie("api_key", $_POST['api_key'], time() + (10 * 365 * 24 * 60 * 60));
		setcookie("api_secret", $_POST['api_secret'], time() + (10 * 365 * 24 * 60 * 60));
		setcookie("symbol", $_POST['symbol'], time() + (10 * 365 * 24 * 60 * 60));
		setcookie("amount", $_POST['amount'], time() + (10 * 365 * 24 * 60 * 60));
		setcookie("orderCount", $_POST['orderCount'], time() + (10 * 365 * 24 * 60 * 60));
		setcookie("priceLower", $_POST['priceLower'], time() + (10 * 365 * 24 * 60 * 60));
		setcookie("priceUpper", $_POST['priceUpper'], time() + (10 * 365 * 24 * 60 * 60));
		setcookie("ordertype", $_POST['ordertype'], time() + (10 * 365 * 24 * 60 * 60));
		setcookie("orderExec", $_POST['orderExec'], time() + (10 * 365 * 24 * 60 * 60));
		// prepare, bind and execute MySQL
		$stmt = $conn->prepare("INSERT INTO scaled_orders (api_key, api_secret, symbol, side, amount, orderCount, priceLower, priceUpper, ordertype, orderExec) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
		$stmt->bind_param("ssssdiddss", $_POST["api_key"], $_POST["api_secret"], $_POST["symbol"], $_POST["side"], $_POST["amount"], $_POST["orderCount"], $_POST["priceLower"], $_POST["priceUpper"], $_POST["ordertype"], $_POST["orderExec"]);
		$stmt->execute();
		// close connection
		$stmt->close();
		$conn->close();
	}
?>