<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
	# MySQL Database Connection Configuration
	include("config.php");
	// Create connection
	$conn = new mysqli(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME);
	// Check connection
	if ($conn->connect_error) {
	  die("Connection failed: " . $conn->connect_error);
	}
	
	if($_GET["api_key"] && $_GET["api_secret"] && $_GET["symbol"]){
	  echo '<h1><span style="color: purple;">'.$_GET['symbol'].'</span></h1>';
	  $query = "SELECT * FROM exit_strategies WHERE api_key=? AND api_secret=? AND symbol=?";
	  $stmt = $conn->prepare($query);
	  $stmt->bind_param("sss", $_GET["api_key"], $_GET["api_secret"], $_GET["symbol"]);
	  $stmt->execute();
	  $result = $stmt->get_result();
	  $result = $result->fetch_all(MYSQLI_ASSOC);
	  
	  foreach($result as $row)
	  {
		if (!is_null($row['tb_hedge_sl_static_cap_ratio_override']) && $row['tb_hedge_sl_static_cap_ratio_override']>0 && $row['tb_hedge_sl_static_cap_ratio_override']!='')
		{
			$query2 = "SELECT * FROM positions_sessions WHERE api_key=? AND api_secret=? AND symbol=?";
			$stmt2 = $conn->prepare($query2);
			$stmt2->bind_param("sss", $_GET["api_key"], $_GET["api_secret"], $_GET["symbol"]);
			$stmt2->execute();
			$result2 = $stmt2->get_result();
			
			if ($result2->num_rows > 0){
				$result2 = $result2->fetch_all(MYSQLI_ASSOC);
				
				foreach($result2 as $row2)
				{
					if (is_null($row2['last_balanced_equity']))
						$last_balanced_equity = 0;
					else
						$last_balanced_equity = $row2['last_balanced_equity'];
						
						
					if (is_null($row2['highest_equity']))
						$highest_equity = 0;
					else
						$highest_equity = $row2['highest_equity'];
					
					
					if ($highest_equity > $last_balanced_equity)
						$target_tb_hedge_sl_loss_value = $highest_equity * $row['tb_hedge_sl_static_cap_ratio_override']/100;
					else
						$target_tb_hedge_sl_loss_value = $last_balanced_equity * $row['tb_hedge_sl_static_cap_ratio_override']/100;
									
					if ($highest_equity > $last_balanced_equity)
						$tb_sl = $highest_equity - $target_tb_hedge_sl_loss_value;
					else
						$tb_sl = $last_balanced_equity - $target_tb_hedge_sl_loss_value;
					
					if ($row2['current_long_pos_size'] !=  $row2['current_short_pos_size']){
						$size_diff = $row2['current_long_pos_size'] - $row2['current_short_pos_size'];
						if($size_diff > 0){
							// Net Longs
							$position_value_diff = abs($row2['current_long_pos_value'] - $row2['current_short_pos_value']);
							echo '<span><h1>Net LONGS: ' . $size_diff . '</h1></span>';
							$target_tb_sl_ratio = (($row2['realtime_equity'] - $tb_sl) * 100) / $position_value_diff;
							$target_tb_sl_ratio = number_format((float)$target_tb_sl_ratio, 2, '.', '');
							if (($row2['realtime_price'] - (($target_tb_sl_ratio/100) * $row2['realtime_price'])) > 0 )
								echo '<h1>TB SL <span style="color: red;">&#8595; $' . ($row2['realtime_price'] - (($target_tb_sl_ratio/100) * $row2['realtime_price'])) . '</span> &nbsp; &nbsp; &nbsp; &nbsp; ('. $target_tb_sl_ratio . '% from here).</h1>';
							else
								echo '<h1>TB SL <span style="color: red;">&#8595; Out of range</span> &nbsp; &nbsp; &nbsp; &nbsp; ('. $target_tb_sl_ratio . '% from here).</h1>';
						}
						else{
							// Net Shorts
							$position_value_diff = abs($row2['current_short_pos_value'] - $row2['current_long_pos_value']);
							echo '<span><h1>Net SHORTS: ' . abs($size_diff) . '</h1></span>';
							$target_tb_sl_ratio = (($row2['realtime_equity'] - $tb_sl) * 100) / $position_value_diff;
							$target_tb_sl_ratio = number_format((float)$target_tb_sl_ratio, 2, '.', '');
							if (($row2['realtime_price'] + (($target_tb_sl_ratio/100) * $row2['realtime_price'])) > 0 )
								echo '<h1>TB SL <span style="color: green;">&#8593; $' . ($row2['realtime_price'] + (($target_tb_sl_ratio/100) * $row2['realtime_price'])) . '</span> &nbsp; &nbsp; &nbsp; &nbsp; ('. $target_tb_sl_ratio . '% from here).</h1>';
							else
								echo '<h1>TB SL <span style="color: green;">&#85935; Out of range</span> &nbsp; &nbsp; &nbsp; &nbsp; ('. $target_tb_sl_ratio . '% from here).</h1>';
						}
							
						echo '<h1>Total Balance SL at <span>: $' . number_format($tb_sl) . '</span></h1>';
					}
					else
						echo '<h1><span style="color: orange;">Totally Hedged (equal position sizes)</span></h1>';

				}
			}
			
			else{
				echo '<h1>No active positions.</h1>';
			}
		}

	  }
		// close connection
		$stmt2->close();
		$stmt->close();
		$conn->close();
		
	}
?>