<?php
	# MySQL Database Connection Configuration
	include("config.php");
	// Create connection
	$conn = new mysqli(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME);
	// Check connection
	if ($conn->connect_error) {
	  die("Connection failed: " . $conn->connect_error);
	}
	
	if($_GET["command_type"]=="GET" && $_GET["api_key"] && $_GET["api_secret"]){
	  $query = "SELECT id,symbol,tp_type,tp_target_long,tp_target_short,tp_target_type,tp_all_or_none,tp_enforce_all_time,tp_enforce_maxrange,sl_target_long,sl_target_short,sl_trailing_targets_long,sl_trailing_targets_short,sl_target_type,tb_initial_sl_static_cap_ratio_buy_override,tb_initial_sl_static_pos_size_ratio_buy_override,tb_sl_static_cap_ratio_buy_override,tb_sl_static_pos_size_ratio_buy_override,tb_initial_sl_static_cap_ratio_sell_override,tb_initial_sl_static_pos_size_ratio_sell_override,tb_sl_static_cap_ratio_sell_override,tb_sl_static_pos_size_ratio_sell_override,tb_hedge_cap_ratio_buy_override,tb_hedge_pos_size_ratio_buy_override,tb_hedge_cap_ratio_sell_override,tb_hedge_pos_size_ratio_sell_override,tb_hedge_balancer_cap_ratio_override,tb_hedge_sl_static_cap_ratio_override,tp_after_hedge,sl_after_hedge,reset_refresh_rate FROM exit_strategies WHERE api_key=? AND api_secret=? ORDER BY id DESC";
	  $stmt = $conn->prepare($query);
	  $stmt->bind_param("ss", $_GET["api_key"], $_GET["api_secret"]);
	  $stmt->execute();
	  $result = $stmt->get_result();
	  $result = $result->fetch_all(MYSQLI_ASSOC);
	  
	  foreach($result as $row)
	  {
		$output[] = array(
		 'id'    => $row['id'],   
		 'symbol'  => $row['symbol'],
		 'tp_type'   => $row['tp_type'],
		 'tp_target_long'    => $row['tp_target_long'],
		 'tp_target_short'    => $row['tp_target_short'],
		 'tp_target_type'   => $row['tp_target_type'],
		 'tp_all_or_none'   => $row['tp_all_or_none'],
		 'tp_enforce_all_time'   => $row['tp_enforce_all_time'],
		 'tp_enforce_maxrange'   => $row['tp_enforce_maxrange'],
		 'sl_target_long'   => $row['sl_target_long'],
		 'sl_target_short'   => $row['sl_target_short'],
		 'sl_trailing_targets_long'   => $row['sl_trailing_targets_long'],
		 'sl_trailing_targets_short'   => $row['sl_trailing_targets_short'],
		 'sl_target_type'   => $row['sl_target_type'],
		 'tb_initial_sl_static_cap_ratio_buy_override'   => $row['tb_initial_sl_static_cap_ratio_buy_override'],
		 'tb_initial_sl_static_pos_size_ratio_buy_override'   => $row['tb_initial_sl_static_pos_size_ratio_buy_override'],
		 'tb_sl_static_cap_ratio_buy_override'   => $row['tb_sl_static_cap_ratio_buy_override'],
		 'tb_sl_static_pos_size_ratio_buy_override'   => $row['tb_sl_static_pos_size_ratio_buy_override'],
		 'tb_initial_sl_static_cap_ratio_sell_override'   => $row['tb_initial_sl_static_cap_ratio_sell_override'],
		 'tb_initial_sl_static_pos_size_ratio_sell_override'   => $row['tb_initial_sl_static_pos_size_ratio_sell_override'],
		 'tb_sl_static_cap_ratio_sell_override'   => $row['tb_sl_static_cap_ratio_sell_override'],
		 'tb_sl_static_pos_size_ratio_sell_override'   => $row['tb_sl_static_pos_size_ratio_sell_override'],
		 'tb_hedge_cap_ratio_buy_override'   => $row['tb_hedge_cap_ratio_buy_override'],
		 'tb_hedge_pos_size_ratio_buy_override'   => $row['tb_hedge_pos_size_ratio_buy_override'],
		 'tb_hedge_cap_ratio_sell_override'   => $row['tb_hedge_cap_ratio_sell_override'],
		 'tb_hedge_pos_size_ratio_sell_override'   => $row['tb_hedge_pos_size_ratio_sell_override'],
		 'tb_hedge_balancer_cap_ratio_override'   => $row['tb_hedge_balancer_cap_ratio_override'],
		 'tb_hedge_sl_static_cap_ratio_override'   => $row['tb_hedge_sl_static_cap_ratio_override'],
		 'tp_after_hedge'   => $row['tp_after_hedge'],
		 'sl_after_hedge'   => $row['sl_after_hedge'],
		 'reset_refresh_rate'   => $row['reset_refresh_rate']
		);
	  }
		// close connection
		$stmt->close();
		$conn->close();
	  header("Content-Type: application/json");
		echo json_encode($output);
	}
	
	else if($_GET["command_type"]=="INSERT" && $_GET["api_key"] && $_GET["api_secret"]){
	  if($_POST['tp_all_or_none'] == 'true')
		 $tp_all_or_none = 1;
	  else
		 $tp_all_or_none = 0;
	 
	  if($_POST['tp_enforce_all_time'] == 'true')
		 $tp_enforce_all_time = 1;
	  else
		 $tp_enforce_all_time = 0;
	 
	  if($_POST['tp_enforce_maxrange'] == 'true')
		 $tp_enforce_maxrange = 1;
	  else
		 $tp_enforce_maxrange = 0;
	 
	  if($_POST['tp_after_hedge'] == 'true')
		 $tp_after_hedge = 1;
	  else
		 $tp_after_hedge = 0;
	 
	  if($_POST['sl_after_hedge'] == 'true')
		 $sl_after_hedge = 1;
	  else
		 $sl_after_hedge = 0;
	 
	  $query = "INSERT INTO exit_strategies(api_key,api_secret,symbol,tp_type,tp_target_long,tp_target_short,tp_target_type,tp_all_or_none,tp_enforce_all_time,tp_enforce_maxrange,sl_target_long,sl_target_short,sl_trailing_targets_long,sl_trailing_targets_short,sl_target_type,tb_initial_sl_static_cap_ratio_buy_override,tb_initial_sl_static_pos_size_ratio_buy_override,tb_sl_static_cap_ratio_buy_override,tb_sl_static_pos_size_ratio_buy_override,tb_initial_sl_static_cap_ratio_sell_override,tb_initial_sl_static_pos_size_ratio_sell_override,tb_sl_static_cap_ratio_sell_override,tb_sl_static_pos_size_ratio_sell_override,tb_hedge_cap_ratio_buy_override,tb_hedge_pos_size_ratio_buy_override,tb_hedge_cap_ratio_sell_override,tb_hedge_pos_size_ratio_sell_override,tb_hedge_balancer_cap_ratio_override,tb_hedge_sl_static_cap_ratio_override,tp_after_hedge,sl_after_hedge,reset_refresh_rate) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
	  $stmt = $conn->prepare($query);
	  $stmt->bind_param("sssssssiiiddsssddddddddddddddiii", $_GET["api_key"], $_GET["api_secret"], $_POST['symbol'], $_POST['tp_type'], $_POST['tp_target_long'], $_POST['tp_target_short'], $_POST['tp_target_type'], $tp_all_or_none, $tp_enforce_all_time, $tp_enforce_maxrange, $_POST['sl_target_long'], $_POST['sl_target_short'], $_POST['sl_trailing_targets_long'], $_POST['sl_trailing_targets_short'], $_POST['sl_target_type'], $_POST['tb_initial_sl_static_cap_ratio_buy_override'], $_POST['tb_initial_sl_static_pos_size_ratio_buy_override'], $_POST['tb_sl_static_cap_ratio_buy_override'], $_POST['tb_sl_static_pos_size_ratio_buy_override'], $_POST['tb_initial_sl_static_cap_ratio_sell_override'], $_POST['tb_initial_sl_static_pos_size_ratio_sell_override'], $_POST['tb_sl_static_cap_ratio_sell_override'], $_POST['tb_sl_static_pos_size_ratio_sell_override'], $_POST['tb_hedge_cap_ratio_buy_override'], $_POST['tb_hedge_pos_size_ratio_buy_override'], $_POST['tb_hedge_cap_ratio_sell_override'], $_POST['tb_hedge_pos_size_ratio_sell_override'], $_POST['tb_hedge_balancer_cap_ratio_override'], $_POST['tb_hedge_sl_static_cap_ratio_override'], $tp_after_hedge, $sl_after_hedge, $_POST['reset_refresh_rate']);
	  $stmt->execute();
	}
	
	else if($_GET["command_type"]=="UPDATE" && $_GET["api_key"] && $_GET["api_secret"]){
	  if($_POST['tp_all_or_none'] == 'true')
		 $tp_all_or_none = 1;
	  else
		 $tp_all_or_none = 0;
	 
	  if($_POST['tp_enforce_all_time'] == 'true')
		 $tp_enforce_all_time = 1;
	  else
		 $tp_enforce_all_time = 0;
	 
	  if($_POST['tp_enforce_maxrange'] == 'true')
		 $tp_enforce_maxrange = 1;
	  else
		 $tp_enforce_maxrange = 0;
	 
	  if($_POST['tp_after_hedge'] == 'true')
		 $tp_after_hedge = 1;
	  else
		 $tp_after_hedge = 0;
	 
	  if($_POST['sl_after_hedge'] == 'true')
		 $sl_after_hedge = 1;
	  else
		 $sl_after_hedge = 0;
	 
	  $query = "UPDATE exit_strategies SET tp_type=?, tp_target_long=?, tp_target_short=?, tp_target_type=?, tp_all_or_none=?, tp_enforce_all_time=?, tp_enforce_maxrange=?, sl_target_long=?, sl_target_short=?, sl_trailing_targets_long=?, sl_trailing_targets_short=?, sl_target_type=?, tb_initial_sl_static_cap_ratio_buy_override=?, tb_initial_sl_static_pos_size_ratio_buy_override=?, tb_sl_static_cap_ratio_buy_override=?, tb_sl_static_pos_size_ratio_buy_override=?, tb_initial_sl_static_cap_ratio_sell_override=?, tb_initial_sl_static_pos_size_ratio_sell_override=?, tb_sl_static_cap_ratio_sell_override=?, tb_sl_static_pos_size_ratio_sell_override=?, tb_hedge_cap_ratio_buy_override=?, tb_hedge_pos_size_ratio_buy_override=?, tb_hedge_cap_ratio_sell_override=?, tb_hedge_pos_size_ratio_sell_override=?, tb_hedge_balancer_cap_ratio_override=?, tb_hedge_sl_static_cap_ratio_override=?, tp_after_hedge=?, sl_after_hedge=?, reset_refresh_rate=? WHERE api_key=? AND api_secret=? AND symbol=?";
	  $stmt = $conn->prepare($query);
	  $stmt->bind_param("ssssiiiddsssddddddddddddddiiisss", $_POST['tp_type'], $_POST['tp_target_long'], $_POST['tp_target_short'], $_POST['tp_target_type'], $tp_all_or_none, $tp_enforce_all_time, $tp_enforce_maxrange, $_POST['sl_target_long'], $_POST['sl_target_short'], $_POST['sl_trailing_targets_long'], $_POST['sl_trailing_targets_short'], $_POST['sl_target_type'], $_POST['tb_initial_sl_static_cap_ratio_buy_override'], $_POST['tb_initial_sl_static_pos_size_ratio_buy_override'], $_POST['tb_sl_static_cap_ratio_buy_override'], $_POST['tb_sl_static_pos_size_ratio_buy_override'], $_POST['tb_initial_sl_static_cap_ratio_sell_override'], $_POST['tb_initial_sl_static_pos_size_ratio_sell_override'], $_POST['tb_sl_static_cap_ratio_sell_override'], $_POST['tb_sl_static_pos_size_ratio_sell_override'], $_POST['tb_hedge_cap_ratio_buy_override'], $_POST['tb_hedge_pos_size_ratio_buy_override'], $_POST['tb_hedge_cap_ratio_sell_override'], $_POST['tb_hedge_pos_size_ratio_sell_override'], $_POST['tb_hedge_balancer_cap_ratio_override'], $_POST['tb_hedge_sl_static_cap_ratio_override'], $tp_after_hedge, $sl_after_hedge, $_POST['reset_refresh_rate'], $_GET["api_key"], $_GET["api_secret"], $_POST["symbol"]);
	  $stmt->execute();
	}
	
	else if($_GET["command_type"]=="DELETE" && $_GET["api_key"] && $_GET["api_secret"]){
		
	  $query = "DELETE FROM exit_strategies WHERE api_key=? AND api_secret=? AND symbol=?";
	  $stmt = $conn->prepare($query);
	  $stmt->bind_param("sss", $_GET["api_key"], $_GET["api_secret"], $_POST['symbol']);
	  $stmt->execute();
	}
?>