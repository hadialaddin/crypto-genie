<!DOCTYPE html>
<html>
<head>
	<title>Crypto Genie - Dashboard</title>
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" integrity="sha512-Fo3rlrZj/k7ujTnHg4CGR2D7kSs0v4LLanw2qksYuRlEzO+tcaEPQogQ0KaoGN26/zrn20ImR1DfuLWnOo7aBA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
	<link type="text/css" rel="stylesheet" href="js/jsgrid/jsgrid.min.css" />
	<link type="text/css" rel="stylesheet" href="js/jsgrid/jsgrid-theme.min.css" />
	<style>
		.hide
		{
			display:none;
		}
	</style>
</head>
<body>
	<div class="container">
		<div class="row mb-3">
			<div class="col-md-12"><img src="CryptoGenie_Logo_Transparent.png" style="width: 200px;" /></div>
		</div>
		<div class="row mb-3">
			<div class="col-md-12"><h2>Dashboard</h2></div>
		</div>
		
		<form id="scaledOrdersForm" action="postScaledOrders.php" method="POST" class="form-horizontal needs-validation">
			<div class="accordion" id="accordion">
			  <div class="accordion-item">
				<h2 class="accordion-header" id="apiCredentialsHeader">
				  <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#apiCredentialsCollapse" aria-expanded="true" aria-controls="apiCredentialsCollapse">
					<h6>API Credentials</h6>
				  </button>
				</h2>
				<div id="apiCredentialsCollapse" class="accordion-collapse collapse show" aria-labelledby="apiCredentialsHeader">
				  <div class="accordion-body">
					<div id="api-group" class="form-group row alert alert-primary">
						<label for="api_key" class="font-weight-bold">API Key</label>
						<input type="text" class="form-control" id="api_key" name="api_key" placeholder="API Key" value="<?php echo isset($_COOKIE['api_key']) ? $_COOKIE['api_key'] : ''; ?>" required>

						<label for="api_key" class="font-weight-bold">API Secret</label>
						<input type="text" class="form-control" id="api_secret" name="api_secret" placeholder="API Secret" value="<?php echo isset($_COOKIE['api_secret']) ? $_COOKIE['api_secret'] : ''; ?>" required>
					</div>
					<input type="button" class="saveApiCredentials btn btn-success" id="saveApiCredentials" value="Save" /><br />
					<div id="saveApiCredentialsSuccess" class="alert alert-warning" style="display: none;">API Credentials saved</div>
				  </div>
				</div>
			  </div>
			  <!--
			  <div class="accordion-item">
				<h2 class="accordion-header" id="autoTraderHeader">
				  <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#autoTraderCollapse" aria-expanded="true" aria-controls="autoTraderCollapse">
					<h6>Auto Trader Charts</h6>
				  </button>
				</h2>
				<div id="autoTraderCollapse" class="accordion-collapse collapse show" aria-labelledby="autoTraderHeader">
				  <div class="accordion-body">
					 <div class="form-group row mb-3">
						<div class="col-md-1"></div>
						<div class="col-md-2"><img id="autoTraderChartImg0" src="chart_timewindow0.png?m=<?php echo filemtime('chart_timewindow0.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg1" src="chart_timewindow1.png?m=<?php echo filemtime('chart_timewindow1.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg2" src="chart_timewindow2.png?m=<?php echo filemtime('chart_timewindow2.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg3" src="chart_timewindow3.png?m=<?php echo filemtime('chart_timewindow3.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg4" src="chart_timewindow4.png?m=<?php echo filemtime('chart_timewindow4.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-1"></div>
					 </div>
					 <div class="form-group row mb-3">
						<div class="col-md-2"><img id="autoTraderChartImg5" src="chart_timewindow5.png?m=<?php echo filemtime('chart_timewindow5.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg6" src="chart_timewindow6.png?m=<?php echo filemtime('chart_timewindow6.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg7" src="chart_timewindow7.png?m=<?php echo filemtime('chart_timewindow7.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg8" src="chart_timewindow8.png?m=<?php echo filemtime('chart_timewindow8.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg9" src="chart_timewindow9.png?m=<?php echo filemtime('chart_timewindow9.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg10" src="chart_timewindow10.png?m=<?php echo filemtime('chart_timewindow10.png'); ?>" class="img-fluid autoFix"></div>
					 </div>
					 <div class="form-group row mb-3">
						<div class="col-md-2"><img id="autoTraderChartImg11" src="chart_timewindow11.png?m=<?php echo filemtime('chart_timewindow11.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg12" src="chart_timewindow12.png?m=<?php echo filemtime('chart_timewindow12.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg13" src="chart_timewindow13.png?m=<?php echo filemtime('chart_timewindow13.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg14" src="chart_timewindow14.png?m=<?php echo filemtime('chart_timewindow14.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg15" src="chart_timewindow15.png?m=<?php echo filemtime('chart_timewindow15.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg16" src="chart_timewindow16.png?m=<?php echo filemtime('chart_timewindow16.png'); ?>" class="img-fluid autoFix"></div>
					 </div>
					 <div class="form-group row mb-3">
						<div class="col-md-2"><img id="autoTraderChartImg17" src="chart_timewindow17.png?m=<?php echo filemtime('chart_timewindow17.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg18" src="chart_timewindow18.png?m=<?php echo filemtime('chart_timewindow18.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg19" src="chart_timewindow19.png?m=<?php echo filemtime('chart_timewindow19.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg20" src="chart_timewindow20.png?m=<?php echo filemtime('chart_timewindow20.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg21" src="chart_timewindow21.png?m=<?php echo filemtime('chart_timewindow21.png'); ?>" class="img-fluid autoFix"></div>
						<div class="col-md-2"><img id="autoTraderChartImg22" src="chart_timewindow22.png?m=<?php echo filemtime('chart_timewindow22.png'); ?>" class="img-fluid autoFix"></div>
					 </div>
					</div>
				  </div>
				</div>
				-->
				<div class="accordion-item">
				<h2 class="accordion-header" id="scaledOrdersHeader">
				  <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#scaledOrdersCollapse" aria-expanded="true" aria-controls="scaledOrdersCollapse">
					<h6>Scaled Orders</h6>
				  </button>
				</h2>
				<div id="scaledOrdersCollapse" class="accordion-collapse collapse show" aria-labelledby="scaledOrdersHeader">
				  <div class="accordion-body">
					<div class="row mb-3">
						<div class="col-md-12"><button type="button" class="btn btn-dark" id="toggleVoice" data-toggle="tooltip" data-placement="top" title="Click on a field and dictate, or say 'Buy' / 'Sell' to submit.">Enable Voice Commands <i class="fa fa-microphone"></i></button></div>
					</div>
					<br />
					<div class="form-group row mb-3">
						<label for="symbol"  class="col-md-2 control-label font-weight-bold"><b>Symbol (Instrument)</b></label>
						<div class="col-md-4"><input type="text" class="form-control" id="symbol" name="symbol" placeholder="Eg. BTCUSDT" value="<?php echo isset($_COOKIE['symbol']) ? $_COOKIE['symbol'] : ''; ?>" required></div>
						
						<label for="ordertype"  class="col-md-2 control-label font-weight-bold"><b>Order Type</b></label>
						<div class="col-md-4">
							<select class="form-control" id="ordertype" name="ordertype">
							  <option value="Limit" selected>Limit</option>
							</select>
						</div>
					</div>
					<div class="form-group row mb-3">
						<label for="amount" class="col-md-2 control-label font-weight-bold"><b>Amount</b></label>
						<div class="col-md-4"><input type="text" class="form-control" id="amount" name="amount" placeholder="Total size (quantity) of all orders" value="<?php echo isset($_COOKIE['amount']) ? $_COOKIE['amount'] : ''; ?>" required></div>
						
						<label for="orderCount" class="col-md-2 control-label font-weight-bold"><b>Orders Count</b></label>
						<div class="col-md-4"><input type="number" class="form-control" id="orderCount" name="orderCount" placeholder="Number of orders to be distributed over" value="<?php echo isset($_COOKIE['orderCount']) ? $_COOKIE['orderCount'] : ''; ?>" min="2" max="200" step="1" required></div>
					</div>
					<div class="form-group row mb-3">
						<label for="priceLower" class="col-md-2 control-label font-weight-bold"><b>Lower Price</b></label>
						<div class="col-md-4"><input type="text" class="form-control" id="priceLower" name="priceLower" placeholder="" value="<?php echo isset($_COOKIE['priceLower']) ? $_COOKIE['priceLower'] : ''; ?>" required></div>
						
						<label for="priceUpper" class="col-md-2 control-label font-weight-bold"><b>Upper Price</b></label>
						<div class="col-md-4"><input type="text" class="form-control" id="priceUpper" name="priceUpper" placeholder="" value="<?php echo isset($_COOKIE['priceUpper']) ? $_COOKIE['priceUpper'] : ''; ?>" required></div>
					</div>
					
					<div class="form-group row mb-3">
						<div class="col-md-2"></div>
						<div class="col-md-4"></div>
						<div class="col-md-2"></div>
						<div class="col-md-4">
							<input type="submit" onclick="this.form.side='Buy';this.form.orderExec='Open';" class="submitScaledOrders btn btn-success" id="OpenLongButton" value="Open Long" />
							<input type="submit" onclick="this.form.side='Sell';this.form.orderExec='Open';" class="submitScaledOrders btn btn-danger" id="OpenShortButton" value="Open Short"/><br /><br />
							<input type="submit" onclick="this.form.side='Sell';this.form.orderExec='Close';" class="submitScaledOrders btn btn-outline-danger" id="CloseLongButton" value="Close Long" />
							<input type="submit" onclick="this.form.side='Buy';this.form.orderExec='Close';" class="submitScaledOrders btn btn-outline-success" id="CloseShortButton" value="Close Short"/>
							<br /><br />
							<div id="ordersSuccess" class="alert alert-warning" style="display: none;">Orders Submitted</div>
						</div>
						
					</div>
				  </div>
				</div>
				</div>
			  <!--
				  <div class="accordion-item">
					<h2 class="accordion-header" id="tvChartHeader">
					  <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#tvChartCollapse" aria-expanded="true" aria-controls="tvChartCollapse">
						<h6>Executable Drawings</h6>
					  </button>
					</h2>
					<div id="tvChartCollapse" class="accordion-collapse collapse show" aria-labelledby="tvChartHeader">
					  <div class="accordion-body">
						<input type="button" class="submitExecutableDrawings btn btn-success" id="submitExecutableDrawings" value="Submit Drawings" />
						<div id="tv_chart_container">
						</div>
					  </div>
					</div>
				  </div>
			  -->
			  
			  <div class="accordion-item">
				<h2 class="accordion-header" id="jsgridHeader"></h2>
				  <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#jsgridCollapse" aria-expanded="true" aria-controls="jsgridCollapse">
					<h6>Exit Strategies</h6>
				  </button>
				</h2>
				
				<div id="jsgridCollapse" class="accordion-collapse collapse show" aria-labelledby="jsgridHeader">
				  <div class="accordion-body">
					<div class="table-responsive">  
						<br />
						<h5 align="left">Insert or Edit your Exit Strategies for each asset</h5><br />
						
						<div class="alert alert-info" role="alert">
							<b>TP Target Values</b> format: <b>price_level_1 : qty_to_close_as_ratio_1 ; price_level_2 : qty_to_close_as_ratio_2 ; .....</b><br />
							Eg. <b>5 : 30 ; 15 : 40; 30 : 100 ;</b> would close 30% of position size when 5% level hit, 40% of position size when 15% hit and remaining of position when 30% is hit. If <b>Add TPs All or None</b> is selected too, Orders will be placed all together, otherwise one by one and the ratios of the position size will be calculated after each level is hit of the remainder of the position. If <b>TPs Enforce All Time</b> is selected, it will make sure to refresh the levels and quantities according to the position's size and entry price if it changes while TPs already exist, othrewise it will only place the TPs if none exists and will not refresh anything until all TPs are removed or hit.<br /><br />

							<b>SL Trailing Target Values</b> format: <b>price_level_1_reached : move_sl_to_price_level_a ; price_level_2_reached : move_sl_to_price_level_b ; ....</b><br />
							Eg. <b>10 : -5 ; 20 : 2 ; 30 : 10 ;</b> would move the SL to -5% when price reaches 10%, then to 2% (in profit) when price reaches 20% and finally 10% (in profit) when price reaches 30%.<br />
							<br />
						</div>
						<div id="exit_strategies_grid"></div>
					</div> 
				  </div>
				</div>
			  </div>
			</div>
			<br />
		</form>
	</div>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
