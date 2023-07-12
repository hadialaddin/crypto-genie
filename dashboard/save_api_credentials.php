<?php
	if($_POST["api_key"] && $_POST["api_secret"]){
		setcookie("api_key", $_POST['api_key'], time() + (10 * 365 * 24 * 60 * 60));
		setcookie("api_secret", $_POST['api_secret'], time() + (10 * 365 * 24 * 60 * 60));
	}
?>