<!-- <script type="text/javascript" src="charting_library_clonned_data/charting_library/charting_library.js"></script> -->
<!-- <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/1.7.2/socket.io.js"></script> -->
<script type="text/javascript" src="js/jsgrid/jsgrid.min.js"></script>
<!-- Custom datafeed module. -->
<script>

var crosshairValues=new Array; // Array used to store Crosshair Values of the Executable Drawings (X and Y coordinates of each click)

$(document).ready(function(){
  'use strict'

  $('[data-toggle="tooltip"]').tooltip(); // Activate Bootstrap Tooltips
  
  $('img.autoFix').on( "error", function(){
      var src = this.src;
      this.src = src.substr(0, src.indexOf('?')) + '?m=' + new Date().getTime();
  });
	
	// Save API Credentials to Cookies
	$('input#saveApiCredentials').click(function() {
		// Send AJAX call to server
		var btn = $(this)
		btn.attr("disabled", true);
		// Assign handlers immediately after making the request,
		// and remember the jqxhr object for this request
		var data = "api_key=" + $( "input#api_key" ).val() + "&api_secret=" + $( "input#api_secret" ).val();
		var jqxhr = $.post( "save_api_credentials.php", data, function( ) {})
		  .always(function() {
			btn.attr("disabled", false);
			$('#saveApiCredentialsSuccess').show(0).delay(2000).hide(0);
		  });
	})

  
  /*
  setInterval(function(){
	  $("#autoTraderChartImg0").attr("src", "./chart_timewindow0.png?m=?"+new Date().getTime());
      $("#autoTraderChartImg1").attr("src", "./chart_timewindow1.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg2").attr("src", "./chart_timewindow2.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg3").attr("src", "./chart_timewindow3.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg4").attr("src", "./chart_timewindow4.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg5").attr("src", "./chart_timewindow5.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg6").attr("src", "./chart_timewindow6.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg7").attr("src", "./chart_timewindow7.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg8").attr("src", "./chart_timewindow8.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg9").attr("src", "./chart_timewindow9.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg10").attr("src", "./chart_timewindow10.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg11").attr("src", "./chart_timewindow11.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg12").attr("src", "./chart_timewindow12.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg13").attr("src", "./chart_timewindow13.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg14").attr("src", "./chart_timewindow14.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg15").attr("src", "./chart_timewindow15.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg16").attr("src", "./chart_timewindow16.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg17").attr("src", "./chart_timewindow17.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg18").attr("src", "./chart_timewindow18.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg19").attr("src", "./chart_timewindow19.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg20").attr("src", "./chart_timewindow20.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg21").attr("src", "./chart_timewindow21.png?m=?"+new Date().getTime());
	  $("#autoTraderChartImg22").attr("src", "./chart_timewindow22.png?m=?"+new Date().getTime());
  },2000);
  */
  
  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  var forms = document.querySelectorAll('.needs-validation')

  // Loop over them and prevent submission
  Array.prototype.slice.call(forms)
    .forEach(function (form) {
      form.addEventListener('submit', function (event) {
		event.preventDefault()
		event.stopPropagation()
        if (form.checkValidity()) {
			// Send AJAX call to server
			var btn = $('input#'+this.orderExec+this.side+'Button')
			btn.attr("disabled", true);
			// Assign handlers immediately after making the request,
			// and remember the jqxhr object for this request
			var data = $( "#scaledOrdersForm" ).serialize() + '&side=' + this.side + '&orderExec=' + this.orderExec;
			var jqxhr = $.post( "postScaledOrders.php", data, function( ) {})
			  .always(function() {
				btn.attr("disabled", false);
				$('#ordersSuccess').show(0).delay(2000).hide(0);
			  });
        }

        
      }, false)
    })
	
	
	window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
	if (('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
		let speech = {
			enabled: true,
			listening: false,
			recognition: new window.SpeechRecognition(),
			text: ''
		}
		speech.recognition.continuous = true;
		speech.recognition.interimResults = true;
		speech.recognition.lang = 'en-US';
		speech.recognition.addEventListener('result', (event) => {
			const audio = event.results[event.results.length - 1];
			speech.text = audio[0].transcript;
			if (audio.isFinal) {
				try{
					var capturedText = speech.text;
					// Replace any words to numbers (if any)
					capturedText = capturedText.replace("zero", "0");
					capturedText = capturedText.replace("one", "1");
					capturedText = capturedText.replace("two", "2");
					capturedText = capturedText.replace("to", "2");
					capturedText = capturedText.replace("too", "2");
					capturedText = capturedText.replace("three", "3");
					capturedText = capturedText.replace("four", "4");
					capturedText = capturedText.replace("for", "4");
					capturedText = capturedText.replace("five", "5");
					capturedText = capturedText.replace("six", "6");
					capturedText = capturedText.replace("seven", "7");
					capturedText = capturedText.replace("eight", "8");
					capturedText = capturedText.replace("nine", "9");
					capturedText = capturedText.replace(/(\d)\s+(?=\d)/g, '$1'); // Remove spaces between digits (if any)
					capturedText = capturedText.replace(/[^0-9.]/g, ''); // Remove anything but digits and point
					var floats = capturedText.match(/[+-]?\d+(\.\d+)?/g).map(function(v) { return parseFloat(v); }); // Find the Float Numbers
					const tag = document.activeElement.nodeName;
					if (tag === 'INPUT' || tag === 'TEXTAREA')
						document.activeElement.value = floats.join('');
				}catch(e){}
				
				// Check if the command contains "Buy" or "Sell" to execute
				if(speech.text.includes('long') || speech.text.includes('by') || speech.text.includes('buy') || speech.text.includes('bye') || speech.text.includes('boy')){
					$('input#BuyButton').click();
				}
				else if(speech.text.includes('short') || speech.text.includes('sel') || speech.text.includes('cell') || speech.text.includes('sale') || speech.text.includes('sail') || speech.text.includes('send')){
					$('input#SellButton').click();
				}
			}
		});

		$('button#toggleVoice').click(function() {
			speech.listening = !speech.listening;
			if (speech.listening) {
				$(this).removeClass('btn-dark');
				$(this).addClass('btn-warning');
				$(this).addClass('listening');
				$(this).html('Listening ...');
				speech.recognition.start();
			}
			else {
				$(this).removeClass('btn-warning');
				$(this).addClass('btn-dark');
				$(this).removeClass('listening');
				$(this).html('Enable Voice Commands <i class="fa fa-microphone"></i>');
				speech.recognition.stop();
			}
		});
		
		$('#submitExecutableDrawings').click(function() {
			var executableDrawingsCount = 0;
			while(crosshairValues.length >= 2){
				var current_crosshairValue1 = crosshairValues.shift();
				var current_crosshairValue2 = crosshairValues.shift();
				var executableDrawingsData = "api_key=" + $( "input#api_key" ).val() + "&api_secret=" + $( "input#api_secret" ).val() + "&symbol=BTCUSD&type=1&x1=" + current_crosshairValue1.time +"&y1=" + current_crosshairValue1.price +"&x2=" + current_crosshairValue2.time +"&y2=" + current_crosshairValue2.price;
				var jqxhr = $.post( "postExecutableDrawings.php", executableDrawingsData, function( ) {})
				executableDrawingsCount += 1;
			}
			if (executableDrawingsCount>0)
				alert("Total applied Executable Drawings: " + executableDrawingsCount);
				executableDrawingsCount = 0;
		});
	}
	
	
    $('#exit_strategies_grid').jsGrid({

      width: "100%",
      height: "600px",

      filtering: false,
      inserting:true,
      editing: true,
      sorting: true,
      paging: true,
      autoload: true,
      pageSize: 20,
      pageButtonCount: 5,
      deleteConfirm: "Delete this Exit Strategy?",

      controller: {
      loadData: function(filter){
       return $.ajax({
		cache: false,
        type: "GET",
        url: "exit_strategies_fetch.php?command_type=GET&api_key=" + $( "input#api_key" ).val() + "&api_secret=" + $( "input#api_secret" ).val(),
        data: filter
       });
      },
      insertItem: function(item){
       $.ajax({
			tryCount : 0,
			retryLimit : 3,
			async: false,
			cache: false,
			type: "POST",
			url: "exit_strategies_fetch.php?command_type=INSERT&api_key=" + $( "input#api_key" ).val() + "&api_secret=" + $( "input#api_secret" ).val(),
			data:item,
			success : function(json) {
				return;
			},
			error : function(xhr, textStatus, errorThrown ) {
				this.tryCount++;
				if (this.tryCount <= this.retryLimit) {
					//try again
					$.ajax(this);
					return;
				}            
				return;
			}
       });
      },
      updateItem: function(item){
       $.ajax({
			tryCount : 0,
			retryLimit : 20,
			async: false,
			cache: false,
			type: "POST",
			url: "exit_strategies_fetch.php?command_type=UPDATE&api_key=" + $( "input#api_key" ).val() + "&api_secret=" + $( "input#api_secret" ).val(),
			data: item,
			success : function(json) {
				return;
			},
			error : function(xhr, textStatus, errorThrown ) {
				this.tryCount++;
				if (this.tryCount <= this.retryLimit) {
					//try again
					$.ajax(this);
					return;
				}            
				return;
			}
       });
      },
      deleteItem: function(item){
       $.ajax({
			tryCount : 0,
			retryLimit : 20,
			async: false,
			cache: false,
			type: "POST",
			url: "exit_strategies_fetch.php?command_type=DELETE&api_key=" + $( "input#api_key" ).val() + "&api_secret=" + $( "input#api_secret" ).val(),
			data: item,
			success : function(json) {
				return;
			},
			error : function(xhr, textStatus, errorThrown ) {
				this.tryCount++;
				if (this.tryCount <= this.retryLimit) {
					//try again
					$.ajax(this);
					return;
				}            
				return;
			}
       });
      },
      },

      fields: [
        {
          name: "id",
          type: "hidden",
          css: 'hide'
        },
		
        {
          name: "symbol", 
		  title: "Symbol (Instrument)",
          type: "text", 
          width: 100, 
		  editing: false,     
		  sorting: true,
		  sorter: "string",		  
		  validate: {
			validator: function(value, item) {
			  var gridData = $("#exit_strategies_grid").jsGrid("option", "data");
			 
			  for (let i = 0; i < gridData.length; i++) {                                		 
				  if(value == gridData[i].symbol || value == ''){
					  return false;
				  }
			  }
			  return true;
			},
            message: function(value, item) {
                return "Exit Strategy exists for this Symbol or you forgot to type the Symbol!";
            }
		  }
        },
		
        {
          name: "tp_type", 
		  title: "TP Order Type",
          type: "select", 
		  width: 80, 
          items: [
                  { Name: "Limit", Id: 'limitorder' },
				  { Name: "Limit (PostOnly)", Id: 'limitorder_postonly' },
                  { Name: "Market", Id: 'marketorder' }
          ], 
          valueField: "Id", 
          textField: "Name", 
          validate: "required"
        },
		
        {
          name: "tp_target_long", 
		  title: "TP Target Long Values",
          type: "text",
        },
		
        {
          name: "tp_target_short", 
		  title: "TP Target Short Values",
          type: "text",
        },
		
        {
          name: "tp_target_type", 
		  title: "TP Target Type",
          type: "select", 
          items: [
                  { Name: "% Pre-Leverage", Id: 'ratio_pre_leverage' },
                  { Name: "% Post-Leverage", Id: 'ratio_post_leverage' }
          ], 
          valueField: "Id", 
          textField: "Name", 
          validate: "required"
        },
		
        {
          name: "tp_all_or_none", 
		  title: "Add TPs All or None",
          type: "checkbox", 
		  width: 80, 
          validate: "required"
        },
		
        {
          name: "tp_enforce_all_time", 
		  title: "TPs Enforce All Time",
          type: "checkbox", 
		  width: 80, 
          validate: "required"
        },
		
        {
          name: "tp_enforce_maxrange", 
		  title: "TPs Enforce Max Range",
          type: "checkbox", 
		  width: 80, 
          validate: "required"
        },
		
        {
          name: "sl_target_long", 
		  title: "SL Target Long Value",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "sl_target_short", 
		  title: "SL Target Short Value",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "sl_trailing_targets_long", 
		  title: "SL Trailing Target Long Values",
          type: "text",
        },
		
        {
          name: "sl_trailing_targets_short", 
		  title: "SL Trailing Target Short Values",
          type: "text",
        },
		
        {
          name: "sl_target_type", 
		  title: "SL Target Type",
          type: "select", 
          items: [
                  { Name: "% Pre-Leverage", Id: 'ratio_pre_leverage' },
                  { Name: "% Post-Leverage", Id: 'ratio_post_leverage' }
          ], 
          valueField: "Id", 
          textField: "Name", 
          validate: "required"
        },
		
        {
          name: "tb_initial_sl_static_cap_ratio_buy_override", 
		  title: "TB SL Initial Wallet % Long",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "tb_initial_sl_static_pos_size_ratio_buy_override",
		  title: "TB SL Initial Position % Long",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "tb_sl_static_cap_ratio_buy_override", 
		  title: "TB SL Wallet % Long",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "tb_sl_static_pos_size_ratio_buy_override",
		  title: "TB SL Position % Long",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "tb_initial_sl_static_cap_ratio_sell_override", 
		  title: "TB SL Initial Wallet % Short",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "tb_initial_sl_static_pos_size_ratio_sell_override",
		  title: "TB SL Initial Position % Short",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "tb_sl_static_cap_ratio_sell_override", 
		  title: "TB SL Wallet % Short",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "tb_sl_static_pos_size_ratio_sell_override",
		  title: "TB SL Position % Short",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "tb_hedge_cap_ratio_buy_override", 
		  title: "TB Hedge Wallet % Long",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "tb_hedge_pos_size_ratio_buy_override",
		  title: "TB Hedge Position % Long",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "tb_hedge_cap_ratio_sell_override", 
		  title: "TB Hedge Wallet % Short",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "tb_hedge_pos_size_ratio_sell_override",
		  title: "TB Hedge Position % Short",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "tb_hedge_balancer_cap_ratio_override", 
		  title: "TB Hedge Balancer Wallet %",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "tb_hedge_sl_static_cap_ratio_override",
		  title: "TB Hedge SL Wallet %",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          name: "tp_after_hedge", 
		  title: "Place TPs after Hedge",
          type: "checkbox", 
		  width: 80, 
          validate: "required"
        },
		
        {
          name: "sl_after_hedge", 
		  title: "Place SLs after Hedge",
          type: "checkbox", 
		  width: 80, 
          validate: "required"
        },
		
        {
          name: "reset_refresh_rate", 
		  title: "Reset TPs/SLs Refresh Rate (minutes)",
          type: "text", 
          width: 100, 
          validate: function(value)
          {
            if(value >= 0)
            {
              return true;
            }
          }
        },
		
        {
          type: "control"
        }
      ]

    });
	
	
});
</script>
<!-- TradingView Charting Library -->
<!-- <script type="module" src="src/main.js"></script> -->
</body>
</html>